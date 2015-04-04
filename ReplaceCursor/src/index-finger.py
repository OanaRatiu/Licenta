import sys
sys.path.insert(0, "../lib")
import Leap

import Leap, sys, thread, time
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
import subprocess
import time


class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']
    down = False
    i_box = None
    # the distance between clicks cannot be less than x seconds
    now = time.time()

    # do not allow movements too large
    last_x, last_y = 0, 0

    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

        # Enable gestures
        # controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        # controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        # controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        # controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

        # frame = controller.frame()

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        app_width = 1365
        app_height = 765
        i_box = frame.interaction_box
        hand = frame.hands[0]

        bashCommand = ""
        if len(frame.fingers.extended()) == 5:
            if time.time() - self.now >= 2:
                bashCommand = "xdotool click --repeat 2 1"
                self.now = time.time()
        else:
            if hand.pinch_strength == 1 and self.down is False:
                bashCommand = "xdotool mousedown 1"
                self.down = True
            elif hand.pinch_strength < 1 and self.down is True:
                bashCommand = "xdotool mouseup 1"
                self.down = False
        if bashCommand:
            process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
            output = process.communicate()[0]
            bashCommand = ""

        # for pi in frame.pointables:
        #     if pi.is_finger:
        #         finger = Leap.Finger(pi)
        #         if finger.type() == 1 and finger.is_extended and len(frame.fingers.extended()) == 1:
        #             normalized_tip = i_box.normalize_point(finger.tip_position)
        #             app_x = app_width  * normalized_tip.x
        #             # positive values for y axis go down
        #             app_y = app_height * (1 - normalized_tip.y)
        #             if (self.last_x == 0 and self.last_y == 0) or (app_x - self.last_x < 50 and app_y - self.last_y < 50):
        #                 bashCommand = "xdotool mousemove %f %f" % (app_x, app_y)
        #                 process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        #                 output = process.communicate()[0]
        #                 self.last_x, self.last_y = app_x, app_y
        #             else:
        #                 self.last_x, self.last_y = 0, 0

        if len(frame.fingers.extended()) == 1:
            for pi in frame.pointables:
                if pi.is_finger:
                    finger = Leap.Finger(pi)
                    if finger.type() == 1 and finger.is_extended:
                        normalized_tip = i_box.normalize_point(finger.tip_position)
                        app_x = app_width  * normalized_tip.x
                        # positive values for y axis go down
                        app_y = app_height * (1 - normalized_tip.y)
                        if (self.last_x == 0 and self.last_y == 0) or (app_x - self.last_x < 50 and app_y - self.last_y < 50):
                            bashCommand = "xdotool mousemove %f %f" % (app_x, app_y)
                            process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
                            output = process.communicate()[0]
                            self.last_x, self.last_y = app_x, app_y
                        else:
                            self.last_x, self.last_y = 0, 0
        elif hand.pinch_strength > 0:
            pi = frame.pointables[1]
            if pi.is_finger:
                finger = Leap.Finger(pi)
                if finger.type() == 1:
                    normalized_tip = i_box.normalize_point(finger.tip_position)
                    app_x = app_width  * normalized_tip.x
                    # positive values for y axis go down
                    app_y = app_height * (1 - normalized_tip.y)
                    if (self.last_x == 0 and self.last_y == 0) or (app_x - self.last_x < 50 and app_y - self.last_y < 50):
                        bashCommand = "xdotool mousemove %f %f" % (app_x, app_y)
                        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
                        output = process.communicate()[0]
                        self.last_x, self.last_y = app_x, app_y
                    else:
                        self.last_x, self.last_y = 0, 0

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"

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
