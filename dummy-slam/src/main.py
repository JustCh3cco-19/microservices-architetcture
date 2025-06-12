import json
import sys
import dummy_dvde_api as dvde
import time
import numpy as np

connection_consume = None
channel_consume = None

connection_produce = None
channel_produce = None

def send_data(data, queue_name, established_connection, established_channel):

    connection = None
    while connection == None:

        connection = established_connection
        channel = established_channel

        try:
            connection, channel = dvde.produce(queue_name, data, connection = connection, channel = channel)
        except (dvde.pika.exceptions.AMQPConnectionError, RuntimeError) as err: 
            
            # Want to keep trying in case of errors
            print("Connection failed. Probably RabbitMQ is still starting up, sleeping for 4s..")
            
            # Needed to make it print in real time for some reason
            sys.stdout.flush()

            established_connection = None
            established_channel = None
            # This is here just to ensure that the while loop repeats in case of error
            connection = None

            time.sleep(4)
        
    return connection, channel

# Output fake values that oscillate between 2.5m/s and 7.5m/s
output_values_periodic = 2.5 * np.sin(np.deg2rad(np.arange(0, 359, 15))) + 5
num_output_values = len(output_values_periodic)

print("SLAM service started.")

t = 0

while(1):

    print("Sleeping 4 seconds to wait for new data..")
    time.sleep(4)

    dati_ricevuti = []

    # dvde.consume handles all exceptions internally, no need for try-except
    connection_consume, channel_consume = dvde.consume("computer_vision", dati_ricevuti, connection = connection_consume, channel = channel_consume)

    if dati_ricevuti[0] is None:
        print('No new data received.')
        continue

    for i,stringa_matriceInput in enumerate(dati_ricevuti):

        stringa_matriceInput_decodificata = stringa_matriceInput.decode('utf-8')
        matriceInput = json.loads(stringa_matriceInput_decodificata)

        # inizializzazione dei vettori
        xConi = []
        yConi = []
        coloreConi = []

        # estrazione dei vettori
        for riga in matriceInput:
            xConi.append(riga[0])
            yConi.append(riga[1])
            coloreConi.append(riga[2])

        xConi = np.array(xConi)
        yConi = np.array(yConi) 
        coloreConi = np.array(coloreConi)

        print("Data received.")
        # stampa dei vettori
        print("x array:", xConi)
        print("y array:", yConi)
        print("Colors array:", coloreConi)
    
        # Forwards the input unchanged
        message_cones = stringa_matriceInput_decodificata

        connection_produce, channel_produce = send_data(message_cones, 'slam-cones', connection_produce, channel_produce)

        print("Cones forwarded to PP.")

        odometry_data = {
            "x_pos": output_values_periodic[ (t) % num_output_values],
            "y_pos": output_values_periodic[ (t + 1) % num_output_values],
            "x_vel": output_values_periodic[ (t + 2) % num_output_values],
            "y_vel": output_values_periodic[ (t + 3) % num_output_values],
            "x_acc": output_values_periodic[ (t + 4) % num_output_values],
            "y_acc": output_values_periodic[ (t + 5) % num_output_values],
            "psi": output_values_periodic[ (t + 6) % num_output_values],
            "x_velang": output_values_periodic[ (t + 7) % num_output_values],
            "y_velang": output_values_periodic[ (t + 8) % num_output_values]
        }

        print("Output data generated.")
        print(odometry_data)

        message_odometry = json.dumps(odometry_data)

        connection_produce, channel_produce = send_data(message_odometry, 'slam-odometry', connection_produce, channel_produce)

        t = t + 1
        
        print("Produce succeeded.")
        sys.stdout.flush()