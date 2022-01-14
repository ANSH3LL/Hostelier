import sqlite3

print '[*] Creating database...'

worker = sqlite3.connect('database.db')
cursor = worker.cursor()

commands = [
            '''CREATE TABLE students(studentID INTEGER PRIMARY KEY AUTOINCREMENT, firstname TEXT NOT NULL, surname TEXT, gender TEXT, dob REAL, idNumber TEXT UNIQUE, telephone TEXT, emailAddress TEXT, university TEXT, roomID INTEGER, billingID INTEGER, password TEXT)''',
            '''CREATE TABLE bookings(bookingID INTEGER PRIMARY KEY AUTOINCREMENT, firstname TEXT NOT NULL, surname TEXT, gender TEXT, emailAddress TEXT, telephone TEXT, university TEXT, bookingDate REAL, roomType INTEGER, paid TEXT, studentID INTEGER)''',
            '''CREATE TABLE billing(billingID INTEGER PRIMARY KEY AUTOINCREMENT, totalRentPaid REAL, rentOwed REAL, rentDeadline REAL, totalUtilityPaid REAL, utilityOwed REAL, utilityDeadline REAL)''',
            '''CREATE TABLE staff(staffID INTEGER PRIMARY KEY AUTOINCREMENT, firstname TEXT NOT NULL, surname TEXT, gender TEXT, dob REAL, idNumber TEXT UNIQUE, telephone TEXT, emailAddress TEXT, isAdmin TEXT, canViewReports TEXT, password TEXT)''',
            '''CREATE TABLE rooms(roomID INTEGER PRIMARY KEY AUTOINCREMENT, roomType INTEGER, floor INTEGER, locationID INTEGER, currentOccupants INTEGER)''',
            '''CREATE TABLE roomTypes(roomType INTEGER PRIMARY KEY AUTOINCREMENT, roomName TEXT, rentAmount REAL, maxOccupants INTEGER)''',
            '''CREATE TABLE locations(locationID INTEGER PRIMARY KEY AUTOINCREMENT, locationName TEXT, locationAddress TEXT)''',
            '''CREATE TABLE transactions(transactionID INTEGER PRIMARY KEY AUTOINCREMENT, transactionType INTEGER, transactionAmount REAL, transactionDate REAL, studentID INTEGER)''',
            '''CREATE TABLE transactionTypes(transactionType INTEGER PRIMARY KEY AUTOINCREMENT, transactionName TEXT)''',
            '''CREATE TABLE tickets(ticketID INTEGER PRIMARY KEY AUTOINCREMENT, ticketDescription TEXT, roomID INTEGER, location TEXT, issue TEXT, dateOpened REAL, dateClosed REAL, status TEXT, remarks TEXT)''',
            '''CREATE TABLE announcements(announcementID INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, contents TEXT, email TEXT, dateWritten REAL)''',
            '''CREATE TABLE feedback(feedbackID INTEGER PRIMARY KEY AUTOINCREMENT, contents TEXT, starRating INTEGER, dateWritten REAL)'''
]

for command in commands:
    cursor.execute(command)

cursor.execute('INSERT INTO staff(firstname, surname, gender, dob, idNumber, telephone, emailAddress, isAdmin, canViewReports, password) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', ('Administrator', '', 'M', 799669414, '40728472', '+254712345678', 'ictadmin@hostelier.co.ke', 'Y', 'Y', '$2b$12$FqdmlRPZtsxdEXVXtPFRjug8mX6lDtRqzVOcM2KxkBNoo5/vNTCge'))

#1 - sharedx2-1+4  2 - sharedx4-2+3
#1,2 - female
#3,4 - male
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (1, 1, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (1, 1, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (1, 1, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (1, 1, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (1, 1, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (1, 1, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (1, 1, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (1, 1, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (1, 1, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (1, 1, 1, 0))
#
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (2, 2, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (2, 2, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (2, 2, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (2, 2, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (2, 2, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (2, 2, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (2, 2, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (2, 2, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (2, 2, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (2, 2, 1, 0))
#
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (2, 3, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (2, 3, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (2, 3, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (2, 3, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (2, 3, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (2, 3, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (2, 3, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (2, 3, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (2, 3, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (2, 3, 1, 0))
#
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (1, 4, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (1, 4, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (1, 4, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (1, 4, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (1, 4, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (1, 4, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (1, 4, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (1, 4, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (1, 4, 1, 0))
cursor.execute('INSERT INTO rooms(roomType, floor, locationID, currentOccupants) VALUES(?, ?, ?, ?)', (1, 4, 1, 0))

cursor.execute('INSERT INTO roomTypes(roomName, rentAmount, maxOccupants) VALUES(?, ?, ?)', ('2-person sharing', 9500, 2))
cursor.execute('INSERT INTO roomTypes(roomName, rentAmount, maxOccupants) VALUES(?, ?, ?)', ('4-person sharing', 8500, 4))

cursor.execute('INSERT INTO locations(locationName, locationAddress) VALUES(?, ?)', ('Main building', 'South C'))

cursor.execute('INSERT INTO transactionTypes(transactionName) VALUES(?)', ('Rent',))
cursor.execute('INSERT INTO transactionTypes(transactionName) VALUES(?)', ('Rent deposit',))
cursor.execute('INSERT INTO transactionTypes(transactionName) VALUES(?)', ('Electricity & Water',))
cursor.execute('INSERT INTO transactionTypes(transactionName) VALUES(?)', ('Refund',))

worker.commit()
worker.close()
