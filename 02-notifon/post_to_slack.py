# coding: utf-8
import requests
url = ' https://hooks.slack.com/services/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'
data = { "Text": "Hello, world from python." }
requests.post(url, json=data)
 
data = { "text": "Hello, world from python." }
url = 'https://hooks.slack.com/services/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'
requests.post(url, json=data)
