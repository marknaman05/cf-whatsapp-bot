from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
from datetime import datetime
from pytz import timezone
import os

app = Flask(__name__)
IST = timezone('Asia/Kolkata')

def get_contests(show_all=False):
    try:
        response = requests.get('https://codeforces.com/api/contest.list', timeout=5)
        data = response.json()
        
        if data['status'] != 'OK':
            return "Error fetching contests"
            
        contests = []
        for contest in data['result']:
            if contest['phase'] == 'BEFORE':
                start_time = datetime.fromtimestamp(contest['startTimeSeconds'], tz=IST)
                time_until = start_time - datetime.now(IST)
                hours = time_until.total_seconds() / 3600
                
                if show_all or hours <= 24:
                    contest_info = (
                        f"🏆 {contest['name']}\n"
                        f"⏰ Start Time: {start_time.strftime('%d %b %Y, %I:%M %p IST')}\n"
                        f"⏳ Duration: {contest['durationSeconds']//3600} hours\n"
                        f"🔗 Register at: https://codeforces.com/contestRegistration/{contest['id']}\n"
                    )
                    contests.append(contest_info)
        
        if not contests:
            return "No upcoming contests found."
            
        return "\n\n".join(contests)
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)