import time
from datetime import datetime
from django.shortcuts import render, HttpResponse
from plotly.offline import plot
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import urllib.parse
from django.conf import settings
from .models import Customer, SignUpVerification
from .plotly import Plotly
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from cryptography.fernet import Fernet
from .mail_sending import send_mail


# Create your views here.


# home page
def home(request):
    return render(request, 'basic.html')


# upload table
def table_upload(request):
    if "GET" == request.method:
        return render(request, 'dashboard/tables.html', {})
    else:
        excel_file = request.FILES["excel_file"]
        if ('.xlsx' in excel_file.name):
            df = pd.read_excel(excel_file)
            csv_file = df.to_csv(settings.MEDIA_ROOT + '/' + (excel_file.name).replace('.xlsx', '.csv'))
            request.session['file'] = (excel_file.name).replace('.xlsx', '.csv')
        if ('.csv' in excel_file.name):
            df = pd.read_csv(excel_file)
            csv_file = df.to_csv(settings.MEDIA_ROOT + '/' + excel_file.name)
            request.session['file'] = excel_file.name

        excel_data = list()
        excel_heading = list()
        path = str(settings.MEDIA_ROOT + '/' + request.session.get('file'))
        f = open(path, 'r')
        rows = []
        frow = list()
        i = 0
        for row in f:
            if i == 0:
                row = row[1:].strip('\n').split(',')
                excel_heading = row
                i = 1
            else:
                row = row.strip('\n').split(',')
                excel_data.append(row[1:])
    return render(request, "dashboard/tables.html", context={
        "excel_data": excel_data,
        "excel_heading": excel_heading})


# show table
def table(request):
    return render(request, 'dashboard/tables.html')


def show_table(request):
    path = str(settings.MEDIA_ROOT + '/' + request.session.get('file'))
    f = open(path, 'r')
    rows = []
    frow = list()
    i = 0
    for row in f:
        if i == 0:
            row = row[1:].strip('\n').split(',')
            frow = row
            i = 1
        else:
            row = row.strip('\n').split(',')
            rows.append(row[1:])
    return render(request, 'dashboard/show_table.html', context={'frow': frow,
                                                                 'rows': rows})


# graphs

# plotly page
def plotly(request):
    excel_data = list()
    excel_heading = list()
    path = str(settings.MEDIA_ROOT + '/' + request.session.get('file'))
    f = open(path, 'r')
    rows = []
    frow = list()
    i = 0
    for row in f:
        if i == 0:
            row = row[1:].strip('\n').split(',')
            excel_heading = row
            i = 1
        else:
            row = row.strip('\n').split(',')
            excel_data.append(row[1:])
    return render(request, 'dashboard/plotly.html', context={"excel_data": excel_data,
                                                             "excel_heading": excel_heading})


# plotly graph

def plotly_chart(request):
    df = pd.read_csv(settings.MEDIA_ROOT + '/' + request.session.get('file'))
    tab = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df[col] for col in df.columns],
                   fill_color='lavender',
                   align='left'))
    ])
    tab.update_layout(template="plotly_white")
    plot_div = None
    x = request.POST.get('x')
    y = request.POST.get('y')
    f = request.session.get('file')
    color = request.POST.get('color')
    graph = request.POST.get('graph')
    graph_list = []
    if graph == 'Scatter':
        plot_div = Plotly.Scatter(x, y, f, color)
    if graph == 'line':
        plot_div = Plotly.line(x, y, f, color)
    if graph == 'bar':
        plot_div = Plotly.bar(x, y, f, color)
    if graph == 'pie':
        plot_div = Plotly.pie(x, y, f, color)
    if graph == 'bubble':
        plot_div = Plotly.bubble(x, y, f, color)
    if graph == 'gantt':
        plot_div = Plotly.gantt(x, y, f, color)
    if graph == 'box':
        plot_div = Plotly.box(x, y, f, color)
    if graph == 'boxscatter':
        plot_div = Plotly.box_scatter(x, y, f, color)
    if graph == 'violin':
        plot_div = Plotly.violin(x, y, f, color)
    if graph == 'violin_box':
        plot_div = Plotly.violin_box(x, y, f, color)
    if graph == 'violin_box_scatter':
        plot_div = Plotly.violn_box_scatter(x, y, f, color)
    if graph == 'strip':
        plot_div = Plotly.strip(x, y, f, color)
    # table = plot(tab, output_type='div', include_plotlyjs=True)
    excel_data = list()
    excel_heading = list()
    path = str(settings.MEDIA_ROOT + '/' + request.session.get('file'))
    f = open(path, 'r')
    rows = []
    frow = list()
    i = 0
    for row in f:
        if i == 0:
            row = row[1:].strip('\n').split(',')
            excel_heading = row
            i = 1
        else:
            row = row.strip('\n').split(',')
            excel_data.append(row[1:])

    return render(request, 'dashboard/plotly.html', context={'plot_div': plot_div,
                                                             # 'table':table,
                                                             "excel_data": excel_data,
                                                             "excel_heading": excel_heading
                                                             })


