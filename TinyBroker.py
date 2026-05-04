from amqtt.broker import Broker
import asyncio
import logging
logging.basicConfig(level=logging.DEBUG)

broker_config = {
    'listeners': {
        'default': {
            'type': 'tcp',
            'bind': '0.0.0.0:1883'  
        }
    },
    'sys_interval': 10,
    'auth': {
        'allow-anonymous': True  
    },
    'topic-check': {
        'enabled': True,
        'plugins': ['topic_taboo'] 
    }
}

async def start_broker():
    broker = Broker(broker_config)
    await broker.start()
    print("MQTT Broker started...")


loop = asyncio.get_event_loop()
loop.run_until_complete(start_broker())
loop.run_forever()