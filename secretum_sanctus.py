import argparse
import random
import sys
import logging
from datetime import datetime
import smtplib
import pytz
import time
import socket

header = """
   _____                     __                 _____                  __            
  / ___/___  _____________  / /__   ______ ___ / ___/____ _____  _____/ /__   _______
  \__ \/ _ \/ ___/ ___/ _ \/ __/ | / / __ `__ \\__ \/ __ `/ __ \/ ___/ __/ | / / ___/
 ___/ /  __/ /__/ /  /  __/ /_ | |/ / / / / / /__/ / /_/ / / / / /__/ /_ | |/ (__  ) 
/____/\___/\___/_/   \___/\__/ |___/_/ /_/ /_/____/\__,_/_/ /_/\___/\__/ |___/____/  

"""

MAX_ATTEMPTS = 5000

PEEPS = [
    {'name': 'Luke', 'email': 'luke@gmail.com'},
    {'name': 'Lily', 'email': 'lily@gmail.com'},
    {'name': 'Bruce', 'email': 'bruce@gmail.com'},
    {'name': 'Tony', 'email': 'tony@gmail.com'},
    {'name': 'Max', 'email': 'max@gmail.com'}
]

BAD_PAIRS = [
    'Luke, Lily'
]

LOG_FORMAT = '%(asctime)s | %(name)s | %(message)s'
LOG_LEVEL = logging.INFO
LOG_PATH = 'secretum_sanctus_{now}.log'

EMAIL_MESSAGE = '''
  Dear {giver},
  
  This year you are the Secret Santa for {recipient}. Have fun!
  
  The maximum spending limit this year is $50.
  
  Happy Holidays!
  
'''
EMAIL_HEADER = """Date: {date}
Content-Type: text/plain; charset="utf-8"
Message-Id: {message_id}
From: {frm}
To: {to}
Subject: {subject}

"""
EMAIL_CONFIG = {
    'SMTP_SERVER': 'smtp.gmail.com',
    'SMTP_PORT': 587,
    'USERNAME': 'you@gmail.com',
    'PASSWORD': 'your-password',
    'TIMEZONE': 'US/Eastern',
    'FROM': 'You <you@gmail.com>',
    'SUBJECT': 'Your secret santa recipient is {recipient}',
    'MESSAGE': EMAIL_MESSAGE,
    'HEADER': EMAIL_HEADER
}


def configure_root_logger(loglevel, logpath):
    # Logging Setup
    root = logging.getLogger()
    root.setLevel(loglevel)
    formatter = logging.Formatter(LOG_FORMAT)

    # Stream Handler
    sh = logging.StreamHandler()
    sh.setLevel(loglevel)
    sh.setFormatter(formatter)
    root.addHandler(sh)

    # File Handler
    fh = logging.FileHandler(logpath)
    fh.setLevel(loglevel)
    fh.setFormatter(formatter)
    root.addHandler(fh)


class Person:
    def __init__(self, name, email, invalid_recipients):
        self.name = name
        self.email = email
        self.invalid_recipients = invalid_recipients

    def __repr__(self):
        return "%s <%s>" % (self.name, self.email)


class Pair:
    def __init__(self, giver, recipient):
        self.giver = giver
        self.recipient = recipient

    def __repr__(self):
        return "%s ---> %s" % (self.giver.name, self.recipient.name)


def build_participant_lists(participants=PEEPS, bad_pairs=BAD_PAIRS):
    givers = []
    for person in participants:
        name = person['name']
        email = person['email']

        invalid_recipients = []
        for pair in bad_pairs:
            bad_couple = [n.strip() for n in pair.split(',')]
            if name in bad_couple:
                # Get other member of this couple
                for member in bad_couple:
                    if name != member:
                        invalid_recipients.append(member)

        person = Person(name, email, invalid_recipients)
        givers.append(person)

    return givers, givers[:]


def select_recipient(giver, recipients):
    choice = random.choice(recipients)
    if giver.name == choice.name or choice.name in giver.invalid_recipients:
        if len(recipients) is 1:
            raise Exception('Only one recipient left, try again')
        return select_recipient(giver, recipients)
    else:
        return choice


def create_pairs(givers, recipients):
    pairs = []

    for giver in givers:
        recipient = select_recipient(giver, recipients)
        recipients.remove(recipient)
        pairs.append(Pair(giver, recipient))

    return pairs


def designate_recipients(givers, recipients):
    pairs = None
    attempts = 0
    while attempts < MAX_ATTEMPTS:
        try:
            pairs = create_pairs(givers, recipients)
            break
        except Exception as e:
            attempts += 1

    if pairs is None:
        print('Exceeded max attempts ({})!!!'.format(MAX_ATTEMPTS))
        sys.exit()

    return pairs


def send_emails(pairs, logger):
    server = smtplib.SMTP(EMAIL_CONFIG['SMTP_SERVER'], EMAIL_CONFIG['SMTP_PORT'])
    server.starttls()
    server.login(EMAIL_CONFIG['USERNAME'], EMAIL_CONFIG['PASSWORD'])

    for pair in pairs:
        zone = pytz.timezone(EMAIL_CONFIG['TIMEZONE'])
        now = zone.localize(datetime.now())
        date = now.strftime('%a, %d %b %Y %T %Z')  # Sun, 21 Dec 2008 06:25:23 +0000
        message_id = '<%s@%s>' % (str(time.time()) + str(random.random()), socket.gethostname())
        frm = EMAIL_CONFIG['FROM']
        to = pair.giver.email
        subject = EMAIL_CONFIG['SUBJECT'].format(giver=pair.giver.name, recipient=pair.recipient.name)
        body = (EMAIL_CONFIG['HEADER'] + EMAIL_CONFIG['MESSAGE']).format(
            date=date,
            message_id=message_id,
            frm=frm,
            to=to,
            subject=subject,
            giver=pair.giver.name,
            recipient=pair.recipient.name,
        )
        result = server.sendmail(frm, [to], body)
        logger.info('Emailed {} <{}>'.format(pair.giver.name, to))

    server.quit()


def main():
    parser = argparse.ArgumentParser(prog="secretum_sanctus.py",
                                     description="")
    parser.add_argument('-e', '--email', required=False,
                        help='send emails',
                        action='store_true',
                        dest='email',
                        default=False)
    args = parser.parse_args()
    email = args.email

    # Configure logging
    now = datetime.today().strftime('%Y-%m-%d')
    logpath = LOG_PATH.format(now=now)
    configure_root_logger(LOG_LEVEL, logpath)
    LOGGER = 'secretum-sanctus'
    logger = logging.getLogger(LOGGER)

    # Attempt to match everyone
    givers, recipients = build_participant_lists()
    pairs = designate_recipients(givers, recipients)

    # Log results if successful
    logger.info('~' * 80)
    logger.info(header)
    # logger.info('Participants: {}'.format(givers))
    logger.info('Participants: {}'.format(givers))
    logger.info('Pairings: {}'.format(", ".join([str(p) for p in pairs])))
    if email:
        logger.info('Sending emails!')
        send_emails(pairs, logger)
    logger.info('~' * 80)


if __name__ == "__main__":
    sys.exit(main())
