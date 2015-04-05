import sys
sys.path.insert(0, "../lib")
import Leap

import time
import subprocess
from Leap import CircleGesture


class SampleListener(Leap.Listener):
    # the distance between clicks cannot be less than x seconds
    now, scroll = time.time(), time.time()
    down = False
    last_frame_x, last_frame_y = [None, None, None, None, None], [None, None, None, None, None]
    counter = 0

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

    def _shift_x(self):
        for i in range(4):
            self.last_frame_x[i] = self.last_frame_x[i+1]

    def _shift_y(self):
        for i in range(4):
            self.last_frame_y[i] = self.last_frame_y[i+1]

    def on_frame(self, controller):
        frame = controller.frame()
        hand = frame.hands[0]

        app_width, app_height = 1365, 765
        i_box = frame.interaction_box

        if self.counter < 5:
            self.last_frame_x[self.counter] = hand.stabilized_palm_position.x
            self.last_frame_y[self.counter] = hand.stabilized_palm_position.y
            self.counter += 1
        else:
            self._shift_x()
            self._shift_y()
            self.last_frame_x[4] = (sum(self.last_frame_x[:4]) + hand.stabilized_palm_position.x) / 5
            self.last_frame_y[4] = (sum(self.last_frame_y[:4]) + hand.stabilized_palm_position.y) / 5

            l = Leap.Vector(self.last_frame_x[4], self.last_frame_y[4], 0)
            print hand.stabilized_palm_position.x, l.x

            # version 2 - where ibox is shrunk from 0.2-07 for x axis and
            # 0.3 - 0.8 for y axis
            normalized_tip = i_box.normalize_point(l)
            app_x = (normalized_tip.x - 0.2) * 2 * app_width
            app_x = app_x if app_x >= 0 else 0  # avoid negative values for coord
            # positive values for y axis go down, so reverse the axis
            app_y = ((1 - normalized_tip.y) - 0.3) * 2 * app_height

            bash_command = "xdotool mousemove %f %f" % (app_x, app_y)
            self.execute_command(bash_command)

            # index + middle finger for click and double click
            n1 = i_box.normalize_point(hand.fingers[1].stabilized_tip_position)
            n2 = i_box.normalize_point(hand.fingers[2].stabilized_tip_position)
            n3 = i_box.normalize_point(hand.fingers[3].stabilized_tip_position)
            n4 = i_box.normalize_point(hand.fingers[4].stabilized_tip_position)

            if time.time() - self.now >= 0.35:
                if self._fingers_extended(n1, n2, n3, n4):
                    bash_command = "xdotool click --repeat 1 1"
                    self.execute_command(bash_command)
                    self.now = time.time()

        # # drag & drop - rotate hand downwards 90 degrees
        # bash_command = ''
        # if hand.basis.y_basis.x > 0.9 and self.down is False:
        #     bash_command = "xdotool mousedown 1"
        #     self.down = True
        # elif (hand.basis.y_basis.x > -0.2 and hand.basis.y_basis.x < 0.2
        #         and self.down is True):
        #     bash_command = "xdotool mouseup 1"
        #     self.down = False
        # if bash_command:
        #     self.execute_command(bash_command)

        # # scroll
        # if time.time() - self.scroll >= 0.1:
        #     for gesture in frame.gestures():
        #         if gesture.type == Leap.Gesture.TYPE_CIRCLE:
        #             circle = CircleGesture(gesture)
        #             if circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/2:
        #                 # clockwise - move down
        #                 bash_command = "xdotool click --clearmodifiers 5"
        #             else:
        #                 # counterclockwise - move up
        #                 bash_command = "xdotool click --clearmodifiers 4"
        #             self.execute_command(bash_command)
        #     self.scroll = time.time()

    def _fingers_extended(self, index, middle, ring, pinky):
        return (abs(index.x - middle.x) > 0.13
                or abs(middle.x - ring.x) > 0.12
                or abs(ring.x - pinky.x) > 0.10)

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
