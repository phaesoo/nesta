import boto3
import pickle


class SQSClient:
    def __init__(self, queue_url):
        self._queue_url = queue_url
        self._sqs = boto3.client('sqs')

    def send_message(self, data, message="None"):
        assert isinstance(data, dict)
        assert isinstance(message, str)

        self._sqs.send_message(
            QueueUrl=self._queue_url,
            MessageAttributes={
                'Data': {
                    'DataType': 'Binary',
                    'BinaryValue': pickle.dumps(data)
                },
            },
            MessageBody=(
                message
            )
        )

    def receive_message(self):
        response = self._sqs.receive_message(
            QueueUrl=self._queue_url,
            AttributeNames=[
                'SentTimestamp'
            ],
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=0,
            WaitTimeSeconds=0
        )

        messages = response.get('Messages')
        if messages is None:
            return None

        message = messages[0]
        return {
            "data": pickle.loads(message["MessageAttributes"]["Data"]["BinaryValue"]),
            "message": message["Body"],
            "receipt_handle": message["ReceiptHandle"]
        }

    def delete_message(self, receipt_handle):
        self._sqs.delete_message(
            QueueUrl=self._queue_url,
            ReceiptHandle=receipt_handle
        )
