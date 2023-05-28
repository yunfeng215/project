import RPi.GPIO as GPIO
import time
import matplotlib.pyplot as plt
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.message import EmailMessage
from email.mime.base import MIMEBase

# email setting

GPIO.setmode(GPIO.BOARD)

# port numbers
buzzer = 8
trig = 10
echo = 12

# input / output
GPIO.setup(buzzer, GPIO.OUT)
GPIO.setup(trig, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)

# pitch freq
C = 261.63
D = 293.66
E = 329.63
F = 349.23
G = 392
A = 440
B = 493.88

def get_distance():
    # set Trigger to HIGH
    GPIO.output(trig, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(trig, GPIO.LOW)
 
    StartTime = 0
    StopTime = 0
 
    # save StartTime
    while GPIO.input(echo) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(echo) == 1:
        StopTime = time.time()
 
    TimeElapsed = StopTime - StartTime
    distance = (TimeElapsed * 34300) / 2
    return distance

def sing_note(note, t):
    cur = 0
    T = 1 / note
    while cur < t:
        GPIO.output(GPIO.HIGH)
        time.sleep(T / 2)
        GPIO.output(buzzer, GPIO.LOW)
        time.sleep(T / 2)
        cur += T
    GPIO.output(GPIO.LOW)
    time.sleep(0.2)

def sing_twinkle():
    sing_note(C, 0.5)
    sing_note(C, 0.5)
    sing_note(G, 0.5)
    sing_note(G, 0.5)
    sing_note(A, 0.5)
    sing_note(A, 0.5)
    sing_note(G, 1)

    sing_note(F, 0.5)
    sing_note(F, 0.5)
    sing_note(E, 0.5)
    sing_note(E, 0.5)
    sing_note(D, 0.5)
    sing_note(D, 0.5)
    sing_note(C, 1.5)

dist_list = []

def update_data(dist):
    dist_list.append(dist)
    plt.plot(range(len(dist_list)), dist_list)
    plt.savefig('dist.png')

# email setting
from_mail = "xxxxx@xxx.com"
from_password = "token_donot_tell_others"

to_mail = "xxxxx@xxx.com"

smtp_server = "smtp.xxx.com"
smtp_port = 465

def send_email():
    msg = MIMEMultipart()
    msg['Subject'] = 'Distance Not In Range!'
    msg['From'] = from_mail
    msg['To'] = to_mail
    msg.preamble = 'Distance Not In Range!'

    with open('dist.png', 'rb') as fp:
        img = MIMEImage(fp.read())
        img.add_header('Content-Disposition', 'attachment', filename='dist_plot.png')
        img.add_header('X-Attachment-Id', '0')
        img.add_header('Content-ID', '<0>')
        fp.close()
        msg.attach(img)

    # Attach HTML body
    msg.attach(MIMEText(
        '''
        <html>
            <body>
                <h1 style="text-align: center;">Dist Report</h1>
                <p>Distance Not In Range!</p>
                <p><img src="cid:0"></p>
            </body>
        </html>'
        ''',
        'html', 'utf-8'))


    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    server.ehlo()
    server.login(from_mail, from_password)

    server.sendmail(from_mail, [from_mail, to_mail], msg.as_string())
    server.quit()

while 1:
    dist = get_distance()
    update_data(dist)
    if dist < 90:
        sing_twinkle()
        send_email()
    time.sleep(5)
