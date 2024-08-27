import base64
from typing import Callable, List, Optional

import json
import requests
import datetime
import paho.mqtt.client as mqtt

from fms_robot_plugin.typings import (
    ConnectionStatus,
    StartCameraCommand,
    Status,
    LaserScan,
    Twist,
    Pose,
    Map,
    RobotInfo,
    Task,
    DecimatedPlan,
    Result,
    AcquireLockRequest,
    AcquireLockResponse,
    ReleaseLockRequest,
    ReleaseLockResponse,
    RetryAcquireLockCommand,
    ReconnectBehavior,
)
from fms_robot_plugin.mqtt import MqttClient, MqttConsumer


class Robot:
    robot_key: Optional[str]

    def __init__(
        self,
        plugin_name: str,
        plugin_version: str,
        robot_key: str,
        broker_host: str = "broker.movelrobotics.com",
        broker_port: int = 1883,
        broker_use_tls: bool = False,
        broker_ca_certs: Optional[str] = None,
        api_hostname: str = "api.movelrobotics.com",
        capabilities: List[str] = [],
    ):
        self.plugin_name = plugin_name
        self.plugin_version = plugin_version
        self.capabilities = capabilities
        self.robot_key = robot_key
        self.priority: int = 0
        self.reconnect_behavior: ReconnectBehavior = ReconnectBehavior.CANCEL_QUEUE

        self.acquire_lock_message_id: Optional[str] = None
        self.release_lock_message_id: Optional[str] = None
        self.traffic_task: Optional[Task] = None
        self.node_ids: List[str] = []

        self.api_hostname = api_hostname
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.broker_use_tls = broker_use_tls
        self.broker_ca_certs = broker_ca_certs
        # custom mqtt client connection
        self.mqtt = MqttClient(
            broker_host,
            broker_port,
            broker_use_tls,
            broker_ca_certs,
        )
        # default callback mqtt client
        self.callback_clients: List[mqtt.Client] = []

        # main mqtt connection status
        self.client = mqtt.Client()
        self.on_connect: Callable[[dict], None] = lambda payload: None
        self.on_disconnect: Callable[[dict], None] = lambda payload: None
        self.on_reconnect: Callable[[], None] = lambda: None

    def run(self):
        self.register_default_callbacks()
        self.establish_connection()

    def stop(self):
        self.terminate_connection()
        self.unregister_default_callbacks()

    def unregister_default_callbacks(self):
        for client in self.callback_clients:
            client.disconnect()
            client.loop_stop()

    def terminate_connection(self):
        self.client.disconnect()

    """
    Command Callbacks

    These methods are called when a command is published from the FMS server.
    """

    def on_teleop(self, cb: Callable[[Twist], None]):
        topic = f"robots/{self.robot_key}/teleop"
        return self.consumer(topic).consume(lambda data: cb(Twist(**data)))

    def on_stop(self, cb: Callable[[], None]):
        topic = f"robots/{self.robot_key}/stop"
        return self.consumer(topic).consume(lambda _: cb(), serialize=False)

    def on_start_mapping(self, cb: Callable[[str], None]):
        topic = f"robots/{self.robot_key}/mapping/start"
        return self.consumer(topic).consume(lambda map_id: cb(map_id), serialize=False)

    def on_save_mapping(self, cb: Callable[[], None]):
        topic = f"robots/{self.robot_key}/mapping/save"
        return self.consumer(topic).consume(lambda _: cb(), serialize=False)

    def on_localize(self, cb: Callable[[str, Pose], None]):
        topic = f"robots/{self.robot_key}/localize"
        return self.consumer(topic).consume(lambda data: cb(data["map_id"], Pose(**data["initial_pose"])))

    def on_load_navigation_map_pgm(self, cb: Callable[[bytes, str, Optional[Pose], bool], None]):
        topic = f"robots/{self.robot_key}/maps/:map_id/load/navigation_pgm"
        return self.consumer(topic).consume(
            lambda data, url_params: cb(
                base64.b64decode(data["file"]),
                url_params["map_id"],
                Pose(**data["initial_pose"]) if data.get("initial_pose") else None,
                data.get("publish_result", False),
            )
        )

    def on_load_navigation_map_yaml(self, cb: Callable[[bytes, str, Optional[Pose], bool], None]):
        topic = f"robots/{self.robot_key}/maps/:map_id/load/navigation_yaml"
        return self.consumer(topic).consume(
            lambda data, url_params: cb(
                base64.b64decode(data["file"]),
                url_params["map_id"],
                Pose(**data["initial_pose"]) if data.get("initial_pose") else None,
                data.get("publish_result", False),
            )
        )

    def on_load_localization_map_pgm(self, cb: Callable[[bytes, str, Optional[Pose], bool], None]):
        topic = f"robots/{self.robot_key}/maps/:map_id/load/localization_pgm"
        return self.consumer(topic).consume(
            lambda data, url_params: cb(
                base64.b64decode(data["file"]),
                url_params["map_id"],
                Pose(**data["initial_pose"]) if data.get("initial_pose") else None,
                data.get("publish_result", False),
            )
        )

    def on_load_localization_map_yaml(self, cb: Callable[[bytes, str, Optional[Pose], bool], None]):
        topic = f"robots/{self.robot_key}/maps/:map_id/load/localization_yaml"
        return self.consumer(topic).consume(
            lambda data, url_params: cb(
                base64.b64decode(data["file"]),
                url_params["map_id"],
                Pose(**data["initial_pose"]) if data.get("initial_pose") else None,
                data.get("publish_result", False),
            )
        )

    def on_unload_map(self, cb: Callable[[], None]):
        topic = f"robots/{self.robot_key}/maps/unload"
        return self.consumer(topic).consume(lambda _: cb(), serialize=False)

    def on_execute_task(self, cb: Callable[[Task], None]):
        topic = f"robots/{self.robot_key}/tasks/execute"
        return self.consumer(topic).consume(lambda data: cb(Task(**data)))

    def on_resume_task(self, cb: Callable[[], None]):
        topic = f"robots/{self.robot_key}/tasks/resume"
        return self.consumer(topic).consume(lambda _: cb(), serialize=False)

    def on_pause_task(self, cb: Callable[[], None]):
        topic = f"robots/{self.robot_key}/tasks/pause"
        return self.consumer(topic).consume(lambda _: cb(), serialize=False)

    def on_set_priority(self, cb: Callable[[int], None]):
        topic = f"robots/{self.robot_key}/priority"
        return self.consumer(topic).consume(lambda priority: cb(int(priority.decode("utf-8"))), serialize=False)

    def on_robot_info(self, cb: Callable[[RobotInfo], None]):
        topic = f"robots/{self.robot_key}/info/receive"
        return self.consumer(topic).consume(lambda data: cb(RobotInfo(**data)))

    def on_preview_map(self, cb: Callable[[], None]):
        topic = f"robots/{self.robot_key}/mapping/import"
        return self.consumer(topic).consume(lambda _: cb(), serialize=False)

    def on_acquire_lock_response(self, cb: Callable[[AcquireLockResponse], None]):
        topic = f"robots/{self.robot_key}/locks/acquire/response"
        return self.consumer(topic, 2).consume(lambda data: cb(AcquireLockResponse(**data)))

    def on_release_lock_response(self, cb: Callable[[ReleaseLockResponse], None]):
        topic = f"robots/{self.robot_key}/locks/release/response"
        return self.consumer(topic, 2).consume(lambda data: cb(ReleaseLockResponse(**data)))

    def on_retry_acquire_lock(self, cb: Callable[[RetryAcquireLockCommand], None]):
        topic = f"robots/{self.robot_key}/locks/retry-acquire"
        return self.consumer(topic).consume(lambda data: cb(RetryAcquireLockCommand(**data)))

    def on_start_camera_feed(self, cb: Callable[[StartCameraCommand], None]):
        # TODO: camera fix serialize True and use map_id and rostopic payload
        topic = f"robots/{self.robot_key}/camera/start"
        return self.consumer(topic).consume(lambda data: cb(StartCameraCommand(**data)))

    def on_set_reconnect_behavior(self, cb: Callable[[ReconnectBehavior], None]):
        topic = f"robots/{self.robot_key}/reconnect_behavior"
        return self.consumer(topic).consume(
            lambda data: cb(ReconnectBehavior(str(data.decode("utf-8")))), serialize=False
        )

    """
    Publishers

    These methods are called to publish data to the FMS server.
    """

    def set_camera_feed(self, data: str):
        self.mqtt.publish(f"robots/{self.robot_key}/camera", data, serialize=False)

    def set_lidar(self, data: LaserScan):
        self.mqtt.publish(f"robots/{self.robot_key}/lidar", data.dict())

    def set_pose(self, data: Pose):
        self.mqtt.publish(f"robots/{self.robot_key}/pose", data.dict())

    def set_map_data(self, data: Map):
        self.mqtt.publish(f"robots/{self.robot_key}/mapping/data", data.dict())

    def set_status(self, data: Status):
        self.mqtt.publish(f"robots/{self.robot_key}/status", data, serialize=False)

    def set_battery_percentage(self, data: float):
        self.mqtt.publish(f"robots/{self.robot_key}/battery", data, serialize=False)

    def set_map_result(self, pgm: bytes, yaml: bytes):
        url = f"{self.api_hostname}/api/robots/{self.robot_key}/mapping/result"
        files = [
            ("files", ("mapping_result.pgm", pgm)),
            ("files", ("mapping_result.yaml", yaml)),
        ]

        return requests.post(url=url, files=files)

    def check_map_existance(self, filenames: List[str]):
        url = f"{self.api_hostname}/api/robots/{self.robot_key}/check-map"
        data = {
            "filenames": filenames,
        }

        response = requests.post(url, json=data)
        return response

    def set_map_preview_result(self, name: str, pgm: bytes, yaml: bytes):
        url = f"{self.api_hostname}/api/robots/{self.robot_key}/mapping/preview/result"
        files = [
            ("files", pgm),
            ("files", yaml),
        ]
        data = {
            "name": name,
        }
        response = requests.post(url, data=data, files=files)
        return response

    def set_cpu_usage(self, data: float):
        self.mqtt.publish(f"robots/{self.robot_key}/monitor/cpu", data, serialize=False)

    def set_memory_usage(self, data: float):
        self.mqtt.publish(f"robots/{self.robot_key}/monitor/memory", data, serialize=False)

    def set_battery_usage(self, data: float):
        self.mqtt.publish(f"robots/{self.robot_key}/monitor/battery", data, serialize=False)

    def set_robot_info(self, data: RobotInfo):
        self.mqtt.publish(f"robots/{self.robot_key}/info/reply", data.dict())

    def set_decimated_plan(self, data: DecimatedPlan):
        self.mqtt.publish(f"robots/{self.robot_key}/decimated-plan", data.dict())

    def set_result(self, data: Result):
        self.mqtt.publish(f"robots/{self.robot_key}/result", data.dict())

    def set_obstacle_notification(self, data: bool):
        self.mqtt.publish(f"robots/{self.robot_key}/obstacle", data, serialize=False)

    def set_notification_message(self, data: str):
        self.mqtt.publish(f"robots/{self.robot_key}/notification", data, serialize=False)

    def set_acquire_lock_request(self, data: AcquireLockRequest):
        self.acquire_lock_message_id = data.message_id
        self.mqtt.publish(f"robots/{self.robot_key}/locks/acquire/request", data.dict(), qos=2)

    def set_release_lock_request(self, data: ReleaseLockRequest):
        self.release_lock_message_id = data.message_id
        self.mqtt.publish(f"robots/{self.robot_key}/locks/release/request", data.dict(), qos=2)

    def set_map_id(self, map_id: str):
        self.mqtt.publish(f"robots/{self.robot_key}/maps/{map_id}/set", data=None)

    """
    Utilities
    """

    def consumer(self, topic: str, qos: int = 0):
        return MqttConsumer(
            topic,
            qos,
            self.broker_host,
            self.broker_port,
            self.broker_use_tls,
            self.broker_ca_certs,
        )

    def register_default_callbacks(self):
        self.callback_clients.append(self.on_set_priority(self.set_priority))
        self.callback_clients.append(self.on_set_reconnect_behavior(self.set_reconnect_behavior))

    def set_priority(self, priority: int):
        self.priority = priority

    def set_reconnect_behavior(self, behavior: ReconnectBehavior):
        self.reconnect_behavior = behavior

    def establish_connection(self):
        connection_topic = f"robots/{self.robot_key}/connection"

        def _on_connect(client, userdata, flags, rc):
            self.client.publish(
                connection_topic,
                payload=json.dumps(
                    {
                        "status": ConnectionStatus.Connected.value,
                        "sent_at": datetime.datetime.utcnow().isoformat(),
                        "name": self.plugin_name,
                        "version": self.plugin_version,
                        "capabilities": self.capabilities,
                    }
                ),
            )

            payload = {"sent_at": datetime.datetime.now().isoformat()}
            self.on_connect(payload)

        def _on_disconnect(client, userdata, rc):
            payload = {"sent_at": datetime.datetime.now().isoformat()}
            self.on_disconnect(payload)

            # forced disconnect
            if rc != mqtt.MQTT_ERR_SUCCESS:
                self.on_reconnect()

        self.client.on_connect = _on_connect
        self.client.on_disconnect = _on_disconnect
        self.client.will_set(
            connection_topic,
            payload=json.dumps(
                {
                    "status": ConnectionStatus.Disconnected.value,
                    "sent_at": datetime.datetime.utcnow().isoformat(),
                }
            ),
            qos=0,
            retain=True,
        )

        if self.broker_use_tls:
            self.client.tls_set(self.broker_ca_certs)

        self.client.connect(self.broker_host, self.broker_port)
        self.client.loop_forever()
