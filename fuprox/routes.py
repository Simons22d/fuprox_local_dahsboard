from flask import render_template, url_for, flash, redirect, request, abort, jsonify, send_file, send_from_directory
from fuprox import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required,current_user
from fuprox.forms import (RegisterForm, LoginForm, TellerForm, ServiceForm, SolutionForm, ReportForm, ActivateForm,PhraseForm)
from fuprox.models import User, Company, Branch, Service, Help, BranchSchema, CompanySchema, ServiceSchema, Mpesa, \
    MpesaSchema, Booking, BookingSchema, ImageCompany, ImageCompanySchema, Teller, TellerSchema,ServiceOffered,Icon,\
    IconSchema,PhraseSchema,Phrase,ServiceOfferedSchema, VideoSchema,Video
from fuprox.utility import reverse,add_teller,services_exist,services_exist,branch_exist,create_service,upload_video,\
    get_single_video,get_all_videos, get_active_videos, save_mp4, make_video_active,make_video_inactive,\
    toggle_status,validate_link,upload_link,delete_video,save_icon_to_service
import tablib
from datetime import datetime
import time
from PIL import Image

from datetime import datetime
import secrets
import socketio
from fuprox.utility import email
from flask_sqlalchemy import sqlalchemy
import os
import logging
import requests
teller_schema = TellerSchema()
tellers_schema = TellerSchema(many=True)


socket_link = "http://localhost:5000/"
# socket_link = "http://159.65.144.235:5000/"
local_socket = "http://localhost:5500/"

sio = socketio.Client()
local = socketio.Client()

# rendering many route to the same template
branch_schema = BranchSchema()

service_schema = ServiceSchema()
services_schema = ServiceSchema(many=True)

service_offered_schema = ServiceOfferedSchema()
services_offered_schema = ServiceOfferedSchema(many=True)

company_schema = CompanySchema()

mpesa_schema = MpesaSchema()
mpesas_schema = MpesaSchema(many=True)

bookings_schema = BookingSchema(many=True)

comapny_image_schema = ImageCompanySchema()
comapny_image_schemas = ImageCompanySchema(many=True)

videos_schema =VideoSchema(many=True)

phrase_schema = PhraseSchema()

def get_part_of_day(hour):
    return (
        "morning" if 5 <= hour <= 11
        else
        "afternoon" if 12 <= hour <= 17
        else
        "evening"
    )



from datetime import datetime

time = int(datetime.now().strftime("%H"))


@app.route("/")
@app.route("/dashboard")
@login_required
def home():
    # date
    date = datetime.now().strftime("%A, %d %B %Y")
    # report form
    bookings = len(Booking.query.all())
    tellers = len(Teller.query.all())
    service_offered = len(ServiceOffered.query.all())
    videos  = len(videos_schema.dump(Video.query.all()))
    dash_data = {
        "bookings" : f"{bookings} {'booking' if bookings == 1 else 'Bookings'}" if bookings else "No Bookings" ,
        "tellers" : f"{tellers} {'Teller' if tellers <= 1 else 'Tellers'}" if tellers else "No Tellers",
        "services" : f"{service_offered} {'Service' if service_offered <= 1 else 'Services'}" if service_offered else
        "No Services",
        "statement" : get_part_of_day(time).capitalize(),
        "user" : (current_user.username).capitalize(),
        "video" : f"{videos} {'Video' if tellers <= 1 else 'Videos'}" if tellers else "No Videos"
    }
    branch = Branch.query.first()
    log(dash_data)
    return render_template("dashboard.html", today=date,dash_data = dash_data,branch=branch)

@app.route("/doughnut/data", methods=["GET"])
def _doughnut_data():
    open_lookup = Booking.query.filter_by(serviced=False).all()
    open_data = bookings_schema.dump(open_lookup)
    closed_lookup = Booking.query.filter_by(serviced=True).all()
    closed_data = bookings_schema.dump(closed_lookup)

    return jsonify({"open": len(open_data), "closed": len(closed_data)})


@app.route("/bar/data", methods=["GET"])
def last_fifteen_data():
    data = get_issue_count()
    return jsonify(data["result"])


file_name = str()
dir = str()


@app.route("/video/link", methods=["POST"])
def upload_link_():
    link_ = request.json["link"]
    type_ = request.json["type"]
    return upload_link(link_, type_)


@app.route("/dashboard/reports", methods=["POST"])
def daily():
    secrets.token_hex()
    duration = request.json["duration"]  # daily monthly
    kind = request.json["kind"]  # booking / branch
    date = request.json["date"]  # date
    print(duration, date, kind)
    # getting the current path

    # FILE BASED REPORTS
    # import os
    # global file_name,dir
    #
    # # file_name = f"{int(datetime.timestamp(datetime.now()))}_report..xlsx"
    # file_name = "report.xlsx"
    # dir = os.path.join(os.getcwd(),"fuprox","reports")
    # root_file = os.path.join(dir,file_name)
    # # TEST
    # headers = ("firstname","lastname")
    # data = [("Denis", "Wambui"), ("Mark", "Kiruku")]
    # data_ = tablib.Dataset(*data, headers=headers)
    # with open(root_file, 'wb') as f:
    #     f.write(data_.export('xlsx'))
    # # send_file(file)

    booking_data = list()
    if duration and kind and date:
        print(kind, date, duration)
        kind_ = 1001 if kind == 0 else 2001
        duration_ = 1001 if duration == 'day' else 2001
        if duration_ == 1001:
            print("1001")
            # daily
            date = "%{}%".format(date)
            print(date)
            lookup = Booking.query.filter(Booking.date_added.like(date)).all()
            booking_data = bookings_schema.dump(lookup)
        else:
            print("2001")
            # monthly
            date_ = date.split("-")
            print(f"{date_[0]}-{date_[1]}")
            date = f"{date_[0]}-{date_[1]}"
            date = "%{}%".format(date)
            print(date)
            lookup = Booking.query.filter(Booking.date_added.like(date)).all()
            booking_data = bookings_schema.dump(lookup)
    return jsonify(booking_data)


'''mpesa report '''


@app.route("/mpesa/reports", methods=["POST"])
def mpesa_reports():
    kind = request.json["kind"]
    if int(kind) == 1:
        lookup = Mpesa.query.filter(Mpesa.amount.contains(5.0)).all()
    elif int(kind) == 2:
        lookup = Mpsa.query.filter(Mpesa.amount.contains(10.0)).all()
    elif int(kind) == 3:
        lookup = Mpesa.query.all()
    return jsonify(mpesas_schema.dump(lookup))


"""
function to get issue count >>>>
"""


def get_issue_count():
    data = db.session.execute("SELECT COUNT(*) AS issuesCount, DATE (date_added) AS issueDate FROM booking GROUP BY "
                              "issueDate LIMIT 15")
    return {'result': [dict(row) for row in data]}


"""
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::working with all forms of payments linking to the database::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
"""


@app.route("/bookings")
@login_required
def payments():
    bookings = Booking.query.all()
    return render_template("payment.html", bookings=bookings)


@app.route("/reverse", methods=["POST"])
def reverse_():
    """ PARAMS
    'Initiator' => 'testapi',
    'SecurityCredential' => 'eOvenyT2edoSzs5ATD0qQzLj/vVEIAZAIvIH8IdXWoab0NTP0b8xpqs64abjJmM8+cjtTOfcEsKfXUYTmsCKp5X3iToMc5xTMQv3qvM7nxtC/SXVk+aDyNEh3NJmy+Bymyr5ISzlGBV7lgC0JbYW1TWFoz9PIkdS4aQjyXnKA2ui46hzI3fevU4HYfvCCus/9Lhz4p3wiQtKJFjHW8rIRZGUeKSBFwUkILLNsn1HXTLq7cgdb28pQ4iu0EpVAWxH5m3URfEh4m8+gv1s6rP5B1RXn28U3ra59cvJgbqHZ7mFW1GRyNLHUlN/5r+Zco5ux6yAyzBk+dPjUjrbF187tg==',
    'CommandID' => 'TransactionReversal',
    'TransactionID' => 'NGE51H9MBP',
    'Amount' => '800',
    'ReceiverParty' => '600211',
    'RecieverIdentifierType' => '11',
    'ResultURL' => 'http://7ee727a4.ngrok.io/reversal/response.php',
    'QueueTimeOutURL' => 'http://7ee727a4.ngrok.io/reversal/response.php',
    'Remarks' => 'ACT_001',
    'Occasion' => 'Reverse_Cash'
    """
    id = request.json["id"]
    data = get_transaction(id)
    transaction_id = data["receipt_number"]
    amount = data["amount"]
    receiver_party = data["phone_number"]
    return reverse(transaction_id, amount, receiver_party)


