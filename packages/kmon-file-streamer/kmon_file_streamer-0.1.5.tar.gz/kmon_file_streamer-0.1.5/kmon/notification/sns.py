from typing import Optional

from kmon.notification.notification_client import NotificationSender


class SNSNotificationSender(NotificationSender):
    def __init__(self, sns_client, sns_topic_arn: str, lambda_name: str):
        self.sns_client = sns_client
        self.sns_topic_arn = sns_topic_arn
        self.lambda_name = lambda_name

    def send(self, message: str, subject: Optional[str] = None) -> None:
        try:
            self.sns_client.publish(
                TopicArn=self.sns_topic_arn,
                Message=message,
                Subject=f'{subject} - {self.lambda_name}'
            )
        except Exception as e:
            print(f"Failed to send SNS notification: {str(e)}")