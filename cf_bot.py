from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from pytz import timezone
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Set timezone
IST = timezone('Asia/Kolkata')

def format_contest_info(contest, show_all=False):
    try:
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
    except Exception as e:
        logger.error(f"Error in format_contest_info: {str(e)}")
        return None

def get_contests(show_all=False):
    try:
        logger.info("Fetching contests from Codeforces API")
        response = requests.get('https://codeforces.com/api/contest.list', timeout=10)
        contests = response.json()
        
        if contests['status'] != 'OK':
            logger.error(f"Codeforces API error: {contests}")
            return "Error fetching contests from Codeforces"
            
        upcoming_contests = []
        for contest in contests['result']:
            if contest['phase'] == 'BEFORE':
                contest_info = format_contest_info(contest, show_all)
                if contest_info:
                    upcoming_contests.append(contest_info)
        
        if not upcoming_contests:
            logger.info("No upcoming contests found")
            return "No upcoming contests found."
        
        return "\n\n".join(upcoming_contests)
    except requests.exceptions.Timeout:
        logger.error("Timeout while fetching contests")
        return "Error: Timeout while fetching contests"
    except Exception as e:
        logger.error(f"Error in get_contests: {str(e)}")
        return f"Error: {str(e)}"

@app.route("/webhook", methods=['POST'])
def webhook():
    try:
        logger.info("Received webhook request")
        incoming_msg = request.values.get('Body', '').lower()
        logger.info(f"Received message: {incoming_msg}")
        
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
        
        logger.info("Sending response")
        return str(resp)
    except Exception as e:
        logger.error(f"Error in webhook: {str(e)}")
        return str(e), 500

@app.route("/", methods=['GET'])
def home():
    return "Codeforces WhatsApp Bot is running!"

# This is required for Vercel
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)