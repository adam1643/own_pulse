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


class Pulse(object):

    def __init__(self):
        self.camera = Camera(camera=0)
        if not self.camera.valid:
            raise ValueError("ERROR!")

        self.w, self.h = 0, 0

        self.e = Emotions()
        self.processor = findFaceGetPulse(emotions=self.e)

        self.moved_window = False

        self.logged_in = False

        self.bpm = 0

        self.sending_pulse = False
        self.sending_emotions = False

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

        output_frame = cv2.resize(output_frame, (800, 452))
        cv2image = cv2.cvtColor(output_frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)

        bpms = self.processor.get_bpms()

        sum_pulse = 0
        for b in bpms:
            sum_pulse = sum_pulse + b
        if len(bpms) > 0:
            self.bpm = int(sum_pulse / len(bpms))
        else:
            self.bpm = "---"

        if self.sending_pulse is False and self.processor.pulse_measured is True and self.logged_in is True:
            send_pulse()

        if self.sending_emotions is False and self.e.emotions_measured is True and self.logged_in is True:
            send_emotions()

        if self.processor.gap:
            v2.set("Czekaj... " + str(int(self.processor.gap)) + " s")
        else:
            v2.set(str(self.bpm))
        # var_emotions.set(self.e.get_last_prediction_str())
        # var_best.set(self.e.get_best_emotion())
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


def login_entry(event):
    if entry.get() == 'nazwa użytkownika':
        entry.delete(0, "end")  # delete all the text in the entry
        entry.insert(0, '')  # Insert blank for user input
        entry.config(fg="black")


def password_entry(event):
    if entry2.get() == 'hasło':
        entry2.delete(0, "end")  # delete all the text in the entry
        entry2.insert(0, '')  # Insert blank for user input
        entry2.config(show="\u2022")  # set dots for password entry
        entry2.config(fg="black")


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


root = tk.Tk()
root.title("E-Health System")

p = Pulse()
conn = BackendConnection()


def login_callback():
    print("%s:%s" % (entry.get(), entry2.get()))
    conn.login(entry.get(), entry2.get(), login_response)


def callback_start():
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

# pierwsza linijka
labelLogin = tk.Label(frame_login, text="Zaloguj się: ")
labelLogin.grid(column=0, row=0)

# pola do logowania
entry = tk.Entry(frame_login, bd=1)
entry.insert(0, 'nazwa użytkownika')
entry.bind('<FocusIn>', login_entry)
entry.grid(column=0, row=1)
entry.config(fg="#999999")

entry2 = tk.Entry(frame_login, bd=1)
entry2.insert(0, 'hasło')
entry2.bind('<FocusIn>', password_entry)
entry2.grid(column=0, row=2)
entry2.config(fg="#999999")

# przycisk logowania
button_login = tk.Button(frame_login, text="Zaloguj", width=10, command=login_callback)
button_login.grid(column=0, row=3, pady=5)

# link do strony
label_link = tk.Label(frame_login, text="Nie masz konta? Zarejestruj się", width=32)
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

label_pulse = tk.Label(frame_pulse, text="PULS", width=21)
label_pulse.grid(column=0, row=0, sticky=tk.E + tk.W + tk.N + tk.S)
bold_font = font.Font(label_link, label_link.cget("font"))
bold_font.configure(weight="bold")
bold_font.configure(size=18)
label_pulse.configure(font=bold_font)

v2 = tk.StringVar()
v2.set("---")
label3 = tk.Label(frame_pulse, textvariable=v2, fg="blue")
label3.config(font=("Courier", 20))
label3.grid(column=0, row=1, sticky=tk.E + tk.W + tk.N + tk.S)

# przycisk pomiaru
b2 = tk.Button(frame_pulse, text="Wykonaj pomiary", command=callback_start)
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

for i in range(7):
    var_emotions[i].set("")
    (labels_emotion[i], labels_emotions_value[i]) = insert_row(frame=frame_emotions, index=i, text=emotions_l[i],
                                                               text_var=var_emotions[i])

# najlepszy wynik
# var_best = tk.StringVar()
# var_best.set("Best")
# label_emotions = tk.Label(root, textvariable=var_best, fg="red")
# label_emotions.config(font=("Courier", 30))
# label_emotions.grid(column=0, row=16)

# ----------------- FRAME EMOTIONS END --------------


# ----------------- FRAME MAIN VIDEO ----------------

# głowne wideo
lmain = tk.Label(root)
lmain.grid(column=1, row=0, columnspan=4, rowspan=17)
lmain.lower()

# popup o zapisanych danych
label_saved = tk.Label(root, text="Dane zapisano!", bg="#EEEEEE")
label_saved.grid(column=1, row=16, columnspan=4, sticky=tk.E+tk.S)
label_saved.lower()
label_saved.lower()

# ostatnia linijka
warning_text = tk.StringVar()
warning_text.set("Musisz być zalogowany, żeby zapisać wyniki!")
label_warning = tk.Label(root, textvariable=warning_text, fg="red", bg="#DDDDDD")
label_warning.grid(column=1, row=16, columnspan=4, sticky=tk.S)


# ----------------- FRAME MAIN VIDEO END ------------


# a = conn.register_user("adam", "adam")
# print(a.text)


def login_response(response, **kwargs):
    print(response.status_code)
    # print("UDALO SIE!", json.loads(response.content)['id'])
    if response.status_code is 200:
        uid = json.loads(response.content)['id']
        conn.set_user_id(uid)
        conn.logged = True
        p.logged_in = True
        lmain1 = tk.Label(frame_login, text=("Zalogowano jako:\n" + entry.get()))
        lmain1.grid(column=0, row=0, rowspan=4, sticky=tk.W + tk.E + tk.N + tk.S)

        # link do strony
        label_link_results = tk.Label(frame_login, text="Przejdź do historii wyników", width=32)
        label_link_results.bind("<Button-1>", open_website)
        label_link_results.bind("<Enter>", on_enter)
        label_link_results.bind("<Leave>", on_leave)

        label_link_results.configure(font=underline_font)
        label_link_results.grid(column=0, row=4, rowspan=2)

        label_warning.lower()
    else:
        print("a")
        lmain1 = tk.Label(frame_login, text=("Błędne dane logowania! Spróbuj ponownie"), fg="red")
        lmain1.grid(column=0, row=3, rowspan=1, sticky=tk.N + tk.S)
        root.after(2000, lmain1.destroy)


def send_response(response, **kwargs):
    print(response.status_code)
    if response.status_code is 200:
        label_saved.lift(aboveThis=lmain)
        root.after(1000, hide_label)
    else:
        print("Błąd")


while True:
    p.loop()
    root.update_idletasks()
    root.update()

#
# [{ "_id" : ObjectId("5cd5f95db03d621b50347990"), "userId" : "5cd5f75a50805d51d06b25bb", "pulse" : 55, "createdAt" : ISODate("2019-05-10T12:21:17.669Z"), "_class" : "pl.mdados.ehealth.model.PulseReadout" }]
#
# [{"id":"5cd5f93fb03d621b50347993","userId":"5cd5f75a50805d51d06b25bb","pulse":55,"comment":null,"createdAt":"2019-05-10T20:20:47.536+0000"}, {"id":"5cd5f93fb03d621b50347992","userId":"5cd5f75a50805d51d06b25bb","pulse":60,"comment":null,"createdAt":"2019-05-10T18:20:47.536+0000"}, {"id":"5cd5f93fb03d621b50347991","userId":"5cd5f75a50805d51d06b25bb","pulse":85,"comment":null,"createdAt":"2019-05-10T16:20:47.536+0000"}]