def get_transaction(id):
    lookup = Mpesa.query.get(id)
    return mpesa_schema.dump(lookup)



@app.route('/service/icon/upload', methods=['POST'])
def upload_file():
    # print(request.data)
    return upload()

@app.route('/service/icon', methods=['POST'])
def upload_file_():
    icon = request.json["icon"]
    name = request.json["name"]
    # branch_id = request.json["branch_id"]
    branch_id = Branch.query.first().id
    current = save_icon_to_service(icon, name, branch_id)
    return current



@app.route("/card")
@login_required
def payments_card():
    # get date from the database 
    lookup = Mpesa.query.all()
    data = mpesas_schema.dump(lookup)
    # print("><>>>>>XX>>XXXXX")
    # print("mpesa", data)
    # work on the payments templates
    return render_template("payment_card.html", transactions=data)


@app.route("/reports")
@login_required
def payments_report():
    # work on the payments templates
    return render_template("payments_reports.html")


@app.route("/tellers", methods=["POST", "GET"])
@login_required
def tellers():
    # get data from the database
    tellers_ = Teller.query.all()
    # init the form
    teller = TellerForm()
    services = ServiceOffered.query.all()
    if teller.validate_on_submit():
        # get specific compan data
        if not teller_exists(teller.number.data):
            key_ = secrets.token_hex();
            teller_number = teller.number.data
            branch_id = Branch.query.first().id
            service_name = teller.service.data
            # status = True if teller.active.data == "True" else False
            try:
                branch = branch_exists_id(branch_id)
                final = add_teller(teller_number, branch_id, service_name, branch.unique_id)
                sio.emit("add_teller", {"teller_data": final})
            except Exception:
                print("error! teller exists")
            return redirect(url_for("tellers"))
        else:
            flash("Teller Already exists.", "danger")
    return render_template("add_branch.html", form=teller, services=services ,tellers=tellers_)


def branch_exists_id(id):
    return Branch.query.get(id)


def teller_exists(teller_number):
    lookup = Teller.query.filter_by(number=teller_number).first()
    teller_data = teller_schema.dump(lookup)
    return teller_data


""" not recommemded __check if current branch is in db"""

def log(msg):
    print(f"{datetime.now().strftime('%d:%m:%Y %H:%M:%S')} — {msg}")
    return True

def branch_exits(name):
    lookup = Branch.query.filter_by(name=name).first()
    branch_data = branch_schema.dump(lookup)
    return branch_data


# mpesa more info
@app.route("/info/<string:key>")
def more_info(key):
    print("key", key)
    lookup = Mpesa.query.get(key)
    data = mpesa_schema.dump(lookup)
    return render_template("info.html", data=data)


@app.route("/video/upload", methods=["POST"])
def upload_video_():
    return upload_video()



# @app.route("/video/link", methods=["POST"])
# def upload_link_():
#     link_ = request.json["link"]
#     type_ = request.json["type"]
#     return upload_link(link_, type_)
#

# get single video
@app.route("/video/get/one", methods=["POST"])
def get_one_video_():
    id = request.json["id"]
    return get_single_video(id)


@app.route("/video/active", methods=["POST"])
def get_active():
    return get_active_videos()


@app.route("/video/get/all", methods=["POST"])
def get_all_videos_():
    return get_all_videos()


@app.route("/video/toggle", methods=["POST"])
def activate_video():
    id = request.json["id"]
    return toggle_status(id)


@app.route("/video/delete", methods=["POST"])
def video_delete():
    vid_id = request.json["id"]
    return jsonify(delete_video(vid_id))



@app.route("/upload", methods=["POST", "GET", "PUT"])
def upload_video__():
    return render_template("upload.html")


@app.route("/icons", methods=["POST", "GET", "PUT"])
def upload_icon():
    icons = Icon.query.all()
    return render_template("icon.html",icons=icons)

# view_branch
@app.route("/teller/view")
@login_required
def view_branch():
    # get data from the database
    branches_data = Branch.query.all()
    company = ServiceForm()
    return render_template("view_branch.html", form=company, data=branches_data)


