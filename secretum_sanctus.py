import random
import sys
import os


CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yml')

MAX_ATTEMPTS = 5000

PEEPS = [
    {'name': 'Luke', 'email': 'luke@gmail.com'},
    {'name': 'Bruce', 'email': 'bruce@gmail.com'},
    {'name': 'Tony', 'email': 'tony@gmail.com'},
    {'name': 'Max', 'email': 'max@gmail.com'}
]


class Person:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return "%s <%s>" % (self.name, self.email)


class Pair:
    def __init__(self, giver, recipient):
        self.giver = giver
        self.recipient = recipient

    def __repr__(self):
        return "%s ---> %s" % (self.giver.name, self.recipient.name)


def select_recipient(giver, recipients):
    choice = random.choice(recipients)
    if giver.name == choice.name:
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


def main():

    givers = []
    for person in PEEPS:
        name = person['name']
        email = person['email']
        person = Person(name, email)
        givers.append(person)

    recipients = givers[:]

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

    test_pairings = '%s' % ("\n".join([str(p) for p in pairs]))

    print(test_pairings)


if __name__ == "__main__":
    sys.exit(main())
