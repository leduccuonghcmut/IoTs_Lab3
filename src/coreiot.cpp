#include "coreiot.h"

void coreiot_task(void *pvParameters)
{
  AppContext *ctx = static_cast<AppContext *>(pvParameters);
  WiFiClient espClient;
  PubSubClient client(espClient);

  client.setServer("10.12.141.24", 1883); 

  while (1)
  {
    if (!client.connected()) 
    {
      Serial.println("[MQTT] Đang kết nối tới Broker...");
      if (client.connect("ESP32_Node_1")) 
      {
         Serial.println("[MQTT] Kết nối thành công!");
      }
      else
      {
         Serial.print("[MQTT] Lỗi kết nối, mã lỗi: ");
         Serial.println(client.state());
      }
    }

    if (ctx != NULL && ctx->stateMutex != NULL && xSemaphoreTake(ctx->stateMutex, portMAX_DELAY) == pdTRUE)
    {
      float temperature = ctx->temperature;
      float humidity = ctx->humidity;
      xSemaphoreGive(ctx->stateMutex);

      if (client.connected())
      {
        String payload = "{\"temperature\":" + String(temperature) + ",\"humidity\":" + String(humidity) + "}";
        
        client.publish("sensor/dht20", payload.c_str());
        
        Serial.println("[MQTT] Đã đẩy dữ liệu: " + payload);
      }
    }

    client.loop();
    vTaskDelay(pdMS_TO_TICKS(10000)); 
  }
}