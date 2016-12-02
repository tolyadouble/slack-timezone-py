import re
import sys
import json
import time
import requests
from operator import itemgetter
from collections import OrderedDict
from slackclient import SlackClient
from datetime import datetime, timedelta

try:
    TOKEN = str(sys.argv[1])
except IndexError:
    raise ValueError('Error: use first argument as key')

show_nickname = False
try:
    if str(sys.argv[2]) == '-n':
        show_nickname = True
except IndexError:
    pass


def timezone_sort(s):
    return int(s['tz_offset'])


def prepare_emoji(localtime):
    hours = str(localtime[:2])
    if hours == '00':
        hours = '12'
    if hours[:1] == '0':
        hours = hours[1:]
    if int(hours) > 12:
        hours = int(hours) - 12
    return ':clock%s:' % str(hours)

# Get users timezones
response = requests.get("https://slack.com/api/users.list?token=%s&pretty=1" % TOKEN)
slack_members = json.loads(response.text)['members']
timezones = []

for member in slack_members:
    try:
        tz = {
                'user_id': member['id'],
                'nickname': member['name'],
                'tz_offset': member['tz_offset'],
                'tz': member['tz']
            }
    except KeyError:
        # skip users without timezone
        pass
    timezones.append(tz)

timezones = sorted(timezones, key=timezone_sort)

slack_client = SlackClient(TOKEN)

# Listen message event
if slack_client.rtm_connect():
    while True:
        message_object = slack_client.rtm_read()
        if len(message_object) > 0 and 'text' in message_object[0]:
            try:
                initial_time = ''
                message_text = message_object[0]['text']
                user_object = [m for m in timezones if m['user_id'] == message_object[0]['user']][0]
                initial_tz = user_object['tz']
                utc_delta = int(user_object['tz_offset'] if str(user_object['tz_offset'])[:1] != '+'
                                else str(user_object['tz_offset'])[1:])

                # try to find '#time' string
                try:
                    if re.findall(r"#time", message_text)[0] == '#time':
                        # try to find H:M time
                        try:
                            initial_time = datetime.strptime(re.findall(r"\d+:\d+", message_text)[0], '%H:%M')
                        except:
                            # set current time
                            ts = float(message_object[0]['ts'])
                            ts = (datetime.utcfromtimestamp(ts) + timedelta(seconds=utc_delta)).strftime('%H:%M')
                            initial_time = datetime.strptime(ts, '%H:%M')
                except:
                    # prevent no time spam
                    pass

                if not initial_time:
                    raise Exception('No', 'Time')

                initial_utc = initial_time - timedelta(seconds=utc_delta) + timedelta(days=1)

                show_timezones = {}
                for user_timezone in timezones:
                    utc_user_delta = int(user_timezone['tz_offset'] if str(user_timezone['tz_offset'])[:1] != '+'
                                         else str(user_timezone['tz_offset'])[1:])

                    if user_timezone['tz'] not in show_timezones and user_timezone['tz'] is not None:
                        show_timezones[user_timezone['tz']] = (
                            (initial_utc + timedelta(seconds=utc_user_delta)).strftime("%d %H:%M"),
                        )
                    if user_timezone['tz'] in show_timezones and show_nickname:
                        show_timezones[user_timezone['tz']] += (user_timezone['nickname'],)

                show_timezones = OrderedDict(sorted(show_timezones.items(), key=itemgetter(1)))
                msg = ''
                for local_tz, info in show_timezones.iteritems():
                    localtime = info[0][3:]
                    msg += '%s %s `%s`' % (prepare_emoji(localtime), localtime, local_tz)

                    if show_nickname:
                        msg += ' - `'
                        for nick in set(info[1:]):
                            msg += '%s, ' % nick
                        msg = msg[:-2] + '`'

                    msg += ' \n'

                slack_client.api_call(
                    "chat.postMessage", channel=message_object[0]['channel'], text=msg,
                    username='time_bot', icon_emoji=':timer_clock:'
                )
            except:
                # prevent stopping script
                pass

        time.sleep(1)
else:
    print "Connection Failed"
