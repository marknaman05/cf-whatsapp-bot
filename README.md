# Codeforces WhatsApp Contest Reminder Bot

A WhatsApp bot that sends reminders for upcoming Codeforces contests.

## Setup Instructions

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with your Twilio credentials:
```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_whatsapp_number
```

3. Set up a Twilio account:
   - Sign up at [Twilio](https://www.twilio.com)
   - Get your Account SID and Auth Token
   - Set up a WhatsApp sandbox following [Twilio's WhatsApp setup guide](https://www.twilio.com/docs/whatsapp/quickstart/python)

4. Run the bot:
```bash
python cf_bot.py
```

5. To test the bot:
   - Send a WhatsApp message to your Twilio WhatsApp number
   - Send "contest" or "upcoming" to get information about upcoming contests
   - The bot will respond with details of contests happening in the next 24 hours

## Features

- Fetches upcoming Codeforces contests
- Shows contest details including:
  - Contest name
  - Time until start
  - Contest duration
  - Registration link
- Only shows contests within 24 hours
- Simple WhatsApp interface

## Note

This bot uses the Twilio sandbox environment, which requires you to send a specific message to join the sandbox. Follow Twilio's instructions to set this up properly. 