import dummy_dvde_api as dvde
import json
import time
import sys

connection = None
channel = None

# Data enqueing
print(' [*] Sending data. Press CTRL+C to exit')

for i in range(0,6):

    matrix =[[15.3181128601480, 48.0759783968909, 2], 
            [14.2949817462715, 47.9871977358879, 2],
            [16.4380855350346, 42.0386448286094, 1],
            [12.2903853701921, 47.9291209919643, 2],
            [14.4579005366844, 41.9894100214277, 1],
            [10.2903642978411, 47.8659036790991, 2],
            [8.49189149682204, 41.8037451937836, 1],
            [6.49447171658257, 41.7389113024907, 1],
            [8.29483356036796, 47.8005083348189, 2],
            [12.4735170408320, 41.9319164105607, 1],
            [10.4848751821667, 41.8690573815958, 1],
            [16.3042155724446, 48.0371512121282, 2]]
    
    message = json.dumps(matrix)

    connection = None
    while connection == None:

        try:
            connection, channel = dvde.produce("computer_vision", message, connection = connection, channel = channel)
        except (dvde.pika.exceptions.AMQPConnectionError, RuntimeError) as err: 
            
            # Want to keep trying in case of errors
            print("Connection failed. Probably RabbitMQ is still starting up, sleeping for 4s..")
            
            # Needed to make it print in real time for some reason
            sys.stdout.flush()

            connection = None
            time.sleep(4)
    
    print("Produce riuscito.")
    sys.stdout.flush()

channel.close()
connection.close()