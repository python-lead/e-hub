#!/usr/bin/python
# -*- coding:utf-8 -*-
import datetime
import logging
import os
import sys
import tkinter as tk
import tkinter.font as tkfont

from PIL import Image, ImageDraw, ImageFont, ImageTk

static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "e-hub/static")
lib_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "e-hub/lib")

print(f"STATIC_DIR: {static_dir}")

if os.path.exists(lib_dir):
    sys.path.append(lib_dir)

ENVIRONMENT = os.environ.get("ENVIRONMENT")
SIMULATION = False  # if ENVIRONMENT == "rpi" else True

POWER_TASKS = [
    "› Dziennik",
    "› Trening|Spacer",
    "› Intensywna praca",
    "› 10k kroków",
    "",
]
POWER_BELIEFES = [
    "Nigdy nie narzekaj",
    "Przestań się tłumaczyć",
    "Przestań się usprawiedliwiać",
    "Dyscyplina = wolność",
]

COLOR_FRONT = "#363636"
COLOR_BACK = "#ececec"

logging.basicConfig(level=logging.DEBUG)

if SIMULATION:
    root = tk.Tk()

    font22 = tkfont.Font(family="Helvetica", size=22, weight="normal")
    font24 = tkfont.Font(family="Helvetica", size=24, weight="normal")
    font28 = tkfont.Font(family="Helvetica", size=28, weight="normal")
    font30 = tkfont.Font(family="Helvetica", size=30, weight="normal")
    font30bold = tkfont.Font(family="Helvetica", size=30, weight="bold")
else:
    import lib.epd7in5_V2

    font22bold = ImageFont.truetype(os.path.join(static_dir, 'Font.ttc'), 23)
    font22 = ImageFont.truetype(os.path.join(static_dir, 'Font.ttc'), 22)
    font24 = ImageFont.truetype(os.path.join(static_dir, 'Font.ttc'), 24)
    font28 = ImageFont.truetype(os.path.join(static_dir, 'Font.ttc'), 28)
    font30 = ImageFont.truetype(os.path.join(static_dir, 'Font.ttc'), 30)
    font30bold = ImageFont.truetype(os.path.join(static_dir, 'Font.ttc'), 31)


def motion(event):
    x, y = event.x, event.y
    print('{}, {}'.format(x, y))


def display_calendar():
    timestamp = get_date_from_ntp()
    display.write_text(
        10, 10, text=timestamp.strftime("%d"),
        font=font30bold
    )
    display.write_text(
        60, 15, text=timestamp.strftime("%b %Y - %A"),
        font=font30
    )


def display_powerlist():
    for i in range(5):
        display.write_text(10, 104 + i * 46, text=POWER_TASKS[i], font=font30)


def display_text(x, y, y_step, texts: list, font, color=None):
    for i in range(len(texts)):
        display.write_text(x, y + i * y_step, text=texts[i], font=font, color=color)


def get_date_from_ntp() -> datetime.datetime:
    try:
        client = ntplib.NTPClient()
        response = client.request('pool.ntp.org')
        return datetime.datetime.fromtimestamp(response.tx_time)
    except OSError:
        return datetime.datetime.now()


class DisplayService:
    def __init__(self, simulation: bool = True):
        self.simulation = simulation
        self.canvas = None
        self.e_canvas = None
        self.WIDTH = 800
        self.HEIGHT = 480

        if self.simulation:
            self._setup_for_simulation()
        else:
            self._setup_for_e_paper()

    def _setup_for_simulation(self):
        self.canvas = tk.Canvas(root, width=800, height=480, bg=COLOR_BACK)
        self.canvas.grid(row=2, column=3)

    def _setup_for_e_paper(self):
        logging.info("Sol e-hub poc demo")
        self.epd = epd7in5_V2.EPD()
        logging.info("init and Clear")
        self.epd.init()

        logging.info("Creating canvas")

        self.e_canvas = Image.new('1', (self.epd.width, self.epd.height), 255)  # 255: clear the frame

    def run(self) -> None:
        if self.simulation:
            self._run_simulation()
        else:
            self._run_epaper()

    def _run_simulation(self):
        root.bind('<Motion>', motion)
        root.mainloop()

    def _run_epaper(self):
        self.epd.display(self.epd.getbuffer(self.e_canvas))
        self.epd.sleep()

    def add_image(self, image: ImageTk.PhotoImage, x: int = 0, y: int = 0):
        if self.simulation:
            self.canvas.create_image(x, y, anchor=tk.NW, image=image)
        else:
            self.e_canvas.paste(image, (x, y))

    def write_text(self, x: int, y: int, text: str, font: ImageFont, color=None):
        x = x if x else 0
        y = y if y else 0

        if self.simulation:
            color = color if color else COLOR_FRONT
            self.canvas.create_text(x, y, text=text, font=font, fill=color, anchor='nw')
        else:
            color = color if color else 0
            draw = ImageDraw.Draw(self.e_canvas)
            draw.text((x, y), text=text, font=font, fill=color)


try:
    display = DisplayService(simulation=SIMULATION)

    # Images
    if SIMULATION:
        ui_image = ImageTk.PhotoImage(Image.open("static/ui-0.3.bmp"))
    else:
        ui_image = Image.open(os.path.join("static/ui-0.3.bmp"))
    display.add_image(ui_image)

    display_text(x=10, y=104, y_step=46, texts=POWER_TASKS, font=font30)
    display_text(x=10, y=340, y_step=33, texts=POWER_BELIEFES, font=font28, color=255)

    display.run()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd7in5_V2.epdconfig.module_exit()
    exit()
