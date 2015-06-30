from Tkinter import Tk, BOTH
from ttk import Frame, Button, Style, Label


class FirstWindow(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent
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

    def centerWindow(self):
        w, h = 450, 180

        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()

        x = (sw - w)/2
        y = (sh - h)/2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))


# def main():
#     root = Tk()
#     w1 = FirstWindow(root)
#     w1.after(2000, lambda: w1.update_label())

#     root.mainloop()

# if __name__ == '__main__':
#     main()
