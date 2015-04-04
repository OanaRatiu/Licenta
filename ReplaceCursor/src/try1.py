import sys
sys.path.insert(0, "../lib")
import Leap

from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
import subprocess
import time


class SampleListener(Leap.Listener):
    # the distance between clicks cannot be less than x seconds
    now = time.time()
    scroll = time.time()
    down = False
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']

    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE)

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        frame = controller.frame()
        hand = frame.hands[0]

        app_width, app_height = 1365, 765
        i_box = frame.interaction_box

        normalized_tip = i_box.normalize_point(hand.stabilized_palm_position)
        app_x = app_width * normalized_tip.x
        # positive values for y axis go down
        app_y = app_height * (1 - normalized_tip.y)

        bashCommand = "xdotool mousemove %f %f" % (app_x, app_y)
        self.execute_command(bashCommand)

        # index + middle finger for click and double click
        n1 = i_box.normalize_point(hand.fingers[1].stabilized_tip_position)
        n2 = i_box.normalize_point(hand.fingers[2].stabilized_tip_position)
        n3 = i_box.normalize_point(hand.fingers[3].stabilized_tip_position)
        n4 = i_box.normalize_point(hand.fingers[4].stabilized_tip_position)

        if time.time() - self.now >= 0.35:
            if self._fingers_extended(n1, n2, n3, n4):
                bashCommand = "xdotool click --repeat 1 1"
                self.execute_command(bashCommand)
                self.now = time.time()

        # drag & drop - rotate hand downwards 90 degrees
        bashCommand = ''
        if hand.basis.y_basis.x > 0.9 and self.down is False:
            bashCommand = "xdotool mousedown 1"
            self.down = True
        elif (hand.basis.y_basis.x > -0.2 and hand.basis.y_basis.x < 0.2
                and self.down is True):
            bashCommand = "xdotool mouseup 1"
            self.down = False
        if bashCommand:
            self.execute_command(bashCommand)

        # scroll
        if time.time() - self.scroll >= 0.1:
            for gesture in frame.gestures():
                if gesture.type == Leap.Gesture.TYPE_CIRCLE:
                    circle = CircleGesture(gesture)
                    if circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/2:
                        # clockwise - move down
                        bashCommand = "xdotool click --clearmodifiers 5"
                    else:
                        # counterclockwise - move up
                        bashCommand = "xdotool click --clearmodifiers 4"
                    self.execute_command(bashCommand)
            self.scroll = time.time()

    def _fingers_extended(self, n1, n2, n3, n4):
        return (abs(n1.x - n2.x) > 0.13
                or abs(n2.x - n3.x) > 0.12
                or abs(n3.x - n4.x) > 0.10)

    def execute_command(self, bash_command):
        process = subprocess.Popen(
            bash_command.split(), stdout=subprocess.PIPE)
        process.communicate()[0]


def main():
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()
