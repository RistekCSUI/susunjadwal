import re
import requests
from app import app
from bs4 import BeautifulSoup
from six.moves import urllib_parse
from scraper.main import fetch_credential, DEFAULT_CREDENTIAL
from json.decoder import JSONDecodeError


SERVICE_URL = "http://127.0.0.1:3000/"
SSO_ROOT_URL = "https://sso.ui.ac.id"
AUTH_URL = f"{SSO_ROOT_URL}/cas2/login?service={SERVICE_URL}"
BASE_PATH = app.config["BASE_PATH"]


def get_ticket_from_sso_ui():
    try:
        username, password = fetch_credential(DEFAULT_CREDENTIAL)
    except TypeError:
        raise Exception('Credentials not found')

    if (username is not None) and (password is not None):
        # Open login page
        req = requests.Session()
        r = req.get(AUTH_URL, verify=False, allow_redirects=True)

        # Find form and all the input fields including the hidden (secret) one
        soup = BeautifulSoup(r.content, "html.parser")
        form = soup.find('form')
        fields = form.findAll('input')

        # Create form payload
        formdata = dict((field.get('name'), field.get('value'))
                        for field in fields)
        formdata['username'] = username
        formdata['password'] = password

        # Send payload to login URL
        post_url = urllib_parse.urljoin(SSO_ROOT_URL, form['action'])

        # Search ticket
        r = req.post(post_url, data=formdata, allow_redirects=True)
        ticket_match = re.search(r"\?ticket=((.*)-sso.ui.ac.id)", r.text)
        if ticket_match:
            return ticket_match.group(1)
        else:
            raise Exception('Ticket not found')
