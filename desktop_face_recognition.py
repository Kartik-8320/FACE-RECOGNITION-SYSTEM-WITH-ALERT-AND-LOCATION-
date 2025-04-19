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
import sys
import smtplib
import ssl
from email.message import EmailMessage
from joblib import load
from tkinter.ttk import Progressbar

# ------------------ Configuration ------------------
KNOWN_FACES_DIR = "known_faces"
TOLERANCE = 0.45
FRAME_THICKNESS = 3
FONT_THICKNESS = 2
MODEL = "hog"
LOG_FILE = "detections_log.csv"

# Email Configuration
SENDER_EMAIL = "sender112234@gmail.com"
APP_PASSWORD = "saey iwoh ajwl haxs"
RECEIVER_EMAIL = "kartikvasandani@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

# Load trained model
clf = load("face_classifier.pkl")

# ------------------ Email Alert ------------------
def get_camera_location():
    try:
        g = geocoder.ip('me')
        if g.ok and g.latlng:
            return g.latlng
    except Exception as e:
        print("[ERROR] Geolocation failed:", e)
    return None

def send_email_alert(name):
    coords = get_camera_location()
    if coords:
        lat, lng = coords
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        maps_link = f"https://www.google.com/maps?q={lat},{lng}"

        subject = f"Face Recognized: {name}"
        body = f"""A face has been recognized!

Name: {name}
Time: {timestamp}
Location: {maps_link}
"""

        msg = EmailMessage()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL
        msg["Subject"] = subject
        msg.set_content(body)

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
                server.login(SENDER_EMAIL, APP_PASSWORD)
                server.send_message(msg)
            print(f"[INFO] Email sent for {name}")
        except Exception as e:
            print(f"[ERROR] Could not send email: {e}")
    else:
        print("[WARNING] Could not retrieve camera location.")

# ------------------ Splash Screen ------------------
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

# ------------------ Load Known Faces ------------------
print("[INFO] Loading known faces...")
known_faces = []
known_names = []
if not os.path.exists(KNOWN_FACES_DIR):
    os.makedirs(KNOWN_FACES_DIR)

for name in os.listdir(KNOWN_FACES_DIR):
    person_dir = os.path.join(KNOWN_FACES_DIR, name)
    if os.path.isdir(person_dir):
        for filename in os.listdir(person_dir):
            image_path = os.path.join(person_dir, filename)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_faces.append(encodings[0])
                known_names.append(name)

# ------------------ GUI Setup ------------------
video = cv2.VideoCapture(0)
window = Tk()
window.title("GOD'S EYE")
window.geometry("1024x800")
window.configure(bg="#121212")

try:
    logo_img = Image.open("logo.jpg").resize((100, 100)).convert("RGBA")
    circle = Image.new('L', (100, 100), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, 100, 100), fill=255)
    logo_img.putalpha(circle)
    logo_photo = ImageTk.PhotoImage(logo_img)
    logo_label = Label(window, image=logo_photo, bg="#121212")
    logo_label.image = logo_photo
    logo_label.pack(pady=(10, 5))
except:
    print("[WARNING] Logo not found or failed to load.")

title_label = Label(window, text="GOD'S EYE", font=("Segoe UI", 28, "bold"), fg="#00e0ff", bg="#121212")
title_label.pack(pady=(0, 20))
def animate_title():
    current = title_label.cget("fg")
    title_label.config(fg="#00ffff" if current == "#00e0ff" else "#00e0ff")
    window.after(500, animate_title)
animate_title()

label = Label(window, bg="#1e1e1e", relief=RIDGE, bd=2)
label.pack(pady=10)
recognized_this_session = set()

# ------------------ Functional Helpers ------------------
def play_beep():
    winsound.Beep(1000, 150)

def save_face(name):
    ret, frame = video.read()
    if not ret: return
    path = os.path.join(KNOWN_FACES_DIR, name)
    os.makedirs(path, exist_ok=True)
    count = len(os.listdir(path)) + 1
    img_path = os.path.join(path, f"{count}.jpg")
    cv2.imwrite(img_path, frame)
    messagebox.showinfo("Saved", f"Saved face as {img_path}")
    window.after(1000, restart_app)

def restart_app():
    os.execl(sys.executable, sys.executable, *sys.argv)

def manage_faces():
    manager = Toplevel(window)
    manager.title("👤 Manage Faces")
    manager.configure(bg="#2c2c3c")
    row = 0
    for person in os.listdir(KNOWN_FACES_DIR):
        Label(manager, text=person, fg="white", bg="#2c2c3c", font=("Helvetica", 12)).grid(row=row, column=0, padx=10, pady=5)
        Button(manager, text="📝 Rename", bg="#007acc", fg="white", command=lambda p=person: rename_face(p)).grid(row=row, column=1)
        Button(manager, text="🗑️ Delete", bg="#e74c3c", fg="white", command=lambda p=person: delete_face(p)).grid(row=row, column=2)
        row += 1

