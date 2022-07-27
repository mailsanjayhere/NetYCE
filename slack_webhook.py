import requests
import sys
import json

# Simple argument  validation
if(len(sys.argv) < 2):
  print("ERROR: slack_webhook.py Argument missing")
  exit()

def payload_text():
  text = ""
  for a in (sys.argv[2:]):
    text = text + a + " "
  return(text)

######## Arguments #######
webhook = sys.argv[1] # https://hooks.slack.com/services/XXXX/XXXX/XXXX
payload = {"text": payload_text()} # {"text": "Hello, World!"}

def validate_url(url):
  import re
  regex = re.compile(
    r'^(?:http)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

  if re.match(regex, url) is  None:
    print("ERROR: The url: %s is Invalid" % url)  # in case json is invalid
    exit()

def send_slack_message(payload, webhook):
  return requests.post(webhook, json.dumps(payload))

# Run the script
if __name__ == '__main__':
  validate_url(webhook)  # webhook URL validation
  result = send_slack_message(payload, webhook)
  print(result.status_code)
  print(result.text)
