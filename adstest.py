import socket
import numpy as np

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
            j=0
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
                    np_array = np.frombuffer(packet, dtype=np.uint32).reshape((ROWS, COLS))
                    all_data.append(np_array)
                    
                    print("rvc ",j)
                    j += 1

            # Combine all arrays into a single large array
            if all_data:
                big_array = np.vstack(all_data)
                print("Received data shape:", big_array.shape)
                
                # Save the large NumPy array to a file
                #np.save('received_data.npy', big_array)
                #print("Data saved to received_data.npy")
            
            return big_array

if __name__ == '__main__':
    received = receive_data()
    print(np.array(received).shape)