@app.route("/branches/category")
@app.route("/branches/category/add", methods=["POST", "GET"])
@login_required
def add_category():
    company = ServiceForm()
    # checkinf the mentioed  comapany exists
    if company.validate_on_submit():
        final = bool()
        # medical
        if company.is_medical.data == "True":
            final = True
        else:
            final = False
        try:
            data = Service(company.name.data, company.service.data, final)
            db.session.add(data)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            flash(f"Category By That Name Exists", "warning")
        # adding a category
        sio.emit("category", service_schema.dump(data))
        company.name.data = ""
        company.service.data = ""
        db.session.close()
        flash(f"Service Successfully Added", "success")
    else:
        flash("Error! Make Sure all data is correct","error")
    return render_template("add_category.html", form=company)





def move_to_api(filename):
    from pathlib import Path
    import shutil
    home = str(Path.home())
    from_ = os.path.join(app.root_path, "icons", filename)
    upload_path = os.path.join(home, "fuprox_api", "fuprox", "icons", filename)
    upload_pth = os.path.join(home, "fuprox_api", "fuprox", "icons")
    if not os.path.exists(f"{home}/fuprox_api/fuprox/icons"):
        try:
            new_dir = Path(upload_path)
            new_dir.mkdir(parents=True)
            shutil.move(from_, upload_pth)
            logging.info("Success! creating a directory.")
            return "Direcroty Created Successfully."
        except OSError:
            logging.info("Error! creating a directory.")
            return "Error! creating a directory."
    else:
        shutil.move(from_, upload_path)


def ticket_unique() -> int:
    return secrets.token_hex(16)


def save_picture(picture):
    pic_name = secrets.token_hex(8)
    # getting the name and the extension of the image
    _, ext = os.path.splitext(picture.filename)
    final_name = pic_name + ext
    picture_path = os.path.join(app.root_path, "icons", final_name)
    # resizing the file
    size = (125, 125)
    i = Image.open(picture)
    i.thumbnail(size)
    # saving the thumbnail
    i.save(picture_path)
    move_to_api(final_name)
    return final_name


@app.route("/service", methods=["POST", "GET"])
@login_required
def add_company():
    service_data = Service.query.all()
    # init the form
    service = ServiceForm()
    tellers = Teller.query.all()
    icons = Icon.query.all()
    branch = Branch.query.first()
    services_offered = ServiceOffered.query.all()

    if request.method == "POST":
        if service.validate_on_submit():
            name = service.name.data
            teller = service.teller.data
            branch_id = branch.id
            code = service.code.data
            icon = service.icon.data
            visible = True if service.visible.data == "True" else False
            # service emit service made
            final = create_service(name, teller, branch_id, code, icon, visible)
            if final:
                try:
                    key = final["key"]
                    flash("Service Added Successfully", "success")
                    sio.emit("sync_service", final)
                    local.emit("update_services", final)
                except KeyError :
                    flash(final['msg'],"danger")
        else:
            flash("Make sure all data is correct", "error")
    return render_template("add_company.html", form=service, companies=service_data, tellers=tellers,icons=icons,
                           services_offered = services_offered)


@app.route("/services/view")
@login_required
def view_company():
    # get the branch data
    company_data = Company.query.all()
    # init the form
    branch = TellerForm()
    return render_template("view_company.html", form=branch, data=company_data)


@app.route("/branches/category/view")
@login_required
def view_category():
    # category data
    service_data = Service.query.all()
    # init the form
    branch = TellerForm()
    return render_template("view_category.html", form=branch, data=service_data)


@app.route("/help", methods=["GET", "POST"])
def help():
    solution_data = Help.query.all()
    return render_template("help.html", data=solution_data)


@app.route("/extras",methods=["GET","POST"])
@login_required
def extras():
    current = Branch.query.first()
    form  = ActivateForm()
    phrase = Phrase.query.first()
    default = "Proceed to counte number"
    phrase = ( phrase.phrase if phrase.phrase else default) if  phrase else default
    # ss = PhraseForm()
    current_phrase = Phrase.query.first()
    if request.method == "POST":
        if form.validate_on_submit() and form.submit.data:
            key = form.key.data
            if len(key) > 20:
                try:
                    data = requests.post(f"http://159.65.144.235:4000/branch/activate", json={"key": key})
                    if (data.json["msg"]):
                        activate_branch(data.json())
                        flash("Success! Applcations Activated", "success")
                        return redirect(url_for("home"))
                    else:
                        flash("Error! Please confirm the key", "Warning")
                        return redirect(url_for("extras"))
                except requests.exceptions.ConnectionError:
                    flash("Error! Activatation Server Not Reachable", "danger")
            else:
                # flash("Error! Database not empty. Data was cleared", "warning")
                flash("Error! Key too short", "danger")
    return render_template("extras.html",branch=current,form=form,current_phrase=current_phrase, phrase=phrase)


