from lib.cam import Camera
import cv2
import tkinter as tk
from tkinter import font

from lib.processing import findFaceGetPulse
from lib.connection import BackendConnection
from lib.emotions import Emotions
from PIL import Image, ImageTk

import webbrowser
from threading import Timer
import json

from text_strings import *


class Pulse(object):

    def __init__(self):
        self.camera = Camera(camera=0)
        if not self.camera.valid:
            raise ValueError("ERROR!")

        self.w, self.h = 0, 0

        self.e = Emotions()
        self.processor = findFaceGetPulse(emotions=self.e)

        self.logged_in = False

        self.bpm = 0

        self.sending_pulse = False
        self.sending_emotions = False

    def start(self):
        self.processor.find_faces_toggle()

    def mean(self, x):
        length = len(x)
        if length is 0:
            return "---"

        sum = 0
        for a in x:
            sum = sum + a
        return sum / length

    def loop(self):
        frame = self.camera.get_frame()
        frame = cv2.flip(frame, 1)
        self.h, self.w, _c = frame.shape
        self.processor.frame_in = frame
        # process the image frame to perform all needed analysis
        self.processor.run()
        # collect the output frame for display
        output_frame = self.processor.frame_out

        output_frame = cv2.resize(output_frame, (800, 452))
        cv2image = cv2.cvtColor(output_frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)

        bpms = self.processor.get_bpms()
        self.bpm = self.mean(bpms)

        if self.sending_pulse is False and self.processor.pulse_measured is True and self.logged_in is True:
            send_pulse()

        if self.sending_emotions is False and self.e.emotions_measured is True and self.logged_in is True:
            send_emotions()

        if self.processor.gap:
            text_var_pulse.set(TXT_WAIT + str(int(self.processor.gap)) + " s")
        else:
            text_var_pulse.set(str(self.bpm))

        set_emotions_labels(self.e.get_last_prediction())


def send_pulse():
    if p.processor.pulse_measured is True:
        p.sending_pulse = True
        conn.save_pulse(p.bpm, send_response)
        Timer(5.0, send_pulse).start()
    else:
        p.sending_pulse = False


def send_emotions():
    if p.e.emotions_measured is True:
        p.sending_emotions = True
        conn.save_emotions(p.e.get_last_prediction(), send_response)
        Timer(5.0, send_emotions).start()
    else:
        p.sending_emotions = False


def username_entry(event):
    if entry_username.get() == TXT_USERNAME:
        entry_username.delete(0, "end")  # delete all the text in the entry
        entry_username.insert(0, '')  # Insert blank for user input
        entry_username.config(fg="black")


def password_entry(event):
    if entry_password.get() == TXT_PASSWORD:
        entry_password.delete(0, "end")  # delete all the text in the entry
        entry_password.insert(0, '')  # Insert blank for user input
        entry_password.config(show="\u2022")  # set dots for password entry
        entry_password.config(fg="black")


def set_emotions_labels(emotions):
    for i in range(7):
        f = font.Font(labelLogin, labelLogin.cget("font"))
        labels_emotion[i].configure(font=f, fg='black')
        labels_emotions_value[i].configure(font=f, fg='black')
        e = emotions[i]
        e = "{:0.2f}%".format(e * 100)
        var_emotions[i].set(e)

    max_emotion = emotions.argmax()
    bold_font = font.Font(labels_emotion[max_emotion], labels_emotion[max_emotion].cget("font"))
    bold_font.configure(weight="bold")
    labels_emotion[max_emotion].configure(font=bold_font, fg='red')
    labels_emotions_value[max_emotion].configure(font=bold_font, fg='red')


p = Pulse()
conn = BackendConnection()
root = tk.Tk()
root.title(TXT_TITLE)


def login_callback():
    print("%s:%s" % (entry_username.get(), entry_password.get()))
    conn.login(entry_username.get(), entry_password.get(), login_response)


def start_pulse_measure():
    p.start()


def hide_label():
    label_saved.lower()


def open_website(event):
    webbrowser.open_new(r"http://www.google.com")


def on_enter(event):
    event.widget.config(fg="blue")


def on_leave(event):
    event.widget.config(fg="black")


# ------------------- FRAME LOGIN -------------------

frame_login = tk.Frame(root, highlightbackground="black", highlightcolor="black", highlightthickness=2, bd=0)
frame_login.grid(column=0, row=0, rowspan=5, sticky=tk.E + tk.W + tk.N + tk.S, pady=3, padx=3)
frame_login.lift()

# first line
labelLogin = tk.Label(frame_login, text=TXT_LOG_IN)
labelLogin.grid(column=0, row=0)

# login entrys
entry_username = tk.Entry(frame_login, bd=1)
entry_username.insert(0, TXT_USERNAME)
entry_username.bind('<FocusIn>', username_entry)
entry_username.grid(column=0, row=1)
entry_username.config(fg="#999999")

entry_password = tk.Entry(frame_login, bd=1)
entry_password.insert(0, TXT_PASSWORD)
entry_password.bind('<FocusIn>', password_entry)
entry_password.grid(column=0, row=2)
entry_password.config(fg="#999999")

# login button
button_login = tk.Button(frame_login, text=TXT_LOG_IN_BUTTON, width=10, command=login_callback)
button_login.grid(column=0, row=3, pady=5)

