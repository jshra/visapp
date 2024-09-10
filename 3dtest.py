from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.task import Task
from panda3d.core import AmbientLight, DirectionalLight

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

        # Simulate external logic for triggers (example: changing triggers every 5 seconds)
        self.taskMgr.add(self.simulate_trigger_logic, "SimulateTriggerLogicTask")

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

    def simulate_trigger_logic(self, task):
        # This function simulates external logic to toggle triggers
        import time
        # Simple simulation: toggle triggers based on time
        elapsed_time = task.time
        if int(elapsed_time) % 10 < 5:
            self.openTrigger = True
            self.closeTrigger = False
        else:
            self.openTrigger = False
            self.closeTrigger = True
        
        return Task.cont

app = MyApp()
app.run()
