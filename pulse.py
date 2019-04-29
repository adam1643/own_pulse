from lib.tools import waitKey, imshow
from lib.cam import Camera
import cv2
import tkinter as tk
import sys
from lib.processing import findFaceGetPulse
from lib.connection import BackendConnection
from PIL import Image, ImageTk

from lib.ui import Example

from threading import Timer


class pulse(object):

    def __init__(self):
        self.camera = Camera(camera=0)
        if not self.camera.valid:
            raise ValueError("ERROR!")

        self.w, self.h = 0, 0

        self.processor = findFaceGetPulse()

        self.moved_window = False

        self.logged_in = False

        self.connection = BackendConnection()

    def start(self):
        self.processor.find_faces_toggle()

    def loop(self):
        frame = self.camera.get_frame()
        frame = cv2.flip(frame, 1)
        self.h, self.w, _c = frame.shape
        self.processor.frame_in = frame
        # process the image frame to perform all needed analysis
        self.processor.run(1)
        # collect the output frame for display
        output_frame = self.processor.frame_out
        # imshow("Processed", output_frame)
        #
        # if self.moved_window is False:
        #     self.moved_window = True
        #     cv2.moveWindow("Processed", 40, 40)
        output_frame = cv2.resize(output_frame, (800, 452))
        cv2image = cv2.cvtColor(output_frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)
        # v2.set(int(self.processor.get_bpm()))

        bpms = self.processor.get_bpms()
        ss = ""
        sum = 0
        for b in bpms:
            ss = ss + "/" + str(int(b))
            sum = sum + b
        if len(bpms) > 0:
            bpm = int(sum/len(bpms))
        else:
            bpm = "---"

        if self.processor.gap:
            v2.set("Czekaj...\n" + str(int(self.processor.gap)) + " s")
        else:
            v2.set("Puls:\n" + str(bpm))
        v.set(ss)


    def send_pulse(self):
        print("Hello")
        print(self.processor.get_bpm())
        a = self.connection.save_pulse(int(self.processor.get_bpm()))
        print(a.get().response.content)
        Timer(5.0, self.send_pulse).start()

    def toggle_send(self):
        self.logged_in = True
        Timer(5.0, self.send_pulse).start()





def on_entry_click(event):
    """function that gets called whenever entry is clicked"""
    if entry.get() == 'nazwa użytkownika':
        entry.delete(0, "end")  # delete all the text in the entry
        entry.insert(0, '')  # Insert blank for user input


def on_entry_click2(event):
    """function that gets called whenever entry is clicked"""
    if entry2.get() == 'hasło':
        entry2.delete(0, "end")  # delete all the text in the entry
        entry2.insert(0, '')  # Insert blank for user input
        entry2.config(show="\u2022");


root = tk.Tk()
root.title("PULS")


p = pulse()

def callback():
    print("%s:%s" % (entry.get(), entry2.get()))
    if conn.login(entry.get(), entry2.get()):
        v.set("SUKCES!")
        p.logged_in = True
        p.toggle_send()



def callback_start():
    p.start()

# root.columnconfigure(1, weight=1)
# root.columnconfigure(3, pad=7)
# root.rowconfigure(3, weight=1)
# root.rowconfigure(5, pad=7)

label = tk.Label(root, text="Zaloguj: ")
label.grid(column=0, row=0)
# label.pack()

v = tk.StringVar()
v.set("Musisz być zalogowany, żeby zapisać wyniki!")
label2 = tk.Label(root, textvariable=v, fg="red")
label2.grid(column=1, row=9, columnspan=4)
# label2.pack()

v3 = tk.StringVar()
v3.set("Musisz być zalogowany, żeby zapisać wyniki!")
label_log = tk.Label(root, textvariable=v3, fg="red")
label_log.grid(column=0, row=4)

v2 = tk.StringVar()
v2.set("---")
label3 = tk.Label(root, textvariable=v2, fg="blue")
label3.config(font=("Courier", 30))
# label3.pack(anchor='nw')
label3.grid(column=0, row=6)

entry = tk.Entry(root, bd=1)
entry.insert(0, 'nazwa użytkownika')
entry.bind('<FocusIn>', on_entry_click)
entry.grid(column=0, row=1)
# entry.pack()

entry2 = tk.Entry(root, bd=1)
entry2.insert(0, 'hasło')
entry2.bind('<FocusIn>', on_entry_click2)
# entry2.pack()
entry2.grid(column=0, row=2)

b = tk.Button(root, text="OK", width=10, command=callback)
b.grid(column=0, row=3)
# b.pack()

b2 = tk.Button(root, text="Zmierz!", width=10, command=callback_start)
# b2.pack()
b2.grid(column=0, row=7)

lmain = tk.Label(root)
# lmain.pack()
lmain.grid(column=1, row=0, columnspan=4, rowspan=9)
conn = BackendConnection()



# a = conn.register_user("adam2", "adam")
# print(a.text)
# print(conn.login("adam", "ad1am"))
# a = conn.get_user_id()
# print(a.json()['id'])

while True:
    p.loop()
    root.update_idletasks()
    root.update()