# url to web app
label_link = tk.Label(frame_login, text=TXT_REGISTER_INFO, width=32)
label_link.bind("<Button-1>", open_website)
label_link.bind("<Enter>", on_enter)
label_link.bind("<Leave>", on_leave)
underline_font = font.Font(label_link, label_link.cget("font"))
underline_font.configure(underline=True)
label_link.configure(font=underline_font)
label_link.grid(column=0, row=4)

# ----------------- FRAME LOGIN END -----------------


# ----------------- FRAME PULSE ---------------------

frame_pulse = tk.Frame(root, highlightbackground="black", highlightcolor="black", highlightthickness=1, bd=0)
frame_pulse.grid(column=0, row=5, rowspan=5, sticky=tk.E + tk.W + tk.N + tk.S, pady=3, padx=3)
frame_pulse.lift()

# PULSE label
label_pulse = tk.Label(frame_pulse, text=TXT_PULSE, width=21)
label_pulse.grid(column=0, row=0, sticky=tk.E + tk.W + tk.N + tk.S)
bold_font = font.Font(label_link, label_link.cget("font"))
bold_font.configure(weight="bold")
bold_font.configure(size=18)
label_pulse.configure(font=bold_font)

# pulse result
text_var_pulse = tk.StringVar()
text_var_pulse.set("---")
label3 = tk.Label(frame_pulse, textvariable=text_var_pulse, fg="blue")
label3.config(font=("Courier", 20))
label3.grid(column=0, row=1, sticky=tk.E + tk.W + tk.N + tk.S)

# measure start button
b2 = tk.Button(frame_pulse, text=TXT_START_MEASURE_BUTTON, command=start_pulse_measure)
b2.grid(column=0, row=2)


# ----------------- FRAME PULSE END -----------------


# ----------------- FRAME EMOTIONS ------------------

def insert_row(frame=None, index=None, text=None, text_var=None):
    l1 = tk.Label(frame, borderwidth=1, relief="groove", width=22, text=text)
    l1.grid(column=0, row=index, sticky=tk.E + tk.W + tk.N + tk.S)
    l2 = tk.Label(frame, borderwidth=1, relief="groove", width=10, textvariable=text_var)
    l2.grid(column=1, row=index, sticky=tk.E + tk.W + tk.N + tk.S)
    return l1, l2


frame_emotions = tk.Frame(root, bd=0)
frame_emotions.grid(column=0, row=10, rowspan=7, sticky=tk.E + tk.W + tk.N + tk.S, pady=3, padx=3)
frame_emotions.lift()

labels_emotion = [None] * 7
labels_emotions_value = [None] * 7
var_emotions = [tk.StringVar() for i in range(7)]

emotions_l = ['Złość', 'Zniesmaczenie', 'Strach', 'Radość', 'Smutek', 'Zaskoczenie', 'Obojętność']

# row for each emotion
for i in range(7):
    var_emotions[i].set("")
    (labels_emotion[i], labels_emotions_value[i]) = insert_row(frame=frame_emotions, index=i, text=emotions_l[i],
                                                               text_var=var_emotions[i])

# best result
# var_best = tk.StringVar()
# var_best.set("Best")
# label_emotions = tk.Label(root, textvariable=var_best, fg="red")
# label_emotions.config(font=("Courier", 30))
# label_emotions.grid(column=0, row=16)

# ----------------- FRAME EMOTIONS END --------------


# ----------------- FRAME MAIN VIDEO ----------------

# main video stream
lmain = tk.Label(root)
lmain.grid(column=1, row=0, columnspan=4, rowspan=17)
lmain.lower()

# data saved popup
label_saved = tk.Label(root, text=TXT_DATA_SAVED, bg="#EEEEEE")
label_saved.grid(column=1, row=16, columnspan=4, sticky=tk.E + tk.S)
label_saved.lower()
label_saved.lower()

# login reminder
warning_text = tk.StringVar()
warning_text.set(TXT_LOGGING_REQUIRED_FOR_SAVING)
label_warning = tk.Label(root, textvariable=warning_text, fg="red", bg="#DDDDDD")
label_warning.grid(column=1, row=16, columnspan=4, sticky=tk.S)


# ----------------- FRAME MAIN VIDEO END ------------


# a = conn.register_user("adam", "adam")
# print(a.text)


def login_response(response, **kwargs):
    if response.status_code is 200:
        uid = json.loads(response.content)['id']
        conn.set_user_id(uid)
        conn.logged = True
        p.logged_in = True
        label_logged_in = tk.Label(frame_login, text=(TXT_LOGGED_AS + "\n" + entry_username.get()))
        label_logged_in.grid(column=0, row=0, rowspan=4, sticky=tk.W + tk.E + tk.N + tk.S)

        # url to web app
        label_link_results = tk.Label(frame_login, text=TXT_RESULTS_HISTORY, width=32)
        label_link_results.bind("<Button-1>", open_website)
        label_link_results.bind("<Enter>", on_enter)
        label_link_results.bind("<Leave>", on_leave)

        label_link_results.configure(font=underline_font)
        label_link_results.grid(column=0, row=4, rowspan=2)

        label_warning.lower()
    else:
        label_logged_in = tk.Label(frame_login, text=TXT_WRONG_CREDENTIALS, fg="red")
        label_logged_in.grid(column=0, row=3, rowspan=1, sticky=tk.N + tk.S)
        # hide window after 2 s
        root.after(2000, label_logged_in.destroy)


def send_response(response, **kwargs):
    print(response.status_code)
    if response.status_code is 200:
        label_saved.lift(aboveThis=lmain)
        root.after(1000, hide_label)


while True:
    p.loop()
    root.update_idletasks()
    root.update()