def covid(request):
    return render(request, 'dashboard/covid.html')


# user login logout

def login(request):
    return render(request, 'login.html')


def signup(request):
    return render(request, 'register.html')


def register(request):
    fname = request.POST.get('firstname')
    lname = request.POST.get('lastname')
    uname = request.POST.get('username')
    pwd = request.POST.get('password')
    email = request.POST.get('email')
    cpassword = request.POST.get('cpassword')
    time_stamp = time.time()
    send_mail(email, "Verification mail", uname, time_stamp)
    usr = Customer.objects.filter(username=uname)
    if len(usr) == 0 and pwd == cpassword:
        newuser = SignUpVerification.objects.create(username=uname, password=pwd, first_name=fname, last_name=lname,
                                                    email=email, signup_timestamp=time_stamp)
        newuser.save()
        return render(request, 'alert-message.html', {"message_type": "info",
                                                      "message": "Mail has been sent to your email address, please verify it."})
    else:
        print("here")
        return render(request, 'register.html', {'error': 'This username already exists'})


# authenticate user

def auth_user(request):
    user = Customer.objects.filter(username=request.POST.get('username')).first()
    if user is not None:
        if user.password == request.POST.get('password'):
            request.session['user'] = user.user_id
            request.session['fname'] = user.first_name
            request.session['lname'] = user.last_name
            return render(request, 'basic.html', {})
        else:
            return render(request, 'login.html', {'message': "invalid password"})
    else:
        return render(request, 'login.html', {'message': "invalid username or password"})


# forgot password page
def reset(request):
    return render(request, 'email.html')


def confirmation(request, time_stamp):
    time_stamp = float(time_stamp)
    user = SignUpVerification.objects.filter(signup_timestamp=time_stamp).first()
    if user is None or user.signup_timestamp != float(time_stamp):
        return render(request, 'alert-message.html',
                      {"message_type": "fail", "message": "Can't Verified, Please try again"})
    elif user.signup_timestamp == float(time_stamp):
        SignUpVerification.objects.filter(signup_timestamp=time_stamp).delete()
        newuser = Customer.objects.create(username=user.username, password=user.password, first_name=user.first_name,
                                          last_name=user.last_name, email=user.email)
        newuser.save()
        return render(request, 'alert-message.html', {"message_type": "success", "message": "Verified Successfully"})


def resetpasswrodform(request):
    time_stamp = request.GET.get('stamp')
    user_id = request.GET.get('id')
    user = Customer.objects.filter(user_id=user_id).first()
    link_create_date = datetime.fromtimestamp(float(time_stamp))
    current_date = datetime.now()
    difference = current_date - link_create_date
    if difference.seconds > 300 or user is None or user.forgot_pwd_timestamp != float(time_stamp):
        return HttpResponse("URL is expired")
    else:
        return render(request, 'resetpassword.html', {"user_id": int(user_id)})


# forgot page email post request
def resetpassword(request):
    email = request.POST.get('email')
    usr = Customer.objects.filter(email=email)
    if (len(usr) != 0):
        sender_email = "your_email_address"
        receiver_email = usr[0].email
        strg = usr[0].user_id
        password = 'your_email_password'
        msg = MIMEMultipart('alternative')

        msg['Subject'] = "Visualize"
        msg['From'] = sender_email
        msg['To'] = receiver_email

        # Create the body of the message (a plain-text and an HTML version).
        text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"
        time_stamp = time.time()
        params = {'id': f"{strg}", 'stamp': f'{time_stamp}'}
        Customer.objects.filter(user_id=strg).update(forgot_pwd_timestamp=time_stamp)
        html = """\
        <html>
          <head></head>
          <body>
            <p>Hi!<br>
               Reset your password from below link<br>
               <hr>
               <a href="http://127.0.0.1:8000/dashboard/reset/password/form/""" + f"?{urllib.parse.urlencode(params)}" + """">Reset your Password</a> you wanted.
            </p>
          </body>
        </html>
        """
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, receiver_email, msg.as_string()
            )

        return render(request, 'login.html')
    return render(request, 'password.html', {'message': "email id does not exists."})


# reset password page post request
def password(request, user_id):
    id = user_id
    pwd = request.POST.get("password")
    cpwd = request.POST.get('cpassword')
    usr = Customer.objects.filter(user_id=user_id)
    if (len(usr) != 0):
        if (pwd == cpwd):
            Customer.objects.filter(user_id=user_id).update(password=pwd)
            return render(request, 'login.html')
        return render(request, 'resetpassword.html', {"error": "your password does not match with confirm password."})
    return render(request, 'resetpassword.html', {"error": "Email id does not exists."})


# logout
def logout(request):
    try:
        del request.session['user']
        del request.session['fname']
        del request.session['lname']
        del request.session['file']
    except KeyError:
        pass
    return render(request, 'basic.html')
