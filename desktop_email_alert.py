import smtplib
import ssl
from email.message import EmailMessage
import datetime
import geocoder

# Email Configuration
SENDER_EMAIL = "sender112234@gmail.com"
APP_PASSWORD = "saey iwoh ajwl haxs"
RECEIVER_EMAIL = "kartikvasandani@gmail.com"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465


def get_camera_location():
    g = geocoder.ip('me')
    return g.latlng


def send_email_alert(name):
    coords = get_camera_location()
    if coords:
        lat, lng = coords
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        maps_link = f"https://www.google.com/maps?q={lat},{lng}"

        subject = f"Face Recognized: {name}"
        body = f"""
        A face has been recognized!

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


# Example usage:
# send_email_alert("Kartik")
