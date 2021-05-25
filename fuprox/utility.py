import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fuprox.models import Teller, TellerSchema, Service, ServiceOffered, ServiceOfferedSchema, Branch, BranchSchema, \
    Icon, IconSchema, Video, VideoSchema
from fuprox import db
from flask import jsonify, request
import sqlalchemy
from werkzeug.utils import secure_filename
import os
from fuprox import app

# mpesa

teller_schema = TellerSchema()
tellers_schema = TellerSchema(many=True)

service_schema = ServiceOfferedSchema()
services_schema = ServiceOfferedSchema(many=True)

branch_schema = BranchSchema()
branchs_schema = BranchSchema(many=True)

video_schema = VideoSchema()
videos_schema = VideoSchema(many=True)

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


def teller_exists(number):
    return Teller.query.filter_by(number=number).first()


def add_teller(teller_number, branch_id, service_name, branch_unique_id):
    branch = Branch.query.first()
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

                # adding the key
                final = teller_schema.dump(lookup)
                final.update({"key_": branch.key_})
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

                # adding the key
                final = teller_schema.dump(lookup)
                final.update({"key_": branch.key_})

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


def has_vowels(term):
    vowels = "aeiouAEIOU"
    l = [v for v in term if v in vowels]
    return False if len(l) else True


def create_service(name, teller, branch_id, code, icon_id, visible, active):
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
                log(icon)
                icon = Icon.query.get(int(icon))
                log(icon)
                if icon:
                    log("icon exists")
                    try:
                        service = ServiceOffered(name, branch_id, teller, code, icon.id)
                        service.medical_active = True
                        if not visible:
                            service.medical_active = False
                        if not active:
                            service.active = False

                        db.session.add(service)
                        db.session.commit()

                        log(service)
                        dict_ = dict()

                        # adding the ofline key so that we can have consitancy
                        key = {"key": branch_data["key_"]}
                        dict_.update(key)
                        dict_.update(service_schema.dump(service))
                        final = dict_
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
    return icon.id


def icon_exist_by_name(name):
    return Icon.query.filter_by(name=name).first()


"""
:::::::::::::::::::::::::::
:::::WORKING WITH VIDEO::::
:::::::::::::::::::::::::::

"""

ALLOWED_EXTENSIONS_ = set(["mp4", "mkv", "flv", "webm"])


def allowed_files_(filename):
    return filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_


# name.rsplit(".",1)[1] in ext

'''
encoding a base 64 string to mp4
'''


def final_html(message):
    return jsonify(message)


def upload_video():
    # check if the post request has the file part
    if 'file' not in request.files:
        return final_html("'No file part in the request")
    file = request.files['file']
    if file.filename == '':
        return final_html("No file selected for uploading")
    if file and allowed_files_(file.filename):
        try:
            # here wen need the file name
            filename = secure_filename(file.filename)
            # move the file to an appropriate location for play back
            # saving the video to the database
            video_lookup = Video(name=filename, type=1)
            db.session.add(video_lookup)
            db.session.commit()

            video_data = video_schema.dump(video_lookup)

            # do not save the file if there was an error
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # move the file to the appropriate location
            # try:
            #     time.sleep(10)
            #     move_video(file.filename)
            # except FileNotFoundError:
            #     return final_html("File Desination Error")

            return final_html("File successfully uploaded")
        except sqlalchemy.exc.IntegrityError:
            return final_html("Error! File by that name exists")
    else:
        return final_html("Allowed file types are mp4,flv,mkv")


def delete_video(video_id):
    vid = Video.query.get(int(video_id))
    db.session.delete(vid)
    db.session.commit()

    return video_schema.dump(vid)


def save_icon_to_service(icon, name, branch):
    try:
        try:
            icon_ = bytes(icon, encoding='utf8')
            lookup = Icon(name, branch, icon_)
            db.session.add(lookup)
            db.session.commit()

            final = {"msg": "Icon added succesfully", "status": 201}
        except sqlalchemy.exc.DataError:
            final = {"msg": "Icon size too large", "status": 500}
    except sqlalchemy.exc.IntegrityError:
        final = {"msg": f"Icon \"{name}\" Already Exists", "status": 500}
    return final


def upload():
    # check if the post request has the file part
    if 'file' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message': 'No file selected for uploading'})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        try:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        except FileNotFoundError:
            flash("file Not Found. Path Issue.", "warning")
        # adding to the database
        lookup = Icon(filename, 1)
        db.session.add(lookup)
        db.session.commit()

        resp = jsonify({'message': 'File successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify({'message': 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
        resp.status_code = 400
        return resp


def save_icon_to_service(icon, name, branch):
    try:
        try:
            icon_ = bytes(icon, encoding='utf8')
            lookup = Icon(name, branch, icon_)
            db.session.add(lookup)
            db.session.commit()

            final = {"msg": "Icon added succesfully", "status": 201}
        except sqlalchemy.exc.DataError:
            final = {"msg": "Icon size too large", "status": 500}
    except sqlalchemy.exc.IntegrityError:
        final = {"msg": f"Icon \"{name}\" Already Exists", "status": 500}
    return final


def upload_link(link, type):
    """
    :param link:
    :param type:
    :return:
    """
    try:
        video_lookup = Video(name=link.strip(), type=type)
        # print("local videos type",type)
        db.session.add(video_lookup)
        db.session.commit()

        video_data = video_schema.dump(video_lookup)
        return final_html({"msg": "Link successfully uploaded"})
    except sqlalchemy.exc.IntegrityError:
        return final_html({"msg": "Error! File by that name exists"})


def validate_link(link):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return {"valid": (re.match(regex, link) is not None)}


def save_mp4(data):
    random = secrets.token_hex(8)
    with open(f"{random}.mp4", "wb") as file:
        file.write(base64.b64encode(data))
        file.close()
        return ""
    return list()


def get_all_videos():
    lookup = Video.query.all()
    data = videos_schema.dump(lookup)
    return jsonify(data)


def get_single_video(id):
    lookup = Video.query.get(id)
    data = video_schema.dump(lookup)
    return data


def make_video_active(id):
    lookup = Video.query.get(id)
    lookup.active = 1
    db.session.commit()

    return video_schema.dump(lookup)


def make_video_inactive(id):
    lookup = Video.query.get(id)
    lookup.active = 0
    db.session.commit()

    return video_schema.dump(lookup)


def toggle_status(id):
    # get the video
    video = get_single_video(id)
    if video:
        final = make_video_inactive(video["id"]) if int(video["active"]) == 1 else make_video_active(video["id"])
    else:
        final = dict()
    return final


def get_active_videos():
    lookup = Video.query.filter_by(active=True).all()
    video_data = videos_schema.dump(lookup)
    new_list = [i.update({"link": app.config['UPLOAD_FOLDER']}) for i in video_data]
    return jsonify(video_data)


""":::::END:::::"""
