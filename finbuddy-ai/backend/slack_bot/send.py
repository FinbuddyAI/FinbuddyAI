import requests
import json
import argparse

def send_slack_message(webhook_url, message, channel=None, username=None, icon_emoji=None):
    """
    Send a message to a Slack channel
    
    Parameters:
        webhook_url (str): Slack Webhook URL
        message (str): Message content to send
        channel (str, optional): Target channel, e.g. "#general". Defaults to the channel set in Webhook
        username (str, optional): Sender name. Defaults to the name set in Webhook
        icon_emoji (str, optional): Sender avatar emoji, e.g. ":ghost:". Defaults to the avatar set in Webhook
    """
    payload = {
        "text": message
    }
    
    if channel:
        payload["channel"] = channel
    if username:
        payload["username"] = username
    if icon_emoji:
        payload["icon_emoji"] = icon_emoji
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers=headers
        )
        
        if response.status_code == 200:
            print("Message sent successfully!")
        else:
            print(f"Failed to send message, status code: {response.status_code}, response: {response.text}")
    except Exception as e:
        print(f"Error occurred while sending message: {str(e)}")

if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Send a message to Slack")
    parser.add_argument("--webhook", required=True, help="Slack Webhook URL")
    parser.add_argument("--message", required=True, help="Message content to send")
    parser.add_argument("--channel", help="Target Slack channel, e.g. '#general'")
    parser.add_argument("--username", help="Sender name")
    parser.add_argument("--icon", help="Sender avatar emoji, e.g. ':ghost:'")
    
    args = parser.parse_args()
    
    # Call the send function
    send_slack_message(
        webhook_url=args.webhook,
        message=args.message,
        channel=args.channel,
        username=args.username,
        icon_emoji=args.icon
    )