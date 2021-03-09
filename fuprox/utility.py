import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# mpesa

import requests
from requests.auth import HTTPBasicAuth
from base64 import b64encode
from datetime import datetime

consumer_key = "vK3FkmwDOHAcX8UPt1Ek0njU9iE5plHG"
consumer_secret = "vqB3jnDyqP1umewH"


def authenticate():
    """
    :return: MPESA_TOKEN
    """
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(api_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    return response.text


def email(_to, subject, body):
    _from = "admin@fuprox.com"
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = _from
    message["To"] = _to

    # Turn these into plain/html MIMEText objects
    part = MIMEText(body, "html")
    # Add HTML/plain-text parts to MIMEMultipart message
    message.attach(part)
    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("mail.fuprox.com", 465, context=context) as server:
        server.login(_from, "Japanitoes")
        if server.sendmail(_from, _to, message.as_string()):
            return True
        else:
            return False


"""
Reverse for the mpesa API
"""


def reverse(transaction_id, amount, receiver_party):
    """

    :param access_token:
    :param initiator: This is the credential/username used to authenticate the transaction request.
    :param security_credential: Base64 encoded string of the M-Pesa short code and password, which is encrypted using M-Pesa public key and validates the transaction on M-Pesa Core system.
    :param transaction_id: Organization Receiving the funds.
    :param amount:
    :param receiver_party:
    :param remarks: comment to be sent with the transaction
    :param result_url:
    :param timeout_url:
    :return:
    """
    api_url = "https://sandbox.safaricom.co.ke/mpesa/reversal/v1/request"
    headers = {"Authorization": "Bearer %s" % authenticate()}
    request = {"Initiator": "testapi",  # test_api
               "SecurityCredential": "eOvenyT2edoSzs5ATD0qQzLj/vVEIAZAIvIH8IdXWoab0NTP0b8xpqs64abjJmM8+cjtTOfcEsKfXUYTmsCKp5X3iToMc5xTMQv3qvM7nxtC/SXVk+aDyNEh3NJmy+Bymyr5ISzlGBV7lgC0JbYW1TWFoz9PIkdS4aQjyXnKA2ui46hzI3fevU4HYfvCCus/9Lhz4p3wiQtKJFjHW8rIRZGUeKSBFwUkILLNsn1HXTLq7cgdb28pQ4iu0EpVAWxH5m3URfEh4m8+gv1s6rP5B1RXn28U3ra59cvJgbqHZ7mFW1GRyNLHUlN/5r+Zco5ux6yAyzBk+dPjUjrbF187tg==",
               "CommandID": "TransactionReversal",
               "TransactionID": transaction_id,  # this will be the mpesa code 0GE51H9MBP
               "Amount": amount,  # this has to be the exact amount
               "ReceiverParty": receiver_party,
               "RecieverIdentifierType": "11",  # was 4
               "ResultURL": "http://68.183.89.127:8080/mpesa/reversals",
               "QueueTimeOutURL": "http://68.183.89.127:8080/mpesa/reversals/timeouts",
               "Remarks": "Reverse for the transaction",
               "Occasion": "Reverse_Cash"
               }

    response = requests.post(api_url, json=request, headers=headers)
    print(response.text)
    return response.text
