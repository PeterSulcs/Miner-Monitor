#!/usr/bin/env python
import json
import requests
from secrets import SPARKPOST_KEY, ETHERMINE_URL, RECIPIENT

MIN_HASH_RATE = 15
MAX_TIME_SINCE = 20

def send_email(contents):
    print("Sending email")
    print(str(contents))
    r = requests.post('https://api.sparkpost.com/api/v1/transmissions',
        headers = {'Authorization':SPARKPOST_KEY,
        'Content-Type': 'application/json'},
        data=json.dumps({
            "options": {'sandbox': True},
            "content": {
            "from": "test@sparkpostbox.com",
            "subject": "Mining Alert",
            "text": str(contents)},
            "recipients": [{"address": RECIPIENT}]
        }))
    print(r.text)
    pass

def read_has_notified_down():
    with open('notified.json', 'r') as fid:
        d = json.load(fid)
    return d['HasBeenNotified']

def write_out_has_been_notified(boolean):
    with open('notified.json', 'w') as fid:
        json.dump({'HasBeenNotified': boolean}, fid)
    pass

if __name__ == "__main__":
    TOO_MUCH_TIME = False
    HASHRATE_LOW = False

    data = requests.get(ETHERMINE_URL)
    print(data)

    if data.status_code == requests.codes.ok:
        data = data.json()
        print(data['minerStats'])

        # Calculate time since lastSeen:
        since_last_seen = data['minerStats']['time']-data['minerStats']['lastSeen']
        print('Last seen in epoch ms: {}'.format(since_last_seen))
        in_minutes = float(since_last_seen) / 1000.0 / 60.0
        print('It has been {} minutes since the miner has last been seen.'.format(in_minutes))

        # Check time limit
        if in_minutes > MAX_TIME_SINCE:
            TOO_MUCH_TIME = True
            print("More than {} minutes since last seen!".format(MAX_TIME_SINCE))

        # Calculate hash rate:
        b = [a for a in data['hashRate'] if (a.isnumeric() or a == '.')]
        hashrate = float(''.join(b))
        print('The current hash rate is {}.'.format(hashrate))

        # Check hashrate limit
        if hashrate < MIN_HASH_RATE:
            HASHRATE_LOW = True
            print("Hashrate is below {}!".format(MIN_HASH_RATE))

        if HASHRATE_LOW or TOO_MUCH_TIME:
            if read_has_notified_down():
                print('Failure but user has already been notified...')
            else:
                print('Sending an email because failure is fresh...')
                send_email("Whoa! Hashrate = {}, Time Since Last Seen = {} min".format(
                    hashrate, in_minutes))
                write_out_has_been_notified(True)
                print('Setting notified to true to avoid spamming...')
        else:
            if read_has_notified_down():
                print('Whoa, massive successs, back online!')
                send_email("Hashrate = {} MH/s, Time Since Last Seen = {} min".format(
                    hashrate, in_minutes))
                write_out_has_been_notified(False)
            else:
                print('Success, but no one cares because things have been running smoothly...')


