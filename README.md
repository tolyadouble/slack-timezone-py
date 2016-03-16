## Slack Timezone Py

Convert string with time to your teammates time and timezone. If someone write time like - 22:00, slackbot show all
teammates time and timezones based on localtime of sender message.

![Screenshot](image.png?raw=true "Screenshot")

## Usage
* download or clone repo
* setup requirements (virtualenv is recommended) :
<pre>
pip install -r requirements.txt
</pre>
* run command :
<pre>
python slack-timezone-py.py YOUR_SLACK_TOKEN
</pre>
* if you want to see teammate nicknames near timezone please add '-n' :
<pre>
python slack-timezone-py.py YOUR_SLACK_TOKEN -n
</pre>

Inspired by
* https://github.com/caiosba/slack-timezone-converter

## References

* https://api.slack.com/web#basics
* https://api.slack.com/rtm
* https://github.com/slackhq/python-slackclient