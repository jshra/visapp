import threading
import time
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.task import Task
from panda3d.core import AmbientLight, DirectionalLight
import queue
import socket
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf


DENOMINATOR = 2147483647.0
REF = 5.08
PORT = 12345
ROWS = 200
COLS = 5


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Load the model with animations included in the .bam file
        self.hand_model = Actor("handmodel.bam")

        # Reposition the model
        self.hand_model.setScale(1, 1, 1)
        self.hand_model.setPos(0, 0, 0)

        # Attach model to the render tree
        self.hand_model.reparentTo(self.render)

        # Add basic lighting
        ambient_light = AmbientLight("ambient_light")
        ambient_light.setColor((0.5, 0.5, 0.5, 1))
        ambient_light_node = self.render.attachNewNode(ambient_light)
        self.render.setLight(ambient_light_node)

        directional_light = DirectionalLight("directional_light")
        directional_light.setColor((1, 1, 1, 1))
        directional_light_node = self.render.attachNewNode(directional_light)
        directional_light_node.setHpr(0, -60, 0)
        self.render.setLight(directional_light_node)

        # Position the camera
        self.camera.setPos(5, -10, 5)
        self.camera.lookAt(self.hand_model)

        # Trigger variables
        self.openTrigger = False
        self.closeTrigger = False

        # Animation state
        self.current_animation = "HandOpen"  # Default animation
        self.hand_model.loop(self.current_animation)  # Start with default loop animation

        # Add a task to check triggers and play animations
        self.taskMgr.add(self.update_animations, "UpdateAnimationsTask")

        # Queue for inter-process communication
        self.trigger_queue = queue.Queue()

        # Start the data reading and inference thread
        self.data_thread = threading.Thread(target=self.data_reading_and_inference)
        self.data_thread.daemon = True  # Daemonize thread
        self.data_thread.start()

    def update_animations(self, task):
        # Check if any trigger is active
        if self.openTrigger:
            if self.current_animation != "HandOpening":
                self.current_animation = "HandOpening"
                self.hand_model.play("HandOpening")
                self.hand_model.setPlayRate(1.0, "HandOpening")  # Set playback rate
        elif self.closeTrigger:
            if self.current_animation != "HandClosing":
                self.current_animation = "HandClosing"
                self.hand_model.play("HandClosing")
                self.hand_model.setPlayRate(1.0, "HandClosing")  # Set playback rate
        else:
            # Default to looping HandOpen or HandClosed based on last state
            if self.current_animation in ["HandOpening", "HandClosing"]:
                if not self.hand_model.isPlaying():
                    # Animation finished, switch to loop
                    self.current_animation = "HandOpen" if self.current_animation == "HandOpening" else "HandClosed"
                    self.hand_model.loop(self.current_animation)
                    self.hand_model.setPlayRate(1.0, self.current_animation)  # Set playback rate

        return Task.cont

    def data_reading_and_inference(self):
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
                            inference_result = model(np_array[:,1:].reshape(1,200,4)).numpy()
                            print(inference_result)
                            if inference_result > 0.5 :
                                self.openTrigger = True
                                self.closeTrigger = False
                            elif inference_result < 0.5:
                                self.openTrigger = False
                                self.closeTrigger = True





print("starting")
model = tf.keras.models.load_model('model')
print('model loaded')
app = MyApp()
app.run()
