import socket
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

DENOMINATOR = 2147483647.0
REF = 5.08
PORT = 12345
ROWS = 200
COLS = 5

def receive_data():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('0.0.0.0', PORT))
        server_socket.listen()
        print("waiting")
        
        conn, addr = server_socket.accept()
        with conn:
            print(f"connected by {addr}")
            
            # Initialize an empty list to store received data
            all_data = []
            
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
                    if model(np_array[:,1:].reshape(1,200,4)).numpy() > 0.5:
                        print('hand open')
                    else :
                        print('hand closed')


if __name__ == '__main__':
    model = tf.keras.models.load_model('model')
    print('model loaded')
    receive_data()