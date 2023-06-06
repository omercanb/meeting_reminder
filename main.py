import datetime
import smtplib
from email.message import EmailMessage
from string import Template
from pathlib import Path

SELF_NAME = "name"
SENDER = "sender@gmail.com"
PASSWORD = "1234"

class Recipient():
    def __init__(self, name, adress, tz_offset:int, city:str):
        self.name = name
        self.adress = adress
        self.tz = datetime.timezone(datetime.timedelta(hours=tz_offset), name=city)

recipients = [
    Recipient("r1", "r1@gmail.com", 2, "Spain"),
    Recipient("r2", "r2@gmail.com", 2, "Italy"),
    Recipient("r3", "r3@hotmail.com", -7, "Los Angeles"),
]

test_recipients = [
    Recipient("t1", "t1@gmail.com", 2, "Italy"),
]

#UTC datetime
meeting_datetime = {
    "year": 2023,
    "month": 6,
    "day": 6,
    "hour": 18,
    "minute": 30,
}

#Used to output the time left until a meeting as a formatted string.
def strfdelta(tdelta:datetime.timedelta):

    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)

    if d["days"] != 0:
        return "{days} days".format(**d) if d["days"] > 1 else "{days} day".format(**d)
    
    if d["hours"] != 0 and d["minutes"] != 0:
        r = ""
        r += "{hours} hours" if d["hours"] > 1 else "{hours} hour "
        r += "and "
        r += "{minutes} minutes" if d["minutes"] > 1 else "{minutes} minute"
        return r.format(**d) 
    
    if d["minutes"] != 0:
        return "{minutes} minutes".format(**d) if d["minutes"] > 1 else "{minutes} minute".format(**d)


def send_mails(recipients):
    meeting = (datetime.datetime(**meeting_datetime, tzinfo = datetime.timezone.utc))
    time_until_meeting = (datetime.datetime(**meeting_datetime, tzinfo = datetime.timezone.utc) 
                          - datetime.datetime.now(tz = datetime.timezone.utc))
    html = Template(Path("message.html").read_text())

    for r in recipients:
        email = EmailMessage()
        email["from"] = "SwordDuck"
        email["subject"] = f"Meeting on {meeting.strftime('%B %d')}"
        email["to"] = r.adress
        html_substitutions = {
        "name": r.name,
        "utc_time": meeting.strftime("%A, %B %d, %H:%M"),
        "local_time": meeting.astimezone(r.tz).strftime("%A, %B %d, %H:%M"),
        "city": r.tz,
        "time_until_meeting": strfdelta(time_until_meeting),
        "self": str(SELF_NAME)
        }
    
        email.set_content(html.substitute(html_substitutions),"html")

        with smtplib.SMTP(host="smtp.gmail.com",port=587) as smpt:
            smpt.ehlo()
            smpt.starttls()
            smpt.login(SENDER,PASSWORD)
            smpt.send_message(email)
            print(f"Sent mail to {r.name}.")


if __name__ == "__main__":
    send_mails(test_recipients)


