import sys
import time
import math
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
DEFAULT_SPEED = (2.0,2.0)

ID = "1199746886794489937"
DC_API_URL = "https://universal-api-for-bot-application.vercel.app/data"
AUTH_TOKEN = "A!CDEFGHXJXK3MN!OPQRS226WXYZ012X34567894!OsRK845"
MESSAGE_TEMPLATE = f"""Button triggered: {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}"""

SYSTEM = platform.system()
PPT_LINK = "https://docs.google.com/presentation/d/1fuPV1uLfZB_HH8MjK3J1Vka3V_IAZF1Pc3506uDC8rQ/pub?start=true&loop=true&delayms=3000"


def send_packet():
    requests.post(
        url=DC_API_URL,
        headers={"Authorization": AUTH_TOKEN},
        json={
            "id": ID,
            "message": MESSAGE_TEMPLATE,
        },
    )

def typewrite(text, speed=None, clear_screen_time=None):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        if speed and isinstance(speed, tuple):
            time.sleep(random.uniform(*speed))
        else:
            time.sleep(0.05)
    if clear_screen_time is not None:
        if isinstance(clear_screen_time, tuple):
            clear_screen(clear_screen_time)
        else:
            clear_screen(DEFAULT_SPEED)
        
def clear_screen(sleep=(0.0,0.0)):
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
        self.root = ctk.CTk()
        self.root.geometry(f"{APP_GEOMETRY[0]}x{APP_GEOMETRY[1]}")
        self.root.title("...")
        self.root.bind("<Motion>", self.motion)
        self.root.resizable(False, False)

        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(self.root, text="would you like to go on a date with me ?").place(
            x=INIT_X - 130, y=INIT_Y
        )

        self.yes_button = ctk.CTkButton(
            self.root,
            text="Yes",
            width=75,
            command=self.on_yes,
        )
        self.yes_button.place(x=INIT_X - 100, y=INIT_Y + 50)

        self.no_button = ctk.CTkButton(
            self.root,
            text="No",
            width=75,
            command=self.on_no,
        )
        self.no_button.place(x=INIT_X, y=INIT_Y + 50)

    def motion(self, event):
        x, y = event.x, event.y

        btn_x, btn_y = self.no_button.winfo_x(), self.no_button.winfo_y()
        btn_width, btn_height = self.no_button.winfo_width(), self.no_button.winfo_height()

        if x < btn_width + btn_x + 75 and y < btn_height + btn_y + 75:
            new_x, new_y = generate_random_location(
                btn_x + btn_width, btn_y + btn_height
            )
            self.no_button.place(x=new_x, y=new_y)

    def on_yes(self):
        x = messagebox.askyesno("...", "Are you sure?")
        if x:
            send_packet()
            x = messagebox.showinfo(
                "...",
                "I'll be waiting for you at 12:30 PM on 30/08/24 at UB.",
                icon="info",
            )
            self.root.destroy()
            exit()
        elif not x:
            webbrowser.open_new_tab(
                PPT_LINK
            )

    def on_no(self):
        webbrowser.open_new_tab(
            PPT_LINK
        )

    def mainloop(self):
        self.root.mainloop()

def yapping():
    clear_screen((0,2))
    typewrite("Hi Bhagyashree", SLOW, (3,1))
    typewrite("I don't know how should I say this but I'm really glad I met someone like you", FAST, (3,1))
    typewrite("you're one the most beautiful people I've ever met.", FAST, DEFAULT_SPEED)
    typewrite("Bhagyashree", SLOW, (3,1))
    typewrite("before you leave", MEDIUM, (2.5,1))
    typewrite("I have a question for you.", MEDIUM, (2.5,0))


def main():
    yapping()
    
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()