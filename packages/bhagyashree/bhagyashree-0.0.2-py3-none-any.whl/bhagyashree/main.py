import math
import webbrowser
import random
from PIL import Image
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from pkg_resources import resource_filename    

APP_GEOMETRY = 350, 250
INIT_X, INIT_Y = 190, 134
ICON_FILE = resource_filename("bhagyashree", "assets/img/download.ico")
IMAGE_FILE = resource_filename("bhagyashree", "assets/img/5a8d70ce78bd7e2f015f9e6bfe36363e.png")

no_counter = 0


def generate_random_location(x, y):
    while 1:
        new_x = random.randint(0, APP_GEOMETRY[0] - 20)
        new_y = random.randint(0, APP_GEOMETRY[1] - 20)

        distance = math.sqrt((new_x - x) ** 2 + (new_y - y) ** 2)

        if distance >= 50:
            return new_x, new_y

    print("triggreresd")
    return new_x, new_y


def on_yes():
    x = messagebox.askyesno("AFKNFSKDFN", "OMMFGGGadfksdjfsijfdsfkjb really???!?!?")
    if x:
        x = messagebox.showinfo(
            "Info", "Meet me after the exams on 30th at 12:30 PM at UB.", icon="info"
        )
        root.destroy()
        exit()
    elif not x:
        webbrowser.open_new_tab(
            "https://docs.google.com/presentation/d/1fuPV1uLfZB_HH8MjK3J1Vka3V_IAZF1Pc3506uDC8rQ/pub?start=true&loop=true&delayms=3000"
        )


def on_no():
    messagebox.showerror("Error", "wha-")


def main():
    global root

    def motion(event):
        x, y = event.x, event.y

        btn_x, btn_y = no_button.winfo_x(), no_button.winfo_y()
        btn_width, btn_height = no_button.winfo_width(), no_button.winfo_height()

        if x < btn_width + btn_x + 200 and y < btn_height + btn_y + 200:
            new_x, new_y = generate_random_location(
                btn_x + btn_width, btn_y + btn_height
            )
            no_button.place(x=new_x, y=new_y)

    root = ctk.CTk()
    root.geometry(f"{APP_GEOMETRY[0]}x{APP_GEOMETRY[1]}")
    root.title(datetime.now().strftime("%d-%m-%Y"))
    root.bind("<Motion>", motion)
    root.resizable(False, False)
    root.iconbitmap(ICON_FILE)

    ctk.CTkLabel(
        root,
        text="",
        image=ctk.CTkImage(
            light_image=Image.open(
                IMAGE_FILE
            ),
            dark_image=Image.open(
                IMAGE_FILE
            ),
            size=(100, 100),
        ),
    ).place(x=INIT_X - 70, y=INIT_Y - 120)
    ctk.CTkLabel(root, text="will you go on a date with me?").place(
        x=INIT_X - 100, y=INIT_Y
    )
    ctk.CTkButton(
        root,
        text="Yes",
        width=75,
        command=on_yes,
    ).place(x=INIT_X - 100, y=INIT_Y + 50)

    no_button = ctk.CTkButton(
        root,
        text="No",
        width=75,
        command=on_no,
    )
    no_button.place(x=INIT_X, y=INIT_Y + 50)

    root.mainloop()


if __name__ == "__main__":
    main()
