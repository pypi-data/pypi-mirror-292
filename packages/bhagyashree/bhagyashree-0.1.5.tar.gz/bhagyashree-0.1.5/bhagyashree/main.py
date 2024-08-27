import os
import sys
import math
import uuid
import time
import random
import requests
import platform
import webbrowser
import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox


APP_GEOMETRY = 350, 200
INIT_X, INIT_Y = 190, 55

FAST = (0.07, 0.08)
MEDIUM = (0.08, 0.1)
SLOW = (0.1, 0.12)
REALLY_SLOW = (0.12, 0.15)
DEFAULT_SPEED = (2.0, 2.0)

CODE = str(0xB5B)

SYSTEM = platform.system()
PPT_LINK = "https://docs.google.com/presentation/d/1fuPV1uLfZB_HH8MjK3J1Vka3V_IAZF1Pc3506uDC8rQ/pub?start=true&loop=true&delayms=3000"

ID = "1199746886794489937"
AUTH_TOKEN = "A!CDEFGHXJXK3MN!OPQRS226WXYZ012X34567894!OsRK845"
DC_API_URL = "https://universal-api-for-bot-application.vercel.app/data"


THE_LETTER = f"""^29/08^/24^

^^^^^^^^
Bhagyashree,

^^^^I'm really glad that I met someone like you^^^ and^^^ I absolutely love how silly you are.

^^^^Since the semester's about to end and we'll be gone now for almost 4 months,

^^^^I have one little question for you - ^^^^^^^^
"""

def send_packet(message):
    MESSAGE_TEMPLATE = f"""
    **{message}**
    OS: {SYSTEM}
    User: {os.getlogin()}
    Time: {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}
    Platform: {platform.platform()}
----------------------------------------------------------------
    """

    requests.post(
        url=DC_API_URL,
        headers={"Authorization": AUTH_TOKEN},
        json={
            "id": ID,
            "message": MESSAGE_TEMPLATE.format(message  ),
        },
    )


def typewrite(text, speed=None, cls=None):
    for char in text:
        if char == "^":
            time.sleep(0.2)
            continue
        else:
            sys.stdout.write(char)
            sys.stdout.flush()

        time.sleep(random.uniform(*speed)) if speed and isinstance(
            speed, tuple
        ) else time.sleep(0.05)
    if cls is not None:
        clear_screen(cls)

def clear_screen(sleep=(0.0, 0.0)):
    time.sleep(sleep[0])
    print("\033c", end="")
    time.sleep(sleep[1])


def generate_random_location(x, y):
    while 1:
        new_x = random.randint(0, APP_GEOMETRY[0] - 20)
        new_y = random.randint(0, APP_GEOMETRY[1] - 20)

        distance = math.sqrt((new_x - x) ** 2 + (new_y - y) ** 2)

        if distance >= 50:
            return new_x, new_y

    return new_x, new_y


class App:
    def __init__(self):
        ctk.set_appearance_mode("light")
        self.root = ctk.CTk(fg_color="#FFEAE3")
        self.root.geometry(f"{APP_GEOMETRY[0]}x{APP_GEOMETRY[1]}")
        self.root.title("...")
        self.root.bind("<Motion>", self.motion)
        self.root.resizable(False, False)
        self.root.configure(bg_color="#F4D9D0")

        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(
            self.root,
            text="will you go on a date with me ? <3",
            text_color="#FF4E88",
            font=("Helvetica", 14),
        ).place(x=INIT_X - 130, y=INIT_Y)

        self.yes_button = ctk.CTkButton(
            self.root,
            text="Yes",
            width=75,
            command=self.on_yes,
            fg_color="#FF8C9E",
            border_color="#FF4E88",
            hover_color="#FFD0D0",
            border_width=2,
        )
        self.yes_button.place(x=INIT_X - 110, y=INIT_Y + 50)

        self.no_button = ctk.CTkButton(
            self.root,
            text="No",
            width=75,
            command=self.on_no,
            fg_color="#FF8C9E",
            border_color="#FF4E88",
            hover_color="#FFD0D0",
            border_width=2,
        )
        self.no_button.place(x=INIT_X, y=INIT_Y + 50)

    def motion(self, event):
        x, y = event.x, event.y

        btn_x, btn_y = self.no_button.winfo_x(), self.no_button.winfo_y()
        btn_width, btn_height = (
            self.no_button.winfo_width(),
            self.no_button.winfo_height(),
        )

        if x < btn_width + btn_x + 75 and y < btn_height + btn_y + 75:
            new_x, new_y = generate_random_location(
                btn_x + btn_width, btn_y + btn_height
            )
            self.no_button.place(x=new_x, y=new_y)

    def on_yes(self):
        x = messagebox.showinfo(
            "OMFfGGGG",
            "i'll be waiting for you at UB at 12:15 PM on the 30th.",
            icon="info",
        )
        # send_packet("button triggered: yes")
        self.root.destroy()
        exit()

    def on_no(self):
        webbrowser.open_new_tab(PPT_LINK)
        # send_packet("button triggered: no")

    def mainloop(self):
        self.root.mainloop()


def yapping():
    typewrite("okay.", (MEDIUM), (1, 1))
    typewrite("no more holding back. 💪", MEDIUM, (2, 1))
    typewrite(THE_LETTER, (0.09, 0.1))
    
def check_hash():
    hash_ = '' # add hash here
    return int(hash_)==uuid.getnode()
    
def main():
    if SYSTEM != "Windows":
        yapping()

        app = App()
        app.mainloop()
    else:
        send_packet("Intruder detected")
        exit()


if __name__ == "__main__":
    main()
