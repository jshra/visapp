# data_gathering.py

import socket
import numpy as np
import tensorflow as tf
import threading
from collections import deque
import paramiko

DENOMINATOR = 2147483647.0
REF = 5.08
PORT = 12345
ROWS = 200
COLS = 5


def data_reading_and_inference():
    print('started function')
    sentOPEN = False
    sentCLOS = False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 12346)) 

        server_socket.bind(('0.0.0.0', PORT))
        server_socket.listen()
        print("Waiting for connection...")
        stdin, stdout, stderr = ssh.exec_command('sudo ./Desktop/spi_example')
        conn, addr = server_socket.accept()
        print('Started data gathering process on raspberry')
        with conn:
            print(f"Connected by {addr}")
            
            while True:
                # Receive data chunk by chunk
                data_chunk = b''
                while len(data_chunk) < ROWS * COLS * 4:
                    chunk = conn.recv(ROWS * COLS * 4 - len(data_chunk))
                    if not chunk:
                        break
                    data_chunk += chunk
                
                if not data_chunk:
                    break  # End of data stream
                


                # Convert the received chunk to a NumPy array
                num_packets = len(data_chunk) // (ROWS * COLS * 4)
                for i in range(num_packets):
                    start_index = i * ROWS * COLS * 4
                    end_index = start_index + ROWS * COLS * 4
                    packet = data_chunk[start_index:end_index]
                    np_array = np.frombuffer(packet, dtype=np.uint32).reshape((ROWS, COLS))/DENOMINATOR * REF
                    inference_result = model(np_array[:,1:].reshape(1,200,4)).numpy()

                    last_4_results.append(inference_result)
                    # Calculate the average of the last 4 results
                    if len(last_4_results) == 4:
                        average_result = np.mean(last_4_results)
                        if average_result > 0.75 and sentOPEN == False:
                            client_socket.sendall(f"{int(True)},{int(False)}".encode())
                            sentOPEN = True
                            sentCLOS = False
                            # print("sent OPEN")

                        elif average_result < 0.25 and sentCLOS == False:
                            client_socket.sendall(f"{int(False)},{int(True)}".encode())
                            sentOPEN = False
                            sentCLOS = True
                            # print("sent CLOSE")

                        else:
                            client_socket.sendall(f"{int(False)},{int(False)}".encode())
                            # print("sent NONE")
# Ensure that last_4_results list maintains only the last 4 entries
                        if len(last_4_results) > 4:
                            last_4_results.pop(0)



if __name__ == "__main__":
    try:
        print('starting')
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('192.168.1.100', username='rasp', password='maslo')
        print('ssh to raspberry estabilished')
        model = tf.keras.models.load_model('model')
        print('loaded the model')
        last_4_results = deque(maxlen=4)
        data_reading_and_inference()
    except:
        ssh.exec_command('pkill spi_example')
        print('Stopped data gathering process on raspberry')
        ssh.close()
