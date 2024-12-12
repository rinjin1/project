import time
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Slack bot token and channel configuration
SLACK_TOKEN = ""  # Replace with your Slack token
CHANNEL_ID = "C084FP4HC4D"  # Replace with your Slack channel ID

# Function to fetch recent messages from the channel
def fetch_recent_messages():
    url = f"https://slack.com/api/conversations.history?channel={CHANNEL_ID}"
    headers = {
        "Authorization": f"Bearer {SLACK_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        messages = response.json().get("messages", [])
        return messages
    else:
        logging.error(f"Failed to fetch messages: {response.text}")
        return []

# Function to post a response in a thread with interactive buttons
def post_thread_response_with_buttons(thread_ts):
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {SLACK_TOKEN}"
    }
    payload = {
        "channel": CHANNEL_ID,
        "thread_ts": thread_ts,
        "text": "Please select a service experiencing an issue:",
        "attachments": [
            {
                "text": "Select an option:",
                "fallback": "You are unable to choose an option",
                "callback_id": "service_selection",
                "color": "#3AA3E3",
                "attachment_type": "default",
                "actions": [
                    {
                        "name": "service",
                        "text": "Batch-Serving",
                        "type": "button",
                        "value": "batch-serving"
                    },
                    {
                        "name": "service",
                        "text": "Real-Time Services",
                        "type": "button",
                        "value": "real-time-services"
                    }
                ]
            }
        ]
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        logging.info("Response posted successfully in the thread.")
    else: 
        logging.error(f"Failed to post response: {response.text}")

# Function to log the selected option
def log_selected_option(payload):
    if 'actions' in payload and len(payload['actions']) > 0:
        selected_option = payload['actions'][0]['value']
        logging.info(f"User selected option: {selected_option}")

# Function to monitor a channel for new messages and respond in threads
def monitor_channel_and_respond():
    last_message_ts = None

    while True:
        messages = fetch_recent_messages()

        if messages:
            latest_message = messages[0]  # Assuming the latest message is at index 0
            latest_message_ts = latest_message.get("ts")

            if latest_message_ts != last_message_ts:
                logging.info(f"New message detected in the channel: {latest_message.get('text')}")
                post_thread_response_with_buttons(latest_message_ts)
                last_message_ts = latest_message_ts

        time.sleep(5)  # Check for new messages every 5 seconds

if __name__ == "__main__":
    monitor_channel_and_respond()
