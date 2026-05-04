import paho.mqtt.client as mqtt
import json
import time

THINGSBOARD_HOST = 'app.coreiot.io'
THINGSBOARD_PORT = 1883
ACCESS_TOKEN = 'wmFKwhhrR95rzx9xBi6j'  # Gateway token

LOCAL_BROKER = '127.0.0.1'
LOCAL_TOPIC = 'sensor/dht20'


# Create MQTT client
def get_mqtt_client(client_id):
    try:
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)
    except AttributeError:
        return mqtt.Client(client_id)


# Cloud callbacks
def on_cloud_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[CLOUD] Connected to ThingsBoard")
    else:
        print(f"[CLOUD] Connection failed, rc={rc}")


def on_cloud_publish(client, userdata, mid):
    print(f"[CLOUD] Message published (MID: {mid})")


# Local callbacks
def on_local_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[LOCAL] Connected to local broker")
        client.subscribe(LOCAL_TOPIC)
    else:
        print(f"[LOCAL] Connection failed, rc={rc}")


def on_local_message(client, userdata, msg):
    try:
        # Receive sensor data from ESP32
        payload_str = msg.payload.decode("utf-8")
        data = json.loads(payload_str)

        # Format for gateway telemetry
        telemetry = {
            "ESP32_Device": [
                {
                    "ts": int(time.time() * 1000),
                    "values": {
                        "temperature": data.get("temperature"),
                        "humidity": data.get("humidity")
                    }
                }
            ]
        }

        # Send to cloud
        cloud_payload = json.dumps(telemetry)
        cloud_client.publish('v1/gateway/telemetry', cloud_payload)

        print(f"[BRIDGE] Forwarded data: {cloud_payload}")

    except Exception as e:
        print(f"[ERROR] {e}")


# Setup cloud client
cloud_client = get_mqtt_client("CloudGateway")
cloud_client.username_pw_set(ACCESS_TOKEN)
cloud_client.on_connect = on_cloud_connect
cloud_client.on_publish = on_cloud_publish

cloud_client.connect(THINGSBOARD_HOST, THINGSBOARD_PORT, 60)
cloud_client.loop_start()


# Setup local client
local_client = get_mqtt_client("LocalSubscriber")
local_client.on_connect = on_local_connect
local_client.on_message = on_local_message

local_client.connect(LOCAL_BROKER, 1883, 60)


# Main loop
try:
    local_client.loop_forever()

except KeyboardInterrupt:
    print("Interrupted")

finally:
    cloud_client.loop_stop()
    cloud_client.disconnect()
    local_client.disconnect()