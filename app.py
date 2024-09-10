# 3d_application.py

from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.task import Task
from panda3d.core import AmbientLight, DirectionalLight
import threading
import socket

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Load the model with animations included in the .bam file
        self.hand_model = Actor("handmodel.bam")
        print(self.hand_model.getAnimNames())
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
        # Use a separate thread for listening to avoid blocking the main thread
        threading.Thread(target=self.listen_for_triggers, daemon=True).start()

    def update_animations(self, task):
        # Check if any trigger is active
        if self.openTrigger:
            if self.current_animation != "HandOpening.001":
                self.hand_model.setPlayRate(1.5, "HandOpening.001")
                self.hand_model.play("HandOpening.001")
                self.current_animation = "HandOpening.001"
        elif self.closeTrigger:
            if self.current_animation != "HandClosing":
                self.hand_model.setPlayRate(1.5, "HandClosing")
                self.hand_model.play("HandClosing")
                self.current_animation = "HandClosing"
        else:
            # If no trigger is active, return to default looping animation
            if self.current_animation == "HandOpening.001" and not self.hand_model.getCurrentAnim():
                self.hand_model.loop("HandOpen")
                self.current_animation = "HandOpen"
            elif self.current_animation == "HandClosing" and not self.hand_model.getCurrentAnim():
                self.hand_model.loop("HandClosed")
                self.current_animation = "HandClosed"

        return Task.cont

    def listen_for_triggers(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(('localhost', 12346))
            server_socket.listen()
            print("Waiting for trigger data...")

            conn, addr = server_socket.accept()
            print(f"Connected by {addr}")
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    open_trigger, close_trigger = map(int, data.decode().split(','))
                    # if open_trigger:
                    #     print("O")
                    # elif close_trigger:
                    #     print("C")
                    # else:
                    #     print("none")
                    self.openTrigger = bool(open_trigger)
                    self.closeTrigger = bool(close_trigger)

if __name__ == "__main__":
    app = MyApp()
    app.run()
