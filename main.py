import json

from requests import post

user = ''
password = ''
url_base = 'https://api.github.com/repos/incuna/incuna-education/hooks'
print url_base

data = [{
    'name':'irc',
    'config':{
        'server': '',
        'port': '6667',
        'room': '',
        'nick': 'GitHub',
        'password': '',
        'ssl': False,
        'message_without_join': True,
        'no_colors': False,
        'long_url': True,
        'notice': True,
    },
    'events': ['pull_request'],
    'active': True,
}]
data_json = json.dumps(data)
print data_json

r = post(url_base, auth=(user, password), data={'payload': data_json})
print r.status_code
print r.content
