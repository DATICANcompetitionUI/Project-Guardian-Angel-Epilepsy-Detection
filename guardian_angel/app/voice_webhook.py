"""
Twilio Voice Webhook Handler
This is the IVR system that Twilio calls when someone dials your number
"""

import os
import json
import requests
from datetime import datetime
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)

# Firebase config - use same as your main app
FIREBASE_URL = "https://guardian-angel-b37a6-default-rtdb.firebaseio.com"

# ============================================
# HELPER FUNCTIONS
# ============================================

def find_user_by_phone(phone_number):
    """Find user in Firebase by phone number"""
    try:
        url = f"{FIREBASE_URL}/users.json?orderBy=%22phone%22&equalTo=%22{phone_number}%22"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                for uid, user_data in data.items():
                    return uid, user_data
        return None, None
    except:
        return None, None

def log_response(user_id, response, call_sid, caller_type):
    """Log user response to Firebase"""
    try:
        url = f"{FIREBASE_URL}/voice_checkins/{user_id}.json"
        data = {
            "timestamp": str(datetime.now()),
            "call_sid": call_sid,
            "response": response,
            "caller_type": caller_type,
            "date": str(datetime.now().date())
        }
        requests.post(url, json=data)
        return True
    except:
        return False

def send_caregiver_alert(user_id, user_name):
    """Send alert to caregivers (via existing SMS system)"""
    # This would call your existing SMS function
    print(f"🚨 ALERT: {user_name} needs help!")
    return True

# ============================================
# IVR WEBHOOK ENDPOINTS
# ============================================

@app.route("/voice_checkin", methods=["GET", "POST"])
def voice_checkin():
    """Entry point - identifies if caller is patient or caregiver"""
    response = VoiceResponse()
    caller_phone = request.form.get("From", "")
    
    response.say("Hello. This is Guardian Angel.")
    response.say("Are you the patient, or the caregiver?")
    response.say("Press 1 if you are the patient.")
    response.say("Press 2 if you are the caregiver.")
    
    gather = response.gather(
        num_digits=1,
        action="/identify_caller",
        method="POST",
        timeout=10
    )
    
    response.say("We didn't hear from you. Please try again later.")
    response.hangup()
    return str(response)

@app.route("/identify_caller", methods=["POST"])
def identify_caller():
    """Handle caller identification"""
    digits = request.form.get("Digits")
    caller_phone = request.form.get("From")
    call_sid = request.form.get("CallSid")
    
    if digits == "1":
        # Patient calling
        return patient_flow(caller_phone, call_sid)
    elif digits == "2":
        # Caregiver calling
        return caregiver_flow(caller_phone, call_sid)
    else:
        response = VoiceResponse()
        response.say("We didn't understand your response. Please try again.")
        response.hangup()
        return str(response)

def patient_flow(caller_phone, call_sid):
    """Flow for patients checking in"""
    response = VoiceResponse()
    
    # Find patient by phone
    user_id, user_data = find_user_by_phone(caller_phone)
    
    if user_data:
        patient_name = user_data.get("name", "User")
        response.say(f"Hello, {patient_name}. How are you feeling today?")
    else:
        response.say("Hello. How are you feeling today?")
    
    response.say("Press 1 if you are fine.")
    response.say("Press 2 if you need help.")
    
    gather = response.gather(
        num_digits=1,
        action="/patient_response",
        method="POST",
        timeout=10
    )
    
    response.say("We didn't hear from you. We will try again later.")
    response.hangup()
    return str(response)

def caregiver_flow(caller_phone, call_sid):
    """Flow for caregivers reporting on behalf of patient"""
    response = VoiceResponse()
    
    response.say("Please enter the patient's phone number using your keypad.")
    response.say("Press the hash key when done.")
    
    gather = response.gather(
        num_digits=11,
        action="/caregiver_patient",
        method="POST",
        timeout=15
    )
    
    response.say("We didn't get the phone number. Please try again.")
    response.hangup()
    return str(response)

@app.route("/patient_response", methods=["POST"])
def patient_response():
    """Handle patient's response (1 or 2)"""
    digits = request.form.get("Digits")
    caller_phone = request.form.get("From")
    call_sid = request.form.get("CallSid")
    
    response = VoiceResponse()
    
    # Find user
    user_id, user_data = find_user_by_phone(caller_phone)
    
    if digits == "1":
        response.say("You're safe. Thank you for checking in.")
        if user_id:
            log_response(user_id, "fine", call_sid, "patient")
    elif digits == "2":
        response.say("Help is on the way. Please stay on the line.")
        if user_id:
            log_response(user_id, "help", call_sid, "patient")
            # Trigger caregiver alert
            send_caregiver_alert(user_id, user_data.get("name", "User"))
    else:
        response.say("We didn't understand your response. We'll try again later.")
    
    response.hangup()
    return str(response)

@app.route("/caregiver_patient", methods=["POST"])
def caregiver_patient():
    """Handle caregiver entering patient phone number"""
    digits = request.form.get("Digits")
    caller_phone = request.form.get("From")
    call_sid = request.form.get("CallSid")
    
    response = VoiceResponse()
    
    # Find patient by the entered phone number
    user_id, user_data = find_user_by_phone(digits)
    
    if user_data:
        patient_name = user_data.get("name", "Patient")
        response.say(f"You are reporting for {patient_name}.")
        response.say("Press 1 to report a problem.")
        response.say("Press 2 to check their status.")
        
        gather = response.gather(
            num_digits=1,
            action="/caregiver_report",
            method="POST",
            timeout=10
        )
    else:
        response.say("We couldn't find that patient. Please try again.")
        response.hangup()
    
    return str(response)

@app.route("/caregiver_report", methods=["POST"])
def caregiver_report():
    """Handle caregiver's report"""
    digits = request.form.get("Digits")
    caller_phone = request.form.get("From")
    call_sid = request.form.get("CallSid")
    
    response = VoiceResponse()
    
    if digits == "1":
        response.say("Thank you for reporting. A caregiver will be notified immediately.")
        response.say("Help is on the way.")
        # Log as help request from caregiver
    elif digits == "2":
        response.say("Patient status is being checked. You will receive an update shortly.")
    else:
        response.say("We didn't understand your response. Please try again.")
    
    response.hangup()
    return str(response)

@app.route("/", methods=["GET"])
def health():
    return "✅ Guardian Angel Voice IVR is running!"

if __name__ == "__main__":
    app.run(debug=True, port=5000)