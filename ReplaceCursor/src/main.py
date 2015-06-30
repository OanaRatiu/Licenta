import sys
sys.path.insert(0, "../lib")
import Leap

from Tkinter import Tk, BOTH
from ttk import Frame, Button, Style, Label
# from gui import FirstWindow

import time
import subprocess
# from statistics import variance
import numpy as np
from Leap import CircleGesture
from FuzzyLogic.FuzzyComputation import SicknessManager as SM


class SicknessListener(Leap.Listener):
    fuzzy_inputs = {'x': [], 'y': [],
                    'fingers_distance': {
                        'index': [], 'middle': [], 'ring': [], 'pinky': []}
                    }

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

        app_x, app_y = self.get_normal_coordinates(frame)

        self.fuzzy_inputs['x'].append(app_x)
        self.fuzzy_inputs['y'].append(app_y)
        self.fuzzy_inputs['fingers_distance']['index'].append(n1.x)
        self.fuzzy_inputs['fingers_distance']['middle'].append(n2.x)
        self.fuzzy_inputs['fingers_distance']['ring'].append(n3.x)
        self.fuzzy_inputs['fingers_distance']['pinky'].append(n4.x)

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


class BaseListener(Leap.Listener):
    now, scroll, right_click = time.time(), time.time(), time.time()
    down = False

    def on_connect(self, controller):
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);

    def _fingers_extended(self, index, middle, ring, pinky):
        # return (abs(index.x - middle.x) > 0.13
        #         or abs(middle.x - ring.x) > 0.12
        #         or abs(ring.x - pinky.x) > 0.10)
        return ((abs(index.x - middle.x) > 0.13 and abs(middle.x - ring.x) > 0.12)
            or (abs(middle.x - ring.x) > 0.12 and abs(ring.x - pinky.x) > 0.10))

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


class CursorListener(BaseListener):
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

        app_x, app_y = self.get_normal_coordinates(frame)

        bash_command = "xdotool mousemove %f %f" % (app_x, app_y)
        self.execute_command(bash_command)

        self.check_click(n1, n2, n3, n4)
        self.check_right_click(frame)
        self.check_drag_and_drop(hand)
        self.check_scroll(frame)

    def get_normal_coordinates(self, frame):
        hand = frame.hands[0]
        app_width, app_height = 1365, 765
        i_box = frame.interaction_box

        normalized_tip = i_box.normalize_point(hand.stabilized_palm_position)
        # ibox is shrunk from 0.2-07 for x axis and 0.3 - 0.8 for y axis
        app_x = (normalized_tip.x - 0.2) * 2 * app_width
        app_x = app_x if app_x >= 0 else 0
        app_y = ((1 - normalized_tip.y) - 0.3) * 2 * app_height
        return (app_x, app_y)


class StabilizedCursorListener(BaseListener):
    last_frame_x, last_frame_y = 5 * [None], 5 * [None]
    counter = 0

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

        app_x, app_y = self.get_stabilized_coordinates(frame)

        bash_command = "xdotool mousemove %f %f" % (app_x, app_y)
        self.execute_command(bash_command)

        self.check_click(n1, n2, n3, n4)
        self.check_right_click(frame)
        self.check_drag_and_drop(hand)
        self.check_scroll(frame)

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

    def _shift_x(self):
        for i in range(4):
            self.last_frame_x[i] = self.last_frame_x[i+1]

    def _shift_y(self):
        for i in range(4):
            self.last_frame_y[i] = self.last_frame_y[i+1]


class SicknessManager(object):
    def variance(self, l):
        # average = sum(l) / len(l)
        # return sum((average - value) ** 2 for value in l) / len(l)
        # return np.var(l)
        return np.std(l)

    def get_sickness(self, fuzzy_inputs):
            # the maximum the variance can be is 100
            x_variance = self.variance(fuzzy_inputs['x'])
            x_variance = 10 * x_variance / 100 if x_variance <= 100 else 10
            y_variance = self.variance(fuzzy_inputs['y'])
            y_variance = 10 * y_variance / 100 if y_variance <= 100 else 10

            # take into account the fingers between
            # which the distance modfies the most
            fingers = fuzzy_inputs['fingers_distance']
            index_variance = self.variance(fingers['index'])
            middle_variance = self.variance(fingers['middle'])
            ring_variance = self.variance(fingers['ring'])
            pinky_variance = self.variance(fingers['pinky'])
            d_variance = 100 * max(
                [index_variance, middle_variance, ring_variance, pinky_variance])

            s = SM()
            if x_variance > y_variance:
                sickness = s.compute_sickness(x_variance, d_variance)
            else:
                sickness = s.compute_sickness(y_variance, d_variance)

            return sickness


class FirstWindow(Frame):
    def __init__(self, parent, controller, listener):
        Frame.__init__(self, parent)

        self.parent = parent
        self.controller = controller
        self.listener = listener
        self.controller.add_listener(self.listener)
        self.initUI()

    def initUI(self):
        self.centerWindow()

        self.parent.title("Cursor")
        self.style = Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame")

        self.pack(fill=BOTH, expand=1)

        self.label = Label(self)
        self.label.configure(text="Hold your hand above the device for two seconds...")
        self.label.place(x=50, y=50)

        quitButton = Button(self, text="Quit",
                            command=self.quit)
        quitButton.place(x=50, y=100)

    def update_label(self):
        self.label.configure(text="You can now use the cursor.")

    def remove(self):
        self.controller.remove_listener(self.listener)

    def centerWindow(self):
        w, h = 450, 180

        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()

        x = (sw - w)/2
        y = (sh - h)/2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))


def main():
    # LEAP LOGIC
    controller = Leap.Controller()

    root = Tk()
    sickenss_listener = SicknessListener()
    w = FirstWindow(root, controller, sickenss_listener)
    w.after(2000, lambda: root.destroy())
    sickenss_listener = w.listener
    root.mainloop()
    controller.remove_listener(sickenss_listener)

    s = SicknessManager()
    try:
        sickenss_value = s.get_sickness(sickenss_listener.fuzzy_inputs)
    except:
        sickenss_value = 0
    if sickenss_value <= 4:
        listener = CursorListener()
        print 'OK'
    else:
        listener = StabilizedCursorListener()
        print 'SICK'
    root2 = Tk()
    w2 = FirstWindow(root2, controller, listener)
    w2.update_label()
    controller.add_listener(listener)
    root2.mainloop()
    controller.remove_listener(listener)


if __name__ == "__main__":
    main()