@app.route("/reset/tickets",methods=["POST"])
def reset_tickets():
    req = request.post("http://159.65.144.235:4000/ticket/reset")

@app.route("/phrase", methods=["POST"])
def re():
    phrase = request.json["phrase"]
    option = request.json["options"]
    db.session.execute("DELETE FROM phrase")
    is_teller = True if int(option) == 1 else False
    lookup = Phrase(phrase, is_teller)
    db.session.add(lookup)
    db.session.commit()
    return jsonify(phrase_schema.dump(lookup))


@app.route("/this/branch",methods=["POST"])
def this_branch():
    return jsonify(branch_schema.dump(Branch.query.first()))


def activate_branch(data):
    if data:
        if data["service"] and data["branch"] and data["company"]:
            if  not there_are_bookings():
                try:
                    branch = data["branch"]
                    service = data["service"]
                    company = data["company"]
                    prepare_db(branch["key_"])

                    add_service(service["name"],service["service"],service["is_medical"])
                    add_company(company["name"],company["service"])
                    add_branch(branch["name"],branch["company"],branch["longitude"],branch["latitude"],branch["opens"],
                               branch["closes"],branch["service"],branch["description"],branch["key_"],branch["unique_id"])
                except sqlalchemy.exc.InvalidRequestError as e :
                    log(f"Error! {e}")
            else:
                log("Database ned to cleared. There are bookings there already")
                return {"msg" : "Database need to cleared. There are booking there already."}
        else:

            return {'msg' : "Data incomplete"},500
    else:
        return {"msg" : "Error! Key is invalid"}


def there_are_bookings():
    bookings = Booking.query.all()
    return bookings
def prepare_db(key):
    bookings = there_are_bookings()
    if not bookings:
        try:
            branch = Branch.query.filter_by(key_=key).first()
            if branch:
                company = Company.query.filter_by(name=branch.company).first()
                if company:
                    service = Service.query.filter_by(name=branch.service).first()
                    db.session.delete(branch)
                    db.session.commit()
                    db.session.delete(company)
                    db.session.commit()
                    db.session.delete(service)
                else:
                    log("service issue")
            else:
                log("service issue")
        except sqlalchemy.exc.InvalidRequestError as e:
            log("your DB Need upkeep. it is not empty")
        finally:
            log("errors")
    else:
        log("Error, database is not empty still has some bookings")


def branch_exists(name):
    lookup = Branch.query.filter_by(name=name).first()
    print("branch_data", branch_schema.dump(lookup))
    return [1] if lookup else []


def add_branch(name, company, longitude, latitude, opens, closes, service, description, key_, unique_id):
    if branch_exists_():
        db.session.execute("DELETE FROM branch")

    if not branch_exists(name):
        lookup = Branch(name, company, longitude, latitude, opens, closes, service, description, key_, unique_id)
        try:
            db.session.add(lookup)
            db.session.commit()
            return dict()
        except sqlalchemy.exc.IntegrityError as e:
            print("Error! Could not create Branch.")
            return dict()
    else:
        return dict()



def add_company(name, service):
    if company_exists():
        db.session.execute("DELETE FROM company")

    lookup = Company(name, service)
    try:

        db.session.add(lookup)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        print("error! already copied")
    lookup_data = company_schema.dump(lookup)
    return lookup_data

def service_exists():
    return Service.query.first()

def branch_exists_():
    return Branch.query.first()

def company_exists():
    return Company.query.first()

def add_service(name, service, is_medical):
    if service_exists():
        db.session.execute("truncate icon")
        db.session.execute("truncate teller")
        db.session.execute("DELETE from service_offered")
        db.session.execute("DELETE from branch")
        db.session.execute("DELETE from company")
        db.session.execute("DELETE FROM booking")
        db.session.execute("DELETE FROM service")
    lookup = Service(name, service, is_medical)
    try:
        db.session.add(lookup)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        print("error! record exists")
    return service_schema.dump(lookup)



@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    # loading the form
    login = LoginForm()
    # checking the form data status
    if login.validate_on_submit():
        print("form_data", login.email.data, login.password.data)
        user = User.query.filter_by(email=login.email.data).first()
        print("user_data", user)
        if user and bcrypt.check_password_hash(user.password, login.password.data):
            next_page = request.args.get("next")
            login_user(user)
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash("Login unsuccessful Please Check Email and Password", "danger")
    return render_template("login.html", form=login)

print(current_user)
@app.route("/register", methods=["GET", "POST"])
# @login_required
def register():
    # checking if the current user is logged
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    register = RegisterForm()
    if register.validate_on_submit():
        # hashing the password
        hashed_password = bcrypt.generate_password_hash(register.password.data).decode("utf-8")
        # adding the password to the database
        try:
            user = User(username=register.username.data, email=register.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            db.session.close()
        except sqlalchemy.exc.IntegrityError:
            flash("User By That Username Exists", "warning")
        flash(f"Account Created successfully", "success")
        return redirect(url_for('login'))
    return render_template("register.html", form=register)


# new ]
@app.route("/download/book/mac", methods=["GET"])
def book_mac():
    return send_from_directory("uploads/apps", "book_mac.zip", as_attachment=True)


@app.route("/download/book/windows", methods=["GET"])
def book_win():
    return send_from_directory("uploads/apps", "book_windows.zip",
                               as_attachment=True)


@app.route("/download/book/linux", methods=["GET"])
def book_lin():
    return send_from_directory("uploads/apps", "book_linux.zip", as_attachment=True)


@app.route("/download/teller/mac", methods=["GET"])
def teller_mac():
    return send_from_directory("uploads/apps", "teller_mac.zip", as_attachment=True)


@app.route("/download/teller/windows", methods=["GET"])
def teller_win():
    return send_from_directory("uploads/apps", "teller_windows.zip",
                               as_attachment=True)


@app.route("/download/teller/linux", methods=["GET"])
def teller_lin():
    return send_from_directory("uploads/apps", "teller_linux.zip",
                               as_attachment=True)


@app.route("/download/display/mac", methods=["GET"])
def display_mac():
    return send_from_directory("uploads/apps", "display_mac.zip", as_attachment=True)


@app.route("/download/display/windows", methods=["GET"])
def display_win():
    return send_from_directory("uploads/apps", "display_windows.zip", as_attachment=True)


@app.route("/download/display/linux", methods=["GET"])
def display_linux():
    return send_from_directory("uploads/apps", "display_linux.zip", as_attachment=True)


@app.route("/download/app", methods=["GET"])
def mobile_app():
    return send_from_directory("uploads/apps", "fuprox.apk", as_attachment=True)


''' working with users'''


@app.route("/extras/users/add", methods=["GET", "POST"])
@login_required
def add_users():
    # getting user data from the database
    user_data = User.query.all()
    # return form to add a user
    register = RegisterForm()
    if register.validate_on_submit():
        # hashing the password
        hashed_password = bcrypt.generate_password_hash(register.password.data).decode("utf-8")
        # adding the password to the database
        try:
            user = User(username=register.username.data, email=register.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            db.session.close()
        except sqlalchemy.exc.IntegrityError:
            flash("User By That Name Exists", "warning")
        flash(f"Account Created successfully", "success")
    return render_template("add_users.html", form=register, data=user_data)


@app.route("/extras/users/view")
@login_required
def view_users():
    pass


@app.route("/extras/users/manage")
@login_required
def manage_users():
    pass


# SEARCHING ROUTE
@app.route("/help/solution/<int:id>", methods=["GET", "POST"])
def search(id):
    # get data from the database based on the data provided
    data = Help.query.get(id)
    # there should be a solution database || FAQ
    return render_template("search.html", data=data)


@app.route("/help/solution/add", methods=["GET", "POST"])
@login_required
def add_solution():
    solution_form = SolutionForm()
    if solution_form.validate_on_submit():
        topic = solution_form.topic.data
        title = solution_form.title.data
        sol = solution_form.solution.data

        solution_data = Help(topic, title, sol)
        db.session.add(solution_data)
        db.session.commit()
        db.session.close()
        flash("Solution Added Successfully", "success")

        # render a html && add the data to the page
    return render_template("add_solution.html", form=solution_form)


# the edit routes
@app.route("/service/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_branch(id):
    # init the form
    service = ServiceForm()
    tellers = Teller.query.all()
    services = ServiceOffered.query.all()
    icons = Icon.query.all()
    services_offered = ServiceOffered.query.all()

    # this teller
    this_service = ServiceOffered.query.get(id)
    # setting form inputs to the data in the database
    service_data = Service.query.all()
    if service.validate_on_submit():
        # update data in the database
        # this_service.name = service.name.data
        this_service.teller = service.teller.data
        this_service.code = service.code.data
        this_service.icon = service.icon.data
        this_service.medical_active = True if service.visible.data == "True" else False
        db.session.commit()

        # prefilling the form with the empty fields
        service.name.data = ""
        service.teller.data = ""
        service.code.data = ""
        service.icon.data = ""
        sio.emit("sync_edit_service" , service_offered_schema.dump(this_service))
        flash("Service Successfully Updated", "success")
        return redirect(url_for("add_company"))

    elif request.method == "GET":
        service.name.data = this_service.name
        service.teller.data = this_service.teller
        service.code.data = this_service.code
        service.icon.data = this_service.icon
    else:
        flash("Service Does Not exist. Add Service name first.", "danger")
    return render_template("edit_company.html", form=service, services=services,tellers=tellers,icons=icons,
                           services_offered = services_offered)


@app.route("/branch/delete/<int:id>", methods=["GET", "POST"])
@login_required
def delete_branch(id):
    branch_data = Branch.query.get(id)
    # get the branch data
    if request.method == "POST":
        db.session.delete(branch_data)
        db.session.commit()
        db.session.close()
        flash("Branch Deleted Sucessfully","success")
    elif request.method == "GET" :
        # init the form
        branch = TellerForm()
    db.session.delete(branch_data)
    db.session.commit()
    db.session.close()
    flash("Branch Deleted Sucessfully", "success")
    # init the form
    branch = TellerForm()
    return render_template("delete_branch.html", form=branch, data=branch_data)


# edit company
@app.route("/teller/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_teller(id):
    # init the form
    teller = TellerForm()
    teller_data = Teller.query.get(id)
    tellers = Teller.query.all()
    services = ServiceOffered.query.all()
    if teller.validate_on_submit():
        # update data in the database
        try:
            teller_data.number = teller.number.data
            teller_data.service = teller.service.data
            # teller_data.active = True if teller.active.data == "True" else False
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            flash("Branch By That Name Exists", "warning")
        # prefilling the form with the empty fields
        teller.number.data = ""
        teller.service.data = ""
        flash("Branch Successfully Updated", "success")
        return redirect(url_for("tellers"))
    elif request.method == "GET":
        teller.number.data = teller_data.number
        teller.service.data = teller_data.service
    else:
        flash("Service Does Not exist. Add Service name first.", "danger")
    return render_template("edit_branch.html", form=teller,services_offered = teller_data,services=services)


@app.route("/email", methods=["POST"])
def send_email():
    to = request.json["email"]
    subject = request.json["subject"]
    body = request.json["body"]
    print("to", to)
    return email(to, subject, body)


# edit company
@app.route("/category/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_category(id):
    this_category = Service.query.get(id)
    # setting form inputs to the data in the database
    # # init the form
    service = ServiceForm()
    if service.validate_on_submit():
        # update data in the database 
        this_category.name = service.name.data
        this_category.service = service.service.data

        # update date to the database
        db.session.commit()
        db.session.close()
        # prefilling the form with the empty fields
        service.name.data = ""
        service.service.data = ""

        flash("Company Successfully Updated", "success")
        return redirect(url_for("view_category"))

    elif request.method == "GET":
        service.name.data = this_category.name
        service.service.data = this_category.service
    else:
        flash("Company Does Not exist. Add company name first.", "danger")
    return render_template("edit_category.html", form=service)



@sio.event
def connect():
    log('online connection established')


@sio.event
def disconnect():
    log('online disconnected from server')



'''working with sockets '''
try:
    sio.connect(socket_link)
except socketio.exceptions.ConnectionError:
    log("Error! Could not connect to online server.")
    # log("...")

@local.event
def connect():
    log('offline connection established')


@local.event
def disconnect():
    print('offline disconnected from server')


'''working with sockets '''
try:
    local.connect(local_socket)
except socketio.exceptions.ConnectionError:
    print("Error! Could not connect offline server.")
    # print("...")

# TODO : app Issues
