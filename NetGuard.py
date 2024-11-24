import os
import subprocess
import time
import threading
import smtplib
from email.mime.text import MIMEText
from plyer import notification
import winsound

# Email configuration
smtp_server = "smtp-relay.brevo.com"
smtp_port = 587
login_email = "rithwikreddy260@gmail.com"
login_password = "FHhjQdCGyzY9tZmB"  # Replace with a secure method to handle your password
recipient_email = "rithwikreddy260@gmail.com"

# List of IP addresses to ping
ip_addresses = ["192.168.1.8", "192.168.1.15"]
device_status = {ip: "Unknown" for ip in ip_addresses}
exit_event = threading.Event()  # Event to signal threads to exit gracefully

def clear_screen():
    """Clear the terminal screen."""
    print("\033[H\033[J", end="")  # ANSI escape code to clear screen

def display_status():
    """Display the IP and status of each device."""
    clear_screen()
    for ip in ip_addresses:
        print(f"{ip}: {device_status[ip]}")
    print("\nMonitoring... Press Ctrl+C to stop.")

def send_email(subject, message):
    """Send email notification."""
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = login_email
    msg["To"] = recipient_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(login_email, login_password)
            server.sendmail(login_email, recipient_email, msg.as_string())
            print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def play_alert_sound():
    """Play an alert sound."""
    winsound.Beep(1000, 500)  # Frequency 1000 Hz, duration 500 ms

def send_desktop_notification(title, message):
    """Send desktop notification."""
    notification.notify(title=title, message=message, timeout=10)

def ping_device(ip):
    """Ping the device and update its status in real-time."""
    previous_status = None  # Initialize the previous status to None

    while not exit_event.is_set():  # Check if exit event is set
        try:
            # Ping the IP and update status based on the response
            output = subprocess.check_output(["ping", "-n", "1", ip], stderr=subprocess.STDOUT, universal_newlines=True)
            new_status = "Online" if "TTL=" in output else "Offline"
        except subprocess.CalledProcessError:
            new_status = "Offline"

        # Send notifications only if the status has changed and is not the initial state
        if previous_status is not None and previous_status != new_status:
            status_change_message = f"Device {ip} is now {new_status}."
            if new_status == "Offline":
                informative_message = f"Alert: Device {ip} is offline.\nPrevious status: {previous_status}\nCurrent status: {new_status}\nPlease check the device."
                send_email(f"Alert: Device {ip} Offline", informative_message)
                send_desktop_notification("Device Alert", status_change_message)
                play_alert_sound()
            elif new_status == "Online":
                informative_message = f"Info: Device {ip} is back online.\nPrevious status: {previous_status}\nCurrent status: {new_status}\nYou can now access the device."
                send_email(f"Info: Device {ip} Online", informative_message)
                send_desktop_notification("Device Alert", status_change_message)
                play_alert_sound()
        
        device_status[ip] = new_status  # Update device status
        previous_status = new_status  # Update previous status
        display_status()  # Refresh display

        time.sleep(2)  # Wait 2 seconds before the next ping

def monitor_devices():
    """Create threads for monitoring devices."""
    display_status()  # Display initial IP statuses
    
    # Launch each ping in a separate thread
    threads = []
    for ip in ip_addresses:
        thread = threading.Thread(target=ping_device, args=(ip,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete (they won't, as they run indefinitely)
    for thread in threads:
        thread.join()

def main():
    """Main function to start monitoring devices."""
    print("Starting to monitor devices...")
    try:
        monitor_devices()
    except KeyboardInterrupt:
        exit_event.set()  # Set the event to stop threads gracefully
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    main()
