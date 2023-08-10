import random

def generate_otp():
    return str(random.randint(1000, 9999))  # Generate a 4-digit OTP

def send_otp(phone_number, otp):
    print(f"OTP for {phone_number}: {otp}")  # Replace with your actual SMS sending code