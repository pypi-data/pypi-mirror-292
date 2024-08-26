import json
from typing import Optional

import requests
import boto3

from kmon.notification.notification_client import NotificationSender


class SlackNotificationSender(NotificationSender):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send(self, message: str, subject: Optional[str] = None) -> None:
        payload = {'text': message}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.webhook_url, data=json.dumps(payload), headers=headers)
        if response.status_code != 200:
            print(f'Failed to send Slack notification. Status code: {response.status_code}')
            print(response.text)
        else:
            print("Slack notification sent successfully.")