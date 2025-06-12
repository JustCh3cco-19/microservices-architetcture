import json
import sys
import dummy_dvde_api as dvde
import time
import math
import numpy as np

connection_consume = None
channel_consume = None

established_connection_produce = None
established_channel_produce = None

print("High level control service started.")

# Cache the last received values
dati_slam_odometria_correnti = None
dati_path_planning_correnti = None

# Output fake values that oscillate between -60 and 60 degrees
output_values_periodic = 60 * np.sin(np.deg2rad(np.arange(0, 359, 15)))
num_output_values = len(output_values_periodic)

t = 0

while(1):

    print("Sleeping 4 seconds to wait for new data..")
    time.sleep(4)

    dati_slam_odometria_ricevuti = []
    dati_path_planning_ricevuti = []

    # dvde.consume handles all exceptions internally, no need for try-except
    connection_consume, channel_consume = dvde.consume("slam-odometry", dati_slam_odometria_ricevuti, connection = connection_consume, channel = channel_consume)
    connection_consume, channel_consume = dvde.consume("path_planning", dati_path_planning_ricevuti, connection = connection_consume, channel = channel_consume)

    # Check if there are any new data
    new_data = False

    if dati_slam_odometria_ricevuti[0] is not None:
        new_data = True
        dati_slam_odometria_decodificati = [ dato_slam_o.decode('utf-8') for dato_slam_o in dati_slam_odometria_ricevuti ]
        dati_slam_odometria_correnti = [ json.loads(dato_slam_o_decodificato) for dato_slam_o_decodificato in dati_slam_odometria_decodificati ]

    if dati_path_planning_ricevuti[0] is not None:
        new_data = True
        dati_path_planning_decodificati = [ dato_pp.decode('utf-8') for dato_pp in dati_path_planning_ricevuti ]
        dati_path_planning_correnti = [ json.loads(dato_pp_decodificato) for dato_pp_decodificato in dati_path_planning_decodificati ]

    if new_data and dati_slam_odometria_correnti is not None and dati_path_planning_correnti is not None:

        # Use the most recent data
        latest_slam = dati_slam_odometria_correnti[-1]
        latest_pp = dati_path_planning_correnti[-1]

        # SLAM
        x_dot = latest_slam["x_vel"]
        y_dot = latest_slam["y_vel"]
        psi_rate = latest_slam["psi"]

        # PP
        # curvature = latest_pp["curvature"]
        # angle_error = latest_pp["angle_error"]
        wpx = latest_pp["x"]
        wpy = latest_pp["y"]
        
        print("Data received.")
        # Stampa dei vettori
        print("x_dot:", x_dot)
        print("y_dot:", y_dot)
        print("psi_rate:", psi_rate)
        # print("curvature:", curvature)
        # print("angle_error:", angle_error)
        print("wpx:", wpx[:5])
        print("wpy:", wpy[:5])

        # Should try to correct the curvature to make the car go straight, or something
        # A completely fictitious computation of course
        #steer_angle = - (curvature / 2)

        # A periodic sinusoidal function between -60 and 60
        # Just to output something
        steer_angle = output_values_periodic[ (t) % num_output_values ]
        t = t + 1

        # Tries to make the car accelerate to a constant 5 m/s, or something like that
        speed = math.sqrt(x_dot**2 + y_dot**2)
        long_acc = (5 - speed)

        output = {
            "steer_angle": steer_angle,
            "long_acc": long_acc
        }
    
        print("Output data generated.")
        print(output)

        message = json.dumps(output)

        connection_produce = None
        while connection_produce == None:

            connection_produce = established_connection_produce
            channel_produce = established_channel_produce

            try:
                connection_produce, channel_produce = dvde.produce("hlc_output", message, connection = connection_produce, channel = channel_produce)
            except (dvde.pika.exceptions.AMQPConnectionError, RuntimeError) as err: 
                
                # Want to keep trying in case of errors
                print("Connection failed. Probably RabbitMQ is still starting up, sleeping for 4s..")
                
                # Needed to make it print in real time for some reason
                sys.stdout.flush()

                established_connection_produce = None
                established_channel_produce = None
                # This is here just to ensure that the while loop repeats in case of error
                connection_produce = None

                time.sleep(4)
            
        established_connection_produce = connection_produce
        established_channel_produce = channel_produce
        
        print("Produce succeeded.")
        sys.stdout.flush()