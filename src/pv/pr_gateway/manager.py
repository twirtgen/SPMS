from threading import Thread

from cryptography.hazmat.primitives import serialization
import paho.mqtt.client as mqtt
import requests
import ssl

from pv.pr_gateway.config import CONFIG as config

# Subscribe to default topic
TOPICS = [('/all', 2)]

# Add additional topics (protocols, verifiers, properties) from config
TOPICS += config['TOPICS']

def fetch_binding(plugin):
    r = requests.get('https://%s/binding/%s' % (config['PR_ADDR'], plugin), cert=(config['CERT_FILE'], '/dev/shm/pv.key'), verify=config['CA_FILE'])
    if r.status_code != 200:
        # TODO : handle error
        return

    binding = r.content
    
    r = requests.post('http://%s/binding/%s' % (config['BM_ADDR'], plugin), data=binding)
    if r.status_code != 200:
        # TODO : handle error
        pass

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Register PV to expected topics
    client.subscribe(TOPICS)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    # TODO : check payload
    plugin = msg.payload.decode('ascii')

    # FIXME : DDoS possibility
    # Maybe use a locked queue and a consumer process
    callback = Thread(target=fetch_binding, args=(plugin,))
    callback.start()
    
def setup():
    client = mqtt.Client()

    # Define MQTT client callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    # Configure SSL context for MQTTs traffic
    context = ssl.SSLContext()
    context.load_cert_chain(certfile=config['CERT_FILE'], keyfile='/dev/shm/pv.key')
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations(config['CA_FILE'])
    client.tls_set_context(context)
    client.tls_insecure_set(False)

    # Connect to PR
    client.connect(config['PR_ADDR'], 8883)

    # Wait for notifications
    client.loop_forever()

loop = Thread(target=setup)
loop.start()

