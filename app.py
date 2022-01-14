import os
import time
import pdfkit, base64
import bcrypt, random
import datetime, calendar
from flask_mail import (Mail, Message)
from flask import (Flask, render_template, url_for, request, session, redirect, flash, make_response)

from lib import database

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)

app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''

mail = Mail(app)
db = database.Database(os.path.join('db', 'database.db'))

template = '''
Hello, <b>{name}</b>
<br><br>
You are receiving this email because you recently booked a <b>{roomtype}</b> room at <b>Hostelier hostels</b> located in <i>Nairobi, Kenya</i>.
<br><br>
This is to inform you that your booking has been successfully received and you may now pay your deposit to secure a place at the residence.
<br><br>
Kindly pay <b>Ksh.{amount}</b> to the paybill <b>290029</b> using the account number <b>{bookingid}</b>.
<br><br>
After paying, kindly enter the m-pesa transaction code received on the hostelier hostels booking page to confirm payment. You will then receive further information on how to proceed.
<br><br>
Kindly do not reply to this message.
<br>
Hostelier automaton
'''

template2 = '''
Hello,
<br><br>
You are receiving this email because you forgot your old password.
<br>
Visit the link below in your web browser to change your password.
<br><br>
<a href="{link}">{link}</a>
<br><br>
Kindly do not reply to this message.
<br>
Hostelier automaton
'''

def send_email(to, name, rtype, amt, bid):
    final = template.format(name = name, roomtype = rtype, amount = amt, bookingid = bid)
    msg = Message('Hostelier hostels booking confirmation', sender = 'Hostelier automaton', recipients = [to], html = final)  
    mail.send(msg)

def send_email2(to, link):
    final = template2.format(link = link)
    msg = Message('Hostelier hostels password reset', sender = 'Hostelier automaton', recipients = [to], html = final)  
    mail.send(msg)

def verifympesa(code):
    code = code.upper()
    if len(code) != 10: return 'FAIL'
    #
    sanity = code[:2]
    if sanity not in ['PK', 'PL', 'P9', 'PR', 'PM', 'PN', 'PO']: return 'FAIL'
    #
    ptype = code[2:4]
    if ptype in ['65', 'CE', '3N']:
        ptype = 'rent'
    elif ptype in ['D0', 'FR', '90']:
        ptype = 'deposit'
    elif ptype in ['P3', 'U4', 'E3']:
        ptype = 'utility'
    else: return 'FAIL'
    #
    bid = code[4:7]
    if bid[0] == 'N':
        try:
            bid = int(bid[1:])
        except: return 'FAIL'
    else: return 'FAIL'
    #
    amount = code[7:]
    if amount in ['BRE', 'CN0', 'E3N', '99R', '3FP']:
        amount = 8500
    elif amount in ['W34', '12V', '73R', '9PL', 'EZ1']:
        amount = 9500
    else:
        try:
            amount = int(amount, 16)
        except: return 'FAIL'
    #
    return (ptype, bid, amount)

@app.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    else:
        return render_template('index.html')

@app.route('/announcements')
def announcements():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    #
    if session.get('access') == 'staff':
        return redirect(url_for('announcements_admin'))
    #
    data = db.get_announcements()[::-1]
    for x in data:
        s = db.get_staff(x[3])
        x[3] = s[1] + ' ' + s[2]
        dt = datetime.datetime.fromtimestamp(x[4])
        x[4] = dt.strftime('%d-%b-%Y')
    return render_template('announcements.html', data = data)

@app.route('/announcements_admin')
def announcements_admin():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    #
    data = db.get_announcements()[::-1]
    for x in data:
        s = db.get_staff(x[3])
        x[3] = s[1] + ' ' + s[2]
        dt = datetime.datetime.fromtimestamp(x[4])
        x[4] = dt.strftime('%d-%b-%Y')
    return render_template('announcements-admin.html', data = data)

@app.route('/booking')
def booking():
    return render_template('booking.html')

@app.route('/bookings')
def bookings():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    #
    data = {}
    #
    ar = []
    data['full'] = ''
    rms = db.get_rooms()
    for x in rms:
        r = db.get_roomtype(x[1])
        if r[1] == x[4]:
            ar.append(str(x[0]))
    data['full'] = ','.join(ar)
    #
    data['bookings'] = db.get_bookings()[::-1]
    for x in data['bookings']:
        dt = datetime.datetime.fromtimestamp(x[7])
        x[7] = dt.strftime('%d-%b-%Y')
        x[8] = db.get_roomtype(x[8])[0]
    return render_template('bookings.html', data = data)

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    #
    data = {}
    data['announcements'] = db.get_announcements_small()[::-1]
    for x in data['announcements']:
        x[1] = x[1].replace('<br>', '')
        if len(x[1]) > 75:
            x[1] = x[1][:75].replace('<br>', '') + '...'
    #
    if session.get('access') == 'staff':
        data['tickets'] = db.get_tickets_small()[::-1]
        for x in data['tickets']:
            x[2] = x[2].replace('<br>', '')
            if len(x[2]) > 75:
                x[2] = x[2][:75] + '...'
            x[3] = x[3].capitalize()
        #
        residents = len(db.get_residents_small())
        waiting = len(db.get_bookings())
        tickets = len(db.get_tickets_small())
        vacancies = 120 - residents
        arrears = len(db.get_rent_arrears())
        data['details'] = [residents, waiting, tickets, vacancies, arrears]
    else:
        entry = db.get_resident(session['email'])
        bill = db.get_billing(entry[10])
        #
        acno = 'SNBID2021X{}'.format(entry[10])
        deadline = datetime.datetime.fromtimestamp(bill[3]).strftime('%d-%b-%Y')
        deadline2 = datetime.datetime.fromtimestamp(bill[6]).strftime('%d-%b-%Y')
        data['details'] = [entry[9], db.get_roomname(entry[9]), acno, deadline, '{:,}'.format(bill[2]), '{:,}'.format(bill[1]), '{:,}'.format(bill[5]), deadline2, '{:,}'.format(bill[4])]
    return render_template('dashboard.html', data = data)

@app.route('/feedback')
def feedback():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    #
    if session.get('access') == 'staff':
        return redirect(url_for('feedback_admin'))
    #
    return render_template('feedback.html')

@app.route('/feedback_admin')
def feedback_admin():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    #
    data = db.get_feedback()[::-1]
    for x in data:
        dt = datetime.datetime.fromtimestamp(x[3])
        x[3] = dt.strftime('%d-%b-%Y')
    return render_template('feedback-admin.html', data = data)

@app.route('/payments')
def payments():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    #
    sid = db.get_resident(session['email'])[0]
    data = db.get_my_transactions(sid)
    for x in data:
        x[1] = db.get_transaction_type(x[1])
        dt = datetime.datetime.fromtimestamp(x[3])
        x[3] = dt.strftime('%d-%b-%Y')
    return render_template('payments.html', data = data)

@app.route('/profile')
def profile():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    #
    if session['access'] == 'staff':
        data = db.get_staff(session['email'])
        details = [data[3], data[6], data[7]]
    else:
        data = db.get_resident(session['email'])
        details = [data[3], data[6], data[7], data[8]]
    return render_template('profile.html', data = details)

@app.route('/reports')
def reports():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    #
    data = []
    data.append(db.get_mf_residents())
    dat = db.get_all_transactions()
    for x in dat:
        x[3] = datetime.datetime.fromtimestamp(x[3]).strftime('%d-%b-%Y')
    data.append(dat)
    return render_template('reports.html', data = data)

@app.route('/rooms')
def rooms():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    #
    data = db.get_rooms()
    for x in data:
        r = db.get_roomtype(x[1])
        x[1] = r[0]
        x[3] = db.get_location(x[3])
        x.append('full' if r[1] == x[4] else 'vacancy')
    return render_template('rooms.html', data = data)

@app.route('/tickets')
def tickets():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    #
    if session.get('access') == 'staff':
        return redirect(url_for('tickets_admin'))
    #
    data = db.get_my_tickets(session['email'])[::-1]
    for x in data:
        if x[6]:
            dt2 = datetime.datetime.fromtimestamp(x[6])
            x[6] = dt2.strftime('%d-%b-%Y')
        dt = datetime.datetime.fromtimestamp(x[5])
        x[5] = dt.strftime('%d-%b-%Y')
    return render_template('tickets.html', data = data)

@app.route('/tickets_admin')
def tickets_admin():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    #
    data = db.get_tickets()[::-1]
    for x in data:
        if x[6]:
            dt2 = datetime.datetime.fromtimestamp(x[6])
            x[6] = dt2.strftime('%d-%b-%Y')
        dt = datetime.datetime.fromtimestamp(x[5])
        x[5] = dt.strftime('%d-%b-%Y')
    return render_template('tickets-admin.html', data = data)

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    #
    data = {}
    data['staff'] = db.get_staff_small()
    data['students'] = db.get_residents_small()
    #
    for x in data['staff']:
        x[3] = 'Male' if x[3] == 'M' else 'Female'
    for y in data['students']:
        y[3] = 'Male' if y[3] == 'M' else 'Female'
    return render_template('admin.html', data = data)

@app.route('/passwordreset')
def passwordreset():
    email = base64.b64decode(request.args.get('tk'))
    return render_template('passwordreset.html', data = email)

@app.route('/newstaff', methods = ['POST'])
def newstaff():
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    gender = request.form.get('gender')
    dob = request.form.get('dob')
    idno = request.form.get('idno')
    tel = request.form.get('telephone')
    email = request.form.get('email')
    isadmin = request.form.get('isadmin')
    reports = request.form.get('canviewreports')
    passwd = request.form.get('passwd')
    #
    dt = datetime.datetime.strptime(dob, '%Y-%m-%d')
    dob = calendar.timegm(dt.timetuple())
    #
    pw = bcrypt.hashpw(passwd.encode('utf-8'), bcrypt.gensalt())
    db.new_staff(fname, lname, gender, dob, idno, tel, email, isadmin, reports, pw)
    flash('Staff account created successfully')
    return redirect(url_for('admin'))

@app.route('/newticket', methods = ['POST'])
def newticket():
    issue = request.form.get('issue')
    location = request.form.get('location')
    description = request.form.get('description').replace('\n', '<br>')
    #
    rid = db.get_resident(session['email'])[9]
    db.new_ticket(description, rid, location, issue, time.time())
    flash('Ticket logged successfully')
    return redirect(url_for('dashboard'))

@app.route('/closeticket', methods = ['POST'])
def closeticket():
    tid = request.form.get('tid')
    remarks = request.form.get('remarks')
    db.close_ticket(tid, remarks, time.time())
    flash('Ticket closed successfully')
    return redirect(url_for('tickets_admin'))

@app.route('/verifyrent', methods = ['POST'])
def verifyrent():
    code = request.form.get('mpesa')
    data = verifympesa(code)
    if data == 'FAIL':
        flash('Invalid transaction code')
    else:
        sid = db.get_resident(session['email'])[0]
        db.pay_rent(sid, data[1], data[2], time.time())
        flash('Payment of rent amount Ksh.{} verified'.format(data[2]))
    return redirect(url_for('dashboard'))

@app.route('/verifyutility', methods = ['POST'])
def verifyutility():
    code = request.form.get('mpesa')
    data = verifympesa(code)
    if data == 'FAIL':
        flash('Invalid transaction code')
    else:
        sid = db.get_resident(session['email'])[0]
        db.pay_utility(sid, data[1], data[2], time.time())
        flash('Payment of utility bill amount Ksh.{} verified'.format(data[2]))
    return redirect(url_for('dashboard'))

@app.route('/verifydeposit', methods = ['POST'])
def verifydeposit():
    code = request.form.get('mpesa')
    data = verifympesa(code)
    if data == 'FAIL':
        flash('Invalid transaction code')
        return redirect(url_for('booking'))
    else:
        dt = calendar.timegm(datetime.datetime.now().timetuple()) + 864000 # 10 days
        bid = db.new_billing(data[2], dt)
        db.set_booking_paid(data[1])
        dat = db.get_booking(data[1])
        #
        id_ = str(random.randint(10000000, 99999999))
        sid = db.new_resident(dat[1], dat[2], dat[3], 0, id_, dat[5], dat[4], dat[6], 0, bid, '?')
        db.link_booking(data[1], sid)
        db.new_transaction(sid, 2, data[2], time.time())
        flash('Payment of Ksh.{} verified. Kindly report to the location within 2 weeks to be assigned a room'.format(data[2]))
        return redirect(url_for('index'))

@app.route('/bookroom', methods = ['POST'])
def bookroom():
    fname = request.form.get('firstname')
    lname = request.form.get('lastname')
    email = request.form.get('email')
    phone = request.form.get('telephone')
    university = request.form.get('university')
    gender = request.form.get('gender')
    roomtype = request.form.get('roomtype')
    #
    if fname and lname and email and phone and university:
        roomtype = int(roomtype)
        if roomtype == 1:
            t = '2-person sharing'
            a = 9500
        else:
            t = '4-person sharing'
            a = 8500
        bid = db.new_booking(fname, lname, gender, email, phone, university, time.time(), roomtype, 'no', 0)
        send_email(email, fname, t, a, 'SNBID2021X{}'.format(bid))
        flash('Booking received successfully, you will receive an email with details on how to proceed')
        return redirect(url_for('index'))
    else:
        flash('Some details have not been filled out correctly')
        return redirect(url_for('booking'))

@app.route('/upgradebooking', methods = ['POST'])
def upgradebooking():
    bid = request.form.get('bid')
    sid = request.form.get('sid')
    roomid = request.form.get('roomid')
    dob = request.form.get('dob')
    idno = request.form.get('idno')
    passwd = request.form.get('passwd')
    #
    dt = datetime.datetime.strptime(dob, '%Y-%m-%d')
    dob = calendar.timegm(dt.timetuple())
    #
    pw = bcrypt.hashpw(passwd.encode('utf-8'), bcrypt.gensalt())
    db.upgrade_resident(sid, roomid, dob, idno, pw)
    db.remove_booking(bid)
    db.add_occupant(roomid)
    flash('Resident account created successfully')
    return redirect(url_for('bookings'))

@app.route('/newfeedback', methods = ['POST'])
def newfeedback():
    feedback = request.form.get('feedback').replace('\n', '<br>')
    rating = request.form.get('star')
    #
    db.new_feedback(feedback, rating, time.time())
    flash('Feedback received successfully')
    return redirect(url_for('dashboard'))

@app.route('/newannouncement', methods = ['POST'])
def newannouncement():
    title = request.form.get('title')
    announcement = request.form.get('announcement').replace('\n', '<br>')
    #
    db.new_announcement(title, announcement, session['email'], time.time())
    flash('Announcement added successfully')
    return redirect(url_for('announcements'))

@app.route('/delannouncement')
def delannouncement():
    aid = request.args.get('id')
    db.remove_announcement(aid)
    flash('Announcement deleted successfully')
    return redirect(url_for('announcements'))

@app.route('/delstaff')
def delstaff():
    sid = request.args.get('id')
    db.remove_staff(sid)
    flash('Staff profile deleted successfully')
    return redirect(url_for('admin'))

@app.route('/delstudent')
def delstudent():
    sid = request.args.get('id')
    db.remove_billing(sid)
    db.remove_occupant(db.get_resident_id(sid)[9])
    db.remove_resident(sid)
    flash('Resident profile deleted successfully')
    return redirect(url_for('admin'))

@app.route('/delbooking')
def delbooking():
    bid = request.args.get('id')
    db.remove_booking(bid)
    flash('Booking deleted successfully')
    return redirect(url_for('bookings'))

@app.route('/residentsreport')
def residentsreport():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    #
    data = db.get_all_residents()
    for x in data:
        x[4] = datetime.datetime.fromtimestamp(x[4]).strftime('%d-%b-%Y')
    html = render_template('residents-report.html', data = data)
    pdf = pdfkit.from_string(html, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=residents_report.pdf'
    return response

@app.route('/staffreport')
def staffreport():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    #
    data = db.get_all_staff()
    for x in data:
        x[4] = datetime.datetime.fromtimestamp(x[4]).strftime('%d-%b-%Y')
    html = render_template('staff-report.html', data = data)
    pdf = pdfkit.from_string(html, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=staff_report.pdf'
    return response

@app.route('/transactionsreport')
def transactionsreport():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    #
    data = {}
    data['total'] = 0
    data['transactions'] = db.get_all_transactions()
    for x in data['transactions']:
        x[1] = db.get_transaction_type(x[1])
        x[3] = datetime.datetime.fromtimestamp(x[3]).strftime('%d-%b-%Y')
        data['total'] += x[2]
    data['total'] = '{:,}'.format(data['total'])
    html = render_template('transactions-report.html', data = data)
    pdf = pdfkit.from_string(html, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=transactions_report.pdf'
    return response

@app.route('/rdtransactionsreport')
def rdtransactionsreport():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    #
    data = {}
    data['total'] = 0
    data['transactions'] = []
    dat = db.get_all_transactions()
    for x in dat:
        if x[1] not in [1, 2]: continue
        x[1] = db.get_transaction_type(x[1])
        x[3] = datetime.datetime.fromtimestamp(x[3]).strftime('%d-%b-%Y')
        data['total'] += x[2]
        data['transactions'].append(x)
    data['total'] = '{:,}'.format(data['total'])
    html = render_template('rdtransactions-report.html', data = data)
    pdf = pdfkit.from_string(html, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=rent_deposit_transactions_report.pdf'
    return response

@app.route('/utransactionsreport')
def utransactionsreport():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    #
    data = {}
    data['total'] = 0
    data['transactions'] = []
    dat = db.get_all_transactions()
    for x in dat:
        if x[1] != 3: continue
        x[1] = db.get_transaction_type(x[1])
        x[3] = datetime.datetime.fromtimestamp(x[3]).strftime('%d-%b-%Y')
        data['total'] += x[2]
        data['transactions'].append(x)
    data['total'] = '{:,}'.format(data['total'])
    html = render_template('utransactions-report.html', data = data)
    pdf = pdfkit.from_string(html, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=utility_bill_transactions_report.pdf'
    return response

@app.route('/ocroomsreport')
def ocroomsreport():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    #
    data = []
    dat = db.get_rooms()
    for x in dat:
        if x[4] == 0: continue
        rt = db.get_roomtype(x[1])
        x[1] = rt[0]
        x[4] = '{0}/{1}'.format(x[4], rt[1])
        data.append(x)
    html = render_template('occupiedrooms-report.html', data = data)
    pdf = pdfkit.from_string(html, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=occupied_rooms_report.pdf'
    return response

@app.route('/uocroomsreport')
def uocroomsreport():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    #
    data = []
    dat = db.get_rooms()
    for x in dat:
        if x[4] > 0: continue
        rt = db.get_roomtype(x[1])
        x[1] = rt[0]
        x[4] = '{0}/{1}'.format(x[4], rt[1])
        data.append(x)
    html = render_template('emptyrooms-report.html', data = data)
    pdf = pdfkit.from_string(html, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=empty_rooms_report.pdf'
    return response

@app.route('/rentarrearsreport')
def rentarrearsreport():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    #
    data = []
    dat = db.get_rent_arrears()
    for x in dat:
        a = db.get_resident_for_bill(x[0])
        a.append(x[2])
        data.append(a)
    html = render_template('rent-arrears-report.html', data = data)
    pdf = pdfkit.from_string(html, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=rent_arrears_report.pdf'
    return response

@app.route('/utilityarrearsreport')
def utilityarrearsreport():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    #
    data = []
    dat = db.get_utility_arrears()
    for x in dat:
        a = db.get_resident_for_bill(x[0])
        a.append(x[5])
        data.append(a)
    html = render_template('utility-arrears-report.html', data = data)
    pdf = pdfkit.from_string(html, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=utility_arrears_report.pdf'
    return response

@app.route('/editprofile', methods = ['POST'])
def editprofile():
    tel = request.form.get('telephone')
    email = request.form.get('email')
    if session['access'] == 'student':
        uni = request.form.get('university')
        sid = db.get_resident(session['email'])[0]
        db.edit_resident(sid, tel, email, uni)
    else:
        sid = db.get_staff(session['email'])[0]
        db.edit_staff(sid, tel, email)
    #
    if session['email'] != email:
        session['email'] = email
    #
    flash('Profile updated successfully')
    return redirect(url_for('profile'))

@app.route('/forgotpassword', methods = ['POST'])
def forgotpassword():
    link = 'localhost/passwordreset?tk={}'
    email = request.form.get('email')
    if db.get_resident(email) or db.get_staff(email):
        send_email2(email, link.format(base64.b64encode(email)))
        flash('You will receive an email with details on how to proceed')
    else:
        flash('No account with the email provided exists')
    return redirect(url_for('index'))

@app.route('/resetpassword', methods = ['POST'])
def resetpassword():
    email = request.form.get('email')
    newpass = request.form.get('newpass')
    #
    if db.get_resident(email):
        db.set_rpasswd(email, bcrypt.hashpw(newpass.encode('utf-8'), bcrypt.gensalt()))
    else:
        db.set_spasswd(email, bcrypt.hashpw(newpass.encode('utf-8'), bcrypt.gensalt()))
    flash('Password changed successfully')
    return redirect(url_for('index'))

@app.route('/changepassword', methods = ['POST'])
def changepassword():
    old = request.form.get('current')
    new = request.form.get('new')
    #
    if session['access'] == 'staff':
        entry = db.get_staff(session['email'])
        pwhash = entry[10].encode('utf-8')
    else:
        entry = db.get_resident(session['email'])
        pwhash = entry[11].encode('utf-8')
    if bcrypt.checkpw(old.encode('utf-8'), pwhash):
        if session['access'] == 'staff':
            db.set_spasswd(session['email'], bcrypt.hashpw(new.encode('utf-8'), bcrypt.gensalt()))
        else:
            db.set_rpasswd(session['email'], bcrypt.hashpw(new.encode('utf-8'), bcrypt.gensalt()))
        flash('Password changed successfully')
    else:
        flash('Wrong password')
    return redirect(request.referrer)

@app.route('/signin', methods = ['POST'])
def signin():
    email = request.form.get('email')
    passwd = request.form.get('password')
    staff = request.form.get('staff')
    #
    if staff == 'on':
        entry = db.get_staff(email)
        if entry:
            pwhash = entry[10].encode('utf-8')
        else:
            flash('Unknown user account')
            return redirect(url_for('index'))
    else:
        entry = db.get_resident(email)
        if entry:
            pwhash = entry[11].encode('utf-8')
        else:
            flash('Unknown user account')
            return redirect(url_for('index'))
    #
    if entry and bcrypt.checkpw(passwd.encode('utf-8'), pwhash):
        session['id'] = entry[0]
        session['email'] = email
        session['logged_in'] = True
        session['name'] = entry[1] + ' ' + entry[2]
        session['admin'] = True if entry[8] == 'Y' else False
        session['access'] = 'staff' if staff == 'on' else 'student'
        session['canview_reports'] = True if entry[9] == 'Y' else False
        return redirect(url_for('dashboard'))
    #
    flash('Unknown user account')
    return redirect(url_for('index'))

@app.route('/signout')
def signout():
    session['id'] = ''
    session['name'] = ''
    session['email'] = ''
    session['access'] = ''
    session['admin'] = False
    session['logged_in'] = False
    session['canview_reports'] = False
    return redirect(url_for('index'))

if __name__ == '__main__':
    db.open_db()
    app.run(host = '0.0.0.0', port = 80, debug = False)
    db.close_db()
