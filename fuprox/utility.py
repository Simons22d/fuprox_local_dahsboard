import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fuprox.models import Teller, TellerSchema, Service, ServiceOffered, ServiceOfferedSchema, Branch, BranchSchema, \
    Icon, IconSchema
from fuprox import db

# mpesa

teller_schema = TellerSchema()
tellers_schema = TellerSchema(many=True)

service_schema = ServiceOfferedSchema()
services_schema = ServiceOfferedSchema(many=True)

branch_schema = BranchSchema()
branchs_schema = BranchSchema(many=True)

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


def teller_exists(id):
    lookup = Teller.query.get(id)
    teller_data = teller_schema.dump(lookup)
    return teller_data


def branch_exists_id(id):
    return Branch.query.get(id)


def add_teller(teller_number, branch_id, service_name, branch_unique_id):
    # here we are going to ad teller details
    if len(service_name.split(",")) > 1:
        if services_exist(service_name, branch_id) and branch_exist(branch_id):
            # get teller by name
            if get_teller(teller_number, branch_id):
                final = dict(), 500
            else:
                lookup = Teller(teller_number, branch_id, service_name, branch_unique_id)
                db.session.add(lookup)
                db.session.commit()

                # update service_offered
                service_lookup = ServiceOffered.query.filter_by(name=service_name).filter_by(
                    branch_id=branch_id).first()
                service_lookup.teller = teller_number
                db.session.commit()

                final = teller_schema.dump(lookup)


        else:
            final = dict()
    else:
        if branch_exist(branch_id) and service_exists(service_name, branch_id):
            # get teller by name
            if get_teller(teller_number, branch_id):
                final = dict(), 500
            else:
                lookup = Teller(teller_number, branch_id, service_name, branch_unique_id)
                db.session.add(lookup)
                db.session.commit()

                data = teller_schema.dump(lookup)
                final = data

                service_lookup = ServiceOffered.query.filter_by(name=service_name).filter_by(
                    branch_id=branch_id).first()
                service_lookup.teller = teller_number
                db.session.commit()



        else:
            final = dict(), 500

    return final


def service_exists(name, branch_id):
    lookup = ServiceOffered.query.filter_by(name=name).filter_by(branch_id=branch_id).first()
    data = service_schema.dump(lookup)
    return data


def get_teller(number, branch_id):
    lookup = Teller.query.filter_by(number=number).filter_by(branch=branch_id).first()
    data = teller_schema.dump(lookup)
    return data


def services_exist(services, branch_id):
    holder = services.split(",")
    for item in holder:
        if not service_exists(item, branch_id):
            return False
    return True


def branch_exist(branch_id):
    lookup = Branch.query.get(branch_id)
    branch_data = branch_schema.dump(lookup)
    return branch_data


def create_service(name, teller, branch_id, code, icon_id, visible):
    branch_data = branch_exist(branch_id)
    if branch_data:
        log("branch exists")
        final = None
        if service_exists(name, branch_id):
            final = {"msg": "Error service name already exists", "status": None}
            log("Error service name already exists")
        else:
            log("service does not exist")
            if get_service_code(code, branch_id):
                final = {"msg": "Error Code already exists", "status": None}
                log("code exists")
            else:
                log("code does not exists")
                # check if icon exists for the branch
                # if icon_exists(icon_id, branch_id):
                icon = icon_name_to_id(icon_id)
                icon = Icon.query.get(icon)
                if icon:
                    log("icon exists")
                    try:
                        service = ServiceOffered(name, branch_id, teller, code, icon.id)
                        service.medical_active = True
                        if not visible:
                            service.medical_active = False
                        db.session.add(service)
                        db.session.commit()

                        log(service)
                        dict_ = dict()


                        # adding the ofline key so that we can have consitancy
                        key = {"key": branch_data["key_"]}
                        dict_.update(key)
                        dict_.update(service_schema.dump(service))
                        final = dict_
                        log("we are here")
                    except Exception as e:
                        final = {"msg": "Error service by that name exists"}
                        log("service exists")
    else:
        final = {"msg": "Service/Branch issue", "status": None}
    return final


def get_service_code(code, branch_id):
    lookup = ServiceOffered.query.filter_by(name=code).filter_by(branch_id=branch_id).first()
    data = service_schema.dump(lookup)
    return data


def log(msg):
    print(f"{datetime.now().strftime('%d:%m:%Y %H:%M:%S')} — {msg}")
    return True


def icon_name_to_id(name):
    icon = icon_exist_by_name(name)
    if icon:
        return icon.id
    return 1

def icon_exist_by_name(name):
    return Icon.query.filter_by(name=name).first()
