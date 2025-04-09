from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from pytz import timezone

load_dotenv()

app = Flask(__name__)
IST = timezone('Asia/Kolkata')

def format_contest_info(contest, show_all=False):
    start_time = datetime.fromtimestamp(contest['startTimeSeconds'], tz=IST)
    time_until = start_time - datetime.now(IST)
    hours = time_until.total_seconds() / 3600
    
    if not show_all and hours > 24:
        return None
        
    contest_info = (
        f"🏆 {contest['name']}\n"
        f"⏰ Start Time: {start_time.strftime('%d %b %Y, %I:%M %p IST')}\n"
        f"⏳ Duration: {contest['durationSeconds']//3600} hours\n"
        f"🔗 Register at: https://codeforces.com/contestRegistration/{contest['id']}\n"
    )
    return contest_info

def get_contests(show_all=False):
    try:
        response = requests.get('https://codeforces.com/api/contest.list')
        contests = response.json()
        
        if contests['status'] != 'OK':
            return "Error fetching contests from Codeforces"
            
        upcoming_contests = []
        for contest in contests['result']:
            if contest['phase'] == 'BEFORE':
                contest_info = format_contest_info(contest, show_all)
                if contest_info:
                    upcoming_contests.append(contest_info)
        
        if not upcoming_contests:
            return "No upcoming contests found."
        
        return "\n\n".join(upcoming_contests)
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/webhook", methods=['POST'])
def webhook():
    try:
        incoming_msg = request.values.get('Body', '').lower()
        resp = MessagingResponse()
        msg = resp.message()
        
        if incoming_msg == 'next':
            contests_info = get_contests(show_all=False)
            msg.body(contests_info)
        elif incoming_msg == 'list':
            contests_info = get_contests(show_all=True)
            msg.body(contests_info)
        else:
            msg.body("Hi! I'm your Codeforces contest reminder bot.\n\nCommands:\n- 'next': Shows contests in next 24 hours\n- 'list': Shows all contests in next 7 days")
        
        return str(resp)
    except Exception as e:
        return str(e), 500

@app.route("/", methods=['GET'])
def home():
    return "Codeforces WhatsApp Bot is running!"

# This is required for Vercel
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)