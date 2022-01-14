import sqlite3, calendar, datetime

class Database(object):
    def __init__(self, dbname):
        self.dbname = dbname

    def open_db(self):
        self.dbworker = sqlite3.connect(self.dbname, check_same_thread = False)
        self.cursor = self.dbworker.cursor()

    def close_db(self):
        self.dbworker.close()

    def new_resident(self, *args):
        command1 = 'INSERT INTO students(firstname, surname, gender, dob, idNumber, telephone, emailAddress, university, roomID, billingID, password) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        try:
            self.cursor.execute(command1, args)
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        #
        command2 = 'SELECT seq FROM sqlite_sequence WHERE name = ?'
        self.cursor.execute(command2, ('students', ))
        return self.cursor.fetchone()[0]

    def new_staff(self, *args):
        command = 'INSERT INTO staff(firstname, surname, gender, dob, idNumber, telephone, emailAddress, isAdmin, canViewReports, password) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        try:
            self.cursor.execute(command, args)
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        return True

    def new_transaction(self, sid, type_, amount, date):
        command = 'INSERT INTO transactions(transactionType, transactionAmount, transactionDate, studentID) VALUES (?, ?, ?, ?)'
        try:
            self.cursor.execute(command, (type_, amount, date, sid))
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        return True

    def get_transaction_type(self, type_):
        command = 'SELECT transactionName FROM transactionTypes WHERE transactionType = ?'
        self.cursor.execute(command, (type_, ))
        return self.cursor.fetchone()[0]

    def new_billing(self, paid, date):
        command1 = 'INSERT INTO billing(totalRentPaid, rentOwed, rentDeadline, totalUtilityPaid, utilityOwed, utilityDeadline) VALUES (?, ?, ?, ?, ?, ?)'
        try:
            self.cursor.execute(command1, (paid, paid, date, 0, 100, date))
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        #
        command2 = 'SELECT seq FROM sqlite_sequence WHERE name = ?'
        self.cursor.execute(command2, ('billing', ))
        return self.cursor.fetchone()[0]

    def get_billing(self, bid):
        command = 'SELECT * FROM billing WHERE billingID = ?'
        self.cursor.execute(command, (bid, ))
        return self.cursor.fetchone()

    def remove_billing(self, sid):
        bid = self.get_resident_id(sid)[10]
        command = 'DELETE FROM billing WHERE billingID = ?'
        try:
            self.cursor.execute(command, (bid, ))
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        return True

    def get_all_residents(self):
        command = 'SELECT * FROM students'
        self.cursor.execute(command)
        out = []
        data = self.cursor.fetchall()
        for x in data:
            if x[9] == 0: continue
            out.append(list(x))
        return out

    def get_resident_for_bill(self, bid):
        command = 'SELECT * FROM students WHERE billingID = ?'
        self.cursor.execute(command, (bid, ))
        data = self.cursor.fetchone()
        return list(data)

    def get_resident(self, email):
        command = 'SELECT * FROM students WHERE emailAddress = ?'
        self.cursor.execute(command, (email, ))
        return self.cursor.fetchone()

    def get_resident_id(self, sid):
        command = 'SELECT * FROM students WHERE studentID = ?'
        self.cursor.execute(command, (sid, ))
        return self.cursor.fetchone()

    def upgrade_resident(self, sid, roomid, dob, idno, pwd):
        command = 'UPDATE students SET dob = ?, idNumber = ?, roomID = ?, password = ? WHERE studentID = ?'
        try:
            self.cursor.execute(command, (dob, idno, roomid, pwd, sid))
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        return True

    def get_all_transactions(self):
        command = 'SELECT * FROM transactions'
        self.cursor.execute(command)
        out = []
        data = self.cursor.fetchall()
        for x in data:
            out.append(list(x))
        return out

    def get_my_transactions(self, sid):
        command = 'SELECT * FROM transactions WHERE studentID = ?'
        self.cursor.execute(command, (sid, ))
        out = []
        data = self.cursor.fetchall()
        for x in data:
            out.append(list(x))
        return out

    def link_booking(self, bid, sid):
        command = 'UPDATE bookings SET studentID = ? WHERE bookingID = ?'
        try:
            self.cursor.execute(command, (sid, bid))
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        return True

    def add_occupant(self, rid):
        co = self.get_occupants(rid) + 1
        command = 'UPDATE rooms SET currentOccupants = ? WHERE roomID = ?'
        try:
            self.cursor.execute(command, (co, rid))
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        return True

    def remove_occupant(self, rid):
        co = self.get_occupants(rid) - 1
        command = 'UPDATE rooms SET currentOccupants = ? WHERE roomID = ?'
        try:
            self.cursor.execute(command, (co, rid))
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        return True

    def get_residents_small(self):
        command = 'SELECT studentID, firstname, surname, gender, idNumber, telephone, emailAddress, university, roomID FROM students'
        self.cursor.execute(command)
        out = []
        data = self.cursor.fetchall()
        for x in data:
            if x[8] == 0: continue
            out.append(list(x))
        return out

    def get_staff(self, email):
        command = 'SELECT * FROM staff WHERE emailAddress = ?'
        self.cursor.execute(command, (email, ))
        return self.cursor.fetchone()

    def get_all_staff(self):
        command = 'SELECT * FROM staff'
        self.cursor.execute(command)
        out = []
        data = self.cursor.fetchall()
        for x in data:
            out.append(list(x))
        return out

    def get_staff_small(self):
        command = 'SELECT staffID, firstname, surname, gender, idNumber, telephone, emailAddress, isAdmin, canViewReports FROM staff'
        self.cursor.execute(command)
        out = []
        data = self.cursor.fetchall()
        for x in data:
            out.append(list(x))
        return out

    def set_spasswd(self, email, passwd):
        command = 'UPDATE staff SET password = ? WHERE emailAddress = ?'
        try:
            self.cursor.execute(command, (passwd, email))
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        return True

    def set_rpasswd(self, email, passwd):
        command = 'UPDATE students SET password = ? WHERE emailAddress = ?'
        try:
            self.cursor.execute(command, (passwd, email))
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        return True

    def edit_resident(self, sid, phone, email, uni):
        command = 'UPDATE students SET telephone = ?, emailAddress = ?, university = ? WHERE studentID = ?'
        try:
            self.cursor.execute(command, (phone, email, uni, sid))
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        return True

    def edit_staff(self, sid, phone, email):
        command = 'UPDATE staff SET telephone = ?, emailAddress = ? WHERE staffID = ?'
        try:
            self.cursor.execute(command, (phone, email, sid))
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        return True

    def get_mf_residents(self):
        m1, f1 = 0, 0
        command = 'SELECT * FROM students WHERE gender = ?'
        self.cursor.execute(command, ('M', ))
        m = self.cursor.fetchall()
        #
        self.cursor.execute(command, ('F', ))
        f = self.cursor.fetchall()
        #
        for x in m:
            if x[9] == 0: continue
            m1 += 1
        #
        for y in f:
            if y[9] == 0: continue
            f1 += 1
        return m1, f1

    def remove_resident(self, sid):
        command = 'DELETE FROM students WHERE studentID = ?'
        try:
            self.cursor.execute(command, (sid, ))
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        return True

    def remove_staff(self, sid):
        command = 'DELETE FROM staff WHERE staffID = ?'
        try:
            self.cursor.execute(command, (sid, ))
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        return True

    def new_booking(self, *args):
        command1 = 'INSERT INTO bookings(firstname, surname, gender, emailAddress, telephone, university, bookingDate, roomType, paid, studentID) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        try:
            self.cursor.execute(command1, args)
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        #
        command2 = 'SELECT seq FROM sqlite_sequence WHERE name = ?'
        self.cursor.execute(command2, ('bookings', ))
        return self.cursor.fetchone()[0]

    def set_booking_paid(self, bid):
        command = 'UPDATE bookings SET paid = ? WHERE bookingID = ?'
        try:
            self.cursor.execute(command, ('yes', bid))
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        return True

    def get_booking(self, bid):
        command = 'SELECT * FROM bookings WHERE bookingID = ?'
        self.cursor.execute(command, (bid, ))
        return self.cursor.fetchone()

    def get_bookings(self):
        command = 'SELECT * FROM bookings'
        self.cursor.execute(command)
        out = []
        data = self.cursor.fetchall()
        for x in data:
            out.append(list(x))
        return out

    def remove_booking(self, bid):
        command = 'DELETE FROM bookings WHERE bookingID = ?'
        try:
            self.cursor.execute(command, (bid, ))
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        return True

    def get_rent_arrears(self):
        command = 'SELECT * FROM billing'
        self.cursor.execute(command)
        out = []
        data = self.cursor.fetchall()
        for x in data:
            if calendar.timegm(datetime.datetime.now().timetuple()) > x[3]:
                out.append(list(x))
        return out

    def get_utility_arrears(self):
        command = 'SELECT * FROM billing'
        self.cursor.execute(command)
        out = []
        data = self.cursor.fetchall()
        for x in data:
            if calendar.timegm(datetime.datetime.now().timetuple()) > x[6]:
                out.append(list(x))
        return out

    def pay_rent(self, sid, bid, amount, date):
        command1 = 'SELECT * FROM billing WHERE billingID = ?'
        self.cursor.execute(command1, (bid, ))
        details = self.cursor.fetchone()
        #
        total, owed, deadline = details[1], details[2], details[3]
        if owed == amount:
            deadline += 2629746 #1 month
        else:
            deadline += 864000 #10 days
        total += amount
        owed -= amount
        command2 = 'UPDATE billing SET totalRentPaid = ?, rentOwed = ?, rentDeadline = ? WHERE billingID = ?'
        self.cursor.execute(command2, (total, owed, deadline, bid))
        self.dbworker.commit()
        #
        command3 = 'INSERT INTO transactions(transactionType, transactionAmount, transactionDate, studentID) VALUES (?, ?, ?, ?)'
        try:
            self.cursor.execute(command3, (1, amount, date, sid))
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        return True

    def pay_utility(self, sid, bid, amount, date):
        command1 = 'SELECT * FROM billing WHERE billingID = ?'
        self.cursor.execute(command1, (bid, ))
        details = self.cursor.fetchone()
        #
        total, owed, deadline = details[4], details[5], details[6]
        if owed == amount:
            deadline += 2629746 #1 month
        else:
            deadline += 864000 #10 days
        total += amount
        owed -= amount
        command2 = 'UPDATE billing SET totalUtilityPaid = ?, utilityOwed = ?, utilityDeadline = ? WHERE billingID = ?'
        self.cursor.execute(command2, (total, owed, deadline, bid))
        self.dbworker.commit()
        #
        command3 = 'INSERT INTO transactions(transactionType, transactionAmount, transactionDate, studentID) VALUES (?, ?, ?, ?)'
        try:
            self.cursor.execute(command3, (3, amount, date, sid))
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        return True

    def new_announcement(self, title, contents, email, date):
        command = 'INSERT INTO announcements(title, contents, email, dateWritten) VALUES (?, ?, ?, ?)'
        try:
            self.cursor.execute(command, (title, contents, email, date))
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        return True

    def get_announcements(self):
        command = 'SELECT * FROM announcements'
        self.cursor.execute(command)
        out = []
        data = self.cursor.fetchall()
        for x in data:
            out.append(list(x))
        return out

    def remove_announcement(self, aid):
        command = 'DELETE FROM announcements WHERE announcementID = ?'
        try:
            self.cursor.execute(command, (aid, ))
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        return True

    def get_announcements_small(self):
        command = 'SELECT title, contents FROM announcements'
        self.cursor.execute(command)
        out = []
        data = self.cursor.fetchall()
        for x in data:
            out.append(list(x))
        return out

    def new_ticket(self, desc, rid, loc, issue, date):
        command = 'INSERT INTO tickets(ticketDescription, roomID, location, issue, dateOpened, dateClosed, status, remarks) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
        try:
            self.cursor.execute(command, (desc, rid, loc, issue, date, 0, 'open', ''))
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        return True

    def get_tickets(self):
        command = 'SELECT * FROM tickets'
        self.cursor.execute(command)
        out = []
        data = self.cursor.fetchall()
        for x in data:
            out.append(list(x))
        return out

    def get_my_tickets(self, email):
        rid = self.get_resident(email)[9]
        command = 'SELECT * FROM tickets WHERE roomID = ?'
        self.cursor.execute(command, (rid, ))
        out = []
        data = self.cursor.fetchall()
        for x in data:
            out.append(list(x))
        return out

    def get_tickets_small(self):
        command = 'SELECT issue, location, ticketDescription, status FROM tickets WHERE status = ?'
        self.cursor.execute(command, ('open', ))
        out = []
        data = self.cursor.fetchall()
        for x in data:
            out.append(list(x))
        return out

    def close_ticket(self, tid, remarks, date):
        command = 'UPDATE tickets SET dateClosed = ?, status = ?, remarks = ? WHERE ticketID = ?'
        try:
            self.cursor.execute(command, (date, 'closed', remarks, tid))
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        return True

    def new_feedback(self, contents, rating, date):
        command = 'INSERT INTO feedback(contents, starRating, dateWritten) VALUES (?, ?, ?)'
        try:
            self.cursor.execute(command, (contents, rating, date))
        except sqlite3.IntegrityError:
            return False
        self.dbworker.commit()
        return True

    def get_feedback(self):
        command = 'SELECT * FROM feedback'
        self.cursor.execute(command)
        out = []
        data = self.cursor.fetchall()
        for x in data:
            out.append(list(x))
        return out

    def get_rooms(self):
        command = 'SELECT * FROM rooms'
        self.cursor.execute(command)
        out = []
        data = self.cursor.fetchall()
        for x in data:
            out.append(list(x))
        return out

    def get_roomtype(self, rid):
        command = 'SELECT roomName, maxOccupants FROM roomTypes WHERE roomType = ?'
        self.cursor.execute(command, (rid, ))
        return self.cursor.fetchone()

    def get_occupants(self, rid):
        command = 'SELECT currentOccupants FROM rooms WHERE roomID = ?'
        self.cursor.execute(command, (rid, ))
        return self.cursor.fetchone()[0]

    def get_roomname(self, rid):
        command = 'SELECT roomType FROM rooms WHERE roomID = ?'
        self.cursor.execute(command, (rid, ))
        rtype = self.cursor.fetchone()[0]
        return self.get_roomtype(rtype)[0]

    def get_location(self, lid):
        command = 'SELECT locationName, locationAddress FROM locations WHERE locationID = ?'
        self.cursor.execute(command, (lid, ))
        return ', '.join(self.cursor.fetchone())
