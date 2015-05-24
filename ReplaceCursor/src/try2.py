import sys
sys.path.insert(0, "../lib")
import Leap

from Tkinter import *
import ttk


import time
import subprocess
from statistics import variance
from Leap import CircleGesture
from FuzzyLogic.FuzzyComputation import compute_sickness

text = "Hold your hand still for 2 seconds..."


class SampleListener(Leap.Listener):
    # the distance between clicks cannot be less than x seconds
    now, scroll, right_click = time.time(), time.time(), time.time()
    down = False
    last_frame_x, last_frame_y = [None] * 5, [None] * 5
    counter = 0

    start_counter = time.time()
    fuzzy_inputs = {'x': [], 'y': [],
                    'fingers_distance': {
                        'index': [], 'middle': [], 'ring': [], 'pinky': []}
                    }

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

        # app_width, app_height = 1365, 765
        i_box = frame.interaction_box

        # index + middle finger for click and double click
        n1 = i_box.normalize_point(hand.fingers[1].stabilized_tip_position)
        n2 = i_box.normalize_point(hand.fingers[2].stabilized_tip_position)
        n3 = i_box.normalize_point(hand.fingers[3].stabilized_tip_position)
        n4 = i_box.normalize_point(hand.fingers[4].stabilized_tip_position)

        # read for 2 seconds the coordinates of the hand,
        # so it can be stabilized accordingly
        if time.time() - self.start_counter <= 2:
            app_x, app_y = self.get_normal_coordinates(frame)

            self.fuzzy_inputs['x'].append(app_x)
            self.fuzzy_inputs['y'].append(app_y)
            self.fuzzy_inputs['fingers_distance']['index'].append(n1.x)
            self.fuzzy_inputs['fingers_distance']['middle'].append(n2.x)
            self.fuzzy_inputs['fingers_distance']['ring'].append(n3.x)
            self.fuzzy_inputs['fingers_distance']['pinky'].append(n4.x)
        else:
            sickenss = self._get_sickness()
            if sickenss <= 4:
                print "Not Sick"
                app_x, app_y = self.get_normal_coordinates(frame)
            else:
                print "Sick"
                app_x, app_y = self.get_stabilized_coordinates(frame)

            bash_command = "xdotool mousemove %f %f" % (app_x, app_y)
            self.execute_command(bash_command)

            self.check_click(n1, n2, n3, n4)
            self.check_right_click(frame)
            self.check_drag_and_drop(hand)
            self.check_scroll(frame)

    def _fingers_distance(self, index, middle, ring, pinky):
        return min(abs(index.x - middle.x),
                   abs(middle.x - ring.x),
                   abs(ring.x - pinky.x))

    def _fingers_extended(self, index, middle, ring, pinky):
        return (abs(index.x - middle.x) > 0.13
                or abs(middle.x - ring.x) > 0.12
                or abs(ring.x - pinky.x) > 0.10)

    def _get_sickness(self):
        # the maximum the variance can be is 10 000
        x_variance = variance(self.fuzzy_inputs['x'])
        x_variance = 10 * x_variance / 10000 if x_variance <= 10000 else 10
        y_variance = variance(self.fuzzy_inputs['y'])
        y_variance = 10 * y_variance / 10000 if y_variance <= 10000 else 10

        # take into account the fingers between
        # which the distance modfies the most
        fingers = self.fuzzy_inputs['fingers_distance']
        index_variance = variance(fingers['index'])
        middle_variance = variance(fingers['middle'])
        ring_variance = variance(fingers['ring'])
        pinky_variance = variance(fingers['pinky'])
        d_variance = 1000 * max(
            [index_variance, middle_variance, ring_variance, pinky_variance])

        if x_variance > y_variance:
            sickness = compute_sickness(x_variance, d_variance)
        else:
            sickness = compute_sickness(y_variance, d_variance)

        return sickness

    def get_normal_coordinates(self, frame):
        hand = frame.hands[0]
        app_width, app_height = 1365, 765
        i_box = frame.interaction_box

        normalized_tip = i_box.normalize_point(
                hand.stabilized_palm_position)
        # ibox is shrunk from 0.2-07 for x axis and 0.3 - 0.8 for y axis
        app_x = (normalized_tip.x - 0.2) * 2 * app_width
        app_x = app_x if app_x >= 0 else 0
        app_y = ((1 - normalized_tip.y) - 0.3) * 2 * app_height
        return (app_x, app_y)

    def _shift_x(self):
        for i in range(4):
            self.last_frame_x[i] = self.last_frame_x[i+1]

    def _shift_y(self):
        for i in range(4):
            self.last_frame_y[i] = self.last_frame_y[i+1]

    def get_stabilized_coordinates(self, frame):
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
            self.last_frame_x[4] = (sum(self.last_frame_x[:4]) +
                                    hand.stabilized_palm_position.x) / 5
            self.last_frame_y[4] = (sum(self.last_frame_y[:4]) +
                                    hand.stabilized_palm_position.y) / 5

            l = Leap.Vector(self.last_frame_x[4], self.last_frame_y[4], 0)

            # ibox is shrunk from 0.2-07 for x axis and 0.3 - 0.8 for y axis
            normalized_tip = i_box.normalize_point(l)
            app_x = (normalized_tip.x - 0.2) * 2 * app_width
            app_x = app_x if app_x >= 0 else 0
            app_y = ((1 - normalized_tip.y) - 0.3) * 2 * app_height
            return (app_x, app_y)
        return (0, 0)

    def check_click(self, n1, n2, n3, n4):
        if time.time() - self.now >= 0.35:
            if self._fingers_extended(n1, n2, n3, n4):
                bash_command = "xdotool click --repeat 1 1"
                self.execute_command(bash_command)
                self.now = time.time()

    def check_right_click(self, frame):
        if len(frame.hands) == 2 and time.time() - self.right_click >= 1:
            bash_command = "xdotool click 3"
            self.execute_command(bash_command)
            self.right_click = time.time()

    def check_scroll(self, frame):
        if time.time() - self.scroll >= 0.1:
            for gesture in frame.gestures():
                if gesture.type == Leap.Gesture.TYPE_CIRCLE:
                    circle = CircleGesture(gesture)
                    if circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/2:
                        # clockwise - move down
                        bash_command = "xdotool click --clearmodifiers 5"
                    else:
                        # counterclockwise - move up
                        bash_command = "xdotool click --clearmodifiers 4"
                    self.execute_command(bash_command)
            self.scroll = time.time()

    def check_drag_and_drop(self, hand):
        bash_command = ''
        if hand.grab_strength == 1 and self.down is False:
            bash_command = "xdotool mousedown 1"
            self.down = True
        elif hand.grab_strength < 1 and self.down is True:
            bash_command = "xdotool mouseup 1"
            self.down = False
        if bash_command:
            self.execute_command(bash_command)

    def execute_command(self, bash_command):
        process = subprocess.Popen(
            bash_command.split(), stdout=subprocess.PIPE)
        process.communicate()[0]


def main():
    def close():
        controller.remove_listener(listener)
        exit()

    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # GUI
    root = Tk()
    root.title("Cursor")

    mainframe = ttk.Frame(root, padding="20 20 20 20")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)

    ttk.Label(mainframe, text=text).grid(column=3, row=1, sticky=W)
    ttk.Button(mainframe,
               text="Close",
               command=close).grid(column=3, row=2, sticky=W)

    for child in mainframe.winfo_children():
        child.grid_configure(padx=5, pady=5)
    root.mainloop()

if __name__ == "__main__":
    main()
