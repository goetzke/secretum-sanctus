import random
import sys
import logging
from datetime import datetime


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

    pairings = '%s' % (", ".join([str(p) for p in pairs]))

    return pairings


def main():

    # Configure logging
    now = datetime.today().strftime('%Y-%m-%d')
    logpath = LOG_PATH.format(now=now)
    configure_root_logger(LOG_LEVEL, logpath)
    LOGGER = 'secretum-sanctus'
    logger = logging.getLogger(LOGGER)

    # Attempt to match everyone
    givers, recipients = build_participant_lists()
    pairings = designate_recipients(givers, recipients)

    # Log results if successful
    logger.info('~' * 80)
    logger.info('Secretum Sanctus - {}'.format(now))
    logger.info('Participants: {}'.format(givers))
    logger.info(pairings)
    logger.info('~' * 80)


if __name__ == "__main__":
    sys.exit(main())
