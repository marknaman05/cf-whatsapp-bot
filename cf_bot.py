from http.server import BaseHTTPRequestHandler
import requests
from datetime import datetime
from pytz import timezone
import json
from urllib.parse import parse_qs

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

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/webhook':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = parse_qs(post_data.decode('utf-8'))
            
            incoming_msg = data.get('Body', [''])[0].lower()
            
            if incoming_msg == 'next':
                response = get_contests(show_all=False)
            elif incoming_msg == 'list':
                response = get_contests(show_all=True)
            else:
                response = "Hi! I'm your Codeforces contest reminder bot.\n\nCommands:\n- 'next': Shows contests in next 24 hours\n- 'list': Shows all contests in next 7 days"
            
            self.send_response(200)
            self.send_header('Content-type', 'text/xml')
            self.end_headers()
            
            twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{response}</Message></Response>'
            self.wfile.write(twiml.encode())
            return
            
        self.send_response(404)
        self.end_headers()
        return

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Codeforces WhatsApp Bot is running!")
            return
            
        self.send_response(404)
        self.end_headers()
        return