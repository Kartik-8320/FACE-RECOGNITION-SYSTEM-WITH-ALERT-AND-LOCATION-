import cv2
import face_recognition
import os
import numpy as np
from tkinter import *
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk, ImageDraw
import datetime
import webbrowser
import geocoder
import winsound
import pandas as pd
from joblib import load
import smtplib
from email.mime.text import MIMEText
import sys

clf = load("face_classifier.pkl")  # Load KNN model

# ------------------ Configuration ------------------
KNOWN_FACES_DIR = "known_faces"
TOLERANCE = 0.6
FRAME_THICKNESS = 3
FONT_THICKNESS = 2
MODEL = "hog"
LOG_FILE = "detections_log.csv"

# Email Configuration
EMAIL_SENDER = "sender112234@gmail.com"
EMAIL_PASSWORD = "saey iwoh ajwl haxs"
EMAIL_RECEIVER = "kartikvasandani@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# ------------------ Send Email Alert ------------------
def send_email_alert(name, lat, lng):
    maps_link = f"https://www.google.com/maps?q={lat},{lng}"
    body = f"🔍 Face Detected: {name}\n📍 Location: {maps_link}"
    msg = MIMEText(body)
    msg['Subject'] = f"GOD'S EYE ALERT: {name} detected"
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            print(f"[INFO] Email alert sent to {EMAIL_RECEIVER}")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")

# ------------------ Manual Email Alert Button ------------------
def send_manual_alert():
    name = "Manual Alert"
    coords = get_camera_location()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if coords:
        lat, lng = coords
        log_detection(name, timestamp, lat, lng)
        send_email_alert(name, lat, lng)
        messagebox.showinfo("Manual Alert", f"Manual alert sent for {name}\nLocation: {lat}, {lng}")
    else:
        messagebox.showerror("Error", "Unable to retrieve location.")

# ------------------ Splash Screen ------------------
from tkinter.ttk import Progressbar

def show_splash():
    splash = Tk()
    splash.overrideredirect(True)
    splash.configure(bg='#121212')
    splash.geometry('400x300+500+250')

    splash_title = Label(splash, text="GOD'S EYE", font=("Segoe UI", 24, "bold"), fg="#00e0ff", bg="#121212")
    splash_title.pack(pady=50)

    blink = True
    def blink_text():
        nonlocal blink
        splash_title.config(fg="#121212" if blink else "#00e0ff")
        blink = not blink
        global blink_id
        blink_id = splash.after(400, blink_text)

    blink_id = splash.after(400, blink_text)

    Label(splash, text="Initializing face recognition...", font=("Segoe UI", 12), fg="white", bg="#121212").pack(pady=10)
    progress = Progressbar(splash, orient=HORIZONTAL, length=250, mode='determinate')
    progress.pack(pady=20)

    def load_bar():
        for i in range(0, 101, 5):
            progress['value'] = i
            splash.update_idletasks()
            splash.after(50)
        splash.after_cancel(blink_id)
        splash.destroy()

    splash.after(100, load_bar)
    splash.mainloop()

show_splash()

# ------------------ (The rest of your code remains unchanged, continuing GUI setup and recognition logic) ------------------

# Add this button in your button frame setup (under "Buttons"):
Button(btn_frame, text="📨 Send Alert", command=send_manual_alert, bg="#6610f2", fg="white", **button_style).pack(side=LEFT, padx=10)