def rename_face(old_name):
    new_name = simpledialog.askstring("Rename", f"Rename '{old_name}' to:")
    if new_name:
        os.rename(os.path.join(KNOWN_FACES_DIR, old_name), os.path.join(KNOWN_FACES_DIR, new_name))
        messagebox.showinfo("Renamed", f"Renamed to {new_name}")

def delete_face(name):
    if messagebox.askyesno("Delete", f"Delete all data for {name}?"):
        folder = os.path.join(KNOWN_FACES_DIR, name)
        for file in os.listdir(folder):
            os.remove(os.path.join(folder, file))
        os.rmdir(folder)
        messagebox.showinfo("Deleted", f"Deleted {name}")

def log_detection(name, time_str, lat, lng):
    df = pd.DataFrame([{'Name': name, 'Time': time_str, 'Latitude': lat, 'Longitude': lng}])
    if os.path.exists(LOG_FILE):
        df.to_csv(LOG_FILE, mode='a', header=False, index=False)
    else:
        df.to_csv(LOG_FILE, mode='w', header=True, index=False)

def show_map_prompt(lat, lng):
    if messagebox.askyesno("Open Location", "Do you want to open the matched person's location on Google Maps?"):
        webbrowser.open(f"https://www.google.com/maps?q={lat},{lng}")

def manual_alert():
    if recognized_this_session:
        last = list(recognized_this_session)[-1]
        send_email_alert(last)
    else:
        messagebox.showinfo("Info", "No recognized faces yet.")

# ------------------ Real-time Recognition ------------------
def update_frame():
    ret, frame = video.read()
    if not ret:
        return

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb, model=MODEL)
    face_encodings = face_recognition.face_encodings(rgb, face_locations)

    for face_encoding, face_location in zip(face_encodings, face_locations):
        probs = clf.predict_proba([face_encoding])[0]
        max_index = np.argmax(probs)
        confidence = probs[max_index] * 100

        if confidence >= 80:  # ✅ Only trust predictions above threshold
            match = clf.classes_[max_index]
        else:
            match = "Unknown"

        top, right, bottom, left = face_location
        color = (0, 255, 0) if match != "Unknown" else (0, 0, 255)
        label_text = f"{match} ({confidence:.1f}%)" if match != "Unknown" else "Unknown"

        # Draw rectangle and label
        cv2.rectangle(frame, (left, top), (right, bottom), color, FRAME_THICKNESS)
        cv2.putText(frame, label_text, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, FONT_THICKNESS)

        # ✅ Alert only for known faces not yet alerted in this session
        if match != "Unknown" and match not in recognized_this_session:
            play_beep()
            recognized_this_session.add(match)
            coords = get_camera_location()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if coords:
                lat, lng = coords
                log_detection(match, timestamp, lat, lng)
                show_map_prompt(lat, lng)
                send_email_alert(match)

    # Update GUI image
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    imgtk = ImageTk.PhotoImage(image=img)
    label.imgtk = imgtk
    label.configure(image=imgtk)

    # Update status
    if face_locations:
        status_var.set("🟢 Face Detected")
    else:
        status_var.set("🔵 Ready")

    window.after(10, update_frame)


# ------------------ Status & Controls ------------------
status_var = StringVar()
Label(window, textvariable=status_var, font=("Segoe UI", 10), fg="white", bg="#1e1e1e", anchor=W, relief=SUNKEN, bd=1).pack(fill=X, side=BOTTOM)
status_var.set("🔵 Ready")

btn_frame = Frame(window, bg="#121212")
btn_frame.pack(pady=15)
button_style = {"font": ("Segoe UI", 10, "bold"), "padx": 12, "pady": 8, "bd": 0, "relief": RAISED, "activebackground": "#1f1f1f", "cursor": "hand2"}

Button(btn_frame, text="📸 Capture", command=lambda: save_face(simpledialog.askstring("Name", "Enter name:")), bg="#28a745", fg="white", **button_style).pack(side=LEFT, padx=10)
Button(btn_frame, text="👤 Manage", command=manage_faces, bg="#17a2b8", fg="white", **button_style).pack(side=LEFT, padx=10)
Button(btn_frame, text="📍 Log File", command=lambda: os.startfile(LOG_FILE) if os.path.exists(LOG_FILE) else messagebox.showinfo("No Log", "No detections logged yet."), bg="#ffc107", fg="black", **button_style).pack(side=LEFT, padx=10)
Button(btn_frame, text="📧 Send Alert", command=manual_alert, bg="#6c63ff", fg="white", **button_style).pack(side=LEFT, padx=10)
Button(btn_frame, text="❌ Exit", command=window.destroy, bg="#dc3545", fg="white", **button_style).pack(side=LEFT, padx=10)

# ------------------ Run App ------------------
update_frame()
window.mainloop()
video.release()
cv2.destroyAllWindows()
