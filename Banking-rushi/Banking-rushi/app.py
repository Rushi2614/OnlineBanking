from flask import Flask, render_template, request
import mysql.connector as c
import random
from datetime import datetime

app = Flask(__name__)

class Global:
    accno = ''
g = Global()

@app.route('/')
def index():
    return render_template('Login.html')

@app.route('/Registration')
def Registration():
    return render_template('Registration.html')

@app.route('/Login')
def Login():
    return render_template('Login.html')

@app.route('/BankTransfer')
def BankTransfer():
    return render_template('banktranfer.html')

@app.route('/Logout')
def Logout():
    return render_template('logout.html')


@app.route('/Profile')
def Profile():
    con = c.connect(host="localhost", user="root",
                        passwd="hari@9RUSHI", database="bankingsystem")
    cursor = con.cursor()
    querry = "select * from usertable where accountnumber = '{}'".format(g.accno)
    cursor = con.cursor()
    cursor.execute(querry)
    records = cursor.fetchall()
    print(records)
    return render_template('myprofile.html', name=records[0][0], account_number=records[0][-1], balance=records[0][-2], phone_number=records[0][2], email=records[0][3])


@app.route('/RegisterUser', methods = ['POST'])
def RegisterUser():
    name = request.form['uname']
    password = request.form['password']
    phonenumber = request.form['phone']
    email = request.form['email']
    balance = request.form['balance']
    accountNumber = ''
    helper = [1,2,3,4,5,6,7,8,9]
    for i in range(97, 97+27):
        helper.append(chr(i))
    for i in range(10):
        accountNumber += str(random.choice(helper))
    con = c.connect(host="localhost", user="root",
                        passwd="hari@9RUSHI", database="bankingsystem")
    cursor = con.cursor()
    querry = 'insert into usertable (name, password, phonenumber, email, balance, accountnumber) values(%s,%s,%s,%s,%s,%s)'
    values = (name, password, phonenumber, email, balance, accountNumber)
    cursor.execute(querry, values)
    con.commit()
    return render_template('registrationSucess.html', account_number=accountNumber)

@app.route('/ValidateUser', methods = ['POST'])
def ValidateUser():
    name = request.form['uname']
    password = request.form['password']
    con = c.connect(host="localhost", user="root",
                        passwd="hari@9RUSHI", database="bankingsystem")
    cursor = con.cursor()
    querry = "select * from usertable where accountnumber = '{}' and password = '{}'".format(name, password)
    cursor = con.cursor()
    cursor.execute(querry)
    records = cursor.fetchall()
    if len(records) >= 1:
        g.accno = name
        return render_template('Homepage.html')
    return render_template('Invalid.html')

@app.route('/Balance')
def Balance():
    con = c.connect(host="localhost", user="root",
                        passwd="hari@9RUSHI", database="bankingsystem")
    cursor = con.cursor()
    querry = "select * from usertable where accountnumber = '{}'".format(g.accno)
    cursor = con.cursor()
    cursor.execute(querry)
    records = cursor.fetchall()
    print(records)
    return render_template('balance.html', name=records[0][0], account_number=records[0][-1], balance=records[0][-2])

@app.route('/UpdateBalance', methods = ['POST'])
def UpdateBalance():
    newbal = request.form['new_balance']
    con = c.connect(host="localhost", user="root",
                        passwd="hari@9RUSHI", database="bankingsystem")
    cursor = con.cursor()
    querry = "select * from usertable where accountnumber = '{}'".format(g.accno)
    cursor.execute(querry)
    records = cursor.fetchall()
    x = str(int(newbal) + int(records[0][-2]))
    query = "UPDATE usertable SET balance = '{}' WHERE accountnumber = '{}'".format(x, g.accno)
    cursor.execute(query)
    con.commit()
    return render_template('balanceupdate.html', name=records[0][0], account_number=records[0][-1], balance=x)
    
@app.route('/TransferAmount', methods=['POST'])
def TransferAmount():
    sender_account = request.form['sender_account']
    sender_password = request.form['sender_password']
    receiver_account = request.form['receiver_account']
    amount = request.form['amount']
    status = 'passed'
    con = c.connect(host="localhost", user="root",
                        passwd="hari@9RUSHI", database="bankingsystem")
    cursor = con.cursor()
    querry = "select * from usertable where accountnumber = '{}' and password = '{}'".format(sender_account, sender_password)
    cursor = con.cursor()
    cursor.execute(querry)
    senderDetails = cursor.fetchall()
    print(senderDetails)
    if len(senderDetails) == 0:
        status = 'Failed'
    querry = "select * from usertable where accountnumber = '{}'".format(receiver_account)
    cursor = con.cursor()
    cursor.execute(querry)
    recieverDetails = cursor.fetchall()
    print(recieverDetails)
    if len(recieverDetails) == 0:
        status = 'Failed'
    if int(senderDetails[0][4]) < int(amount):
        status = 'Failed'
    if status == 'passed':
        modifiedSenderBal = str(int(senderDetails[0][4]) - int(amount))
        modifiedReciverBal = str(int(recieverDetails[0][4]) + int(amount))
        query = "UPDATE usertable SET balance = '{}' WHERE accountnumber = '{}'".format(modifiedSenderBal, senderDetails[0][-1])
        cursor.execute(query)
        con.commit()
        query1 = "UPDATE usertable SET balance = '{}' WHERE accountnumber = '{}'".format(modifiedReciverBal, recieverDetails[0][-1])
        cursor.execute(query1)
        con.commit() 
        current_datetime = datetime.now()
        querry = 'insert into transaction (senderacc, reciveracc, amount, status, time_stamped) values(%s,%s,%s,%s,%s)'
        values = (sender_account, receiver_account, amount, status, current_datetime)
        cursor.execute(querry, values)
        con.commit()
    if status == 'Failed':
         return render_template('invalidTrans.html')
    return render_template('transucess.html')
    

@app.route('/TransferHistory')
def TransferHistory():
    con = c.connect(host="localhost", user="root",
                        passwd="hari@9RUSHI", database="bankingsystem")
    cursor = con.cursor()
    querry = "select * from transaction where senderacc = '{}'".format(g.accno)
    cursor = con.cursor()
    cursor.execute(querry)
    transferDetails = cursor.fetchall()
    ans = []
    for i in transferDetails:
        a = []
        a.append(i[3])
        a.append(i[2])
        a.append('--')
        a.append(i[1])
        a.append(i[4])
        ans.append(a)
    print(ans)
    querry = "select * from transaction where reciveracc = '{}'".format(g.accno)
    cursor = con.cursor()
    cursor.execute(querry)
    transferDetails = cursor.fetchall()
    for i in transferDetails:
        a = []
        a.append(i[3])
        a.append('--')
        a.append(i[2])
        a.append(i[0])
        a.append(i[4])
        ans.append(a)
    print(ans)
    return render_template('TransactionHistory.html', transactions = ans)

app.run(debug=True)