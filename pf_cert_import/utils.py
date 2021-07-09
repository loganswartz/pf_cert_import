#!/usr/bin/env python3

# Imports {{{
# builtins
import base64
import json
import socket

# 3rd party
import netifaces
import requests
from urllib3.contrib import pyopenssl

# }}}


def get_canonical_name(ip):
    try:
        name = socket.getnameinfo((ip, 0), 0)[0]
        return name
    except IndexError:
        return None


def get_default_gateway():
    try:
        gateways = netifaces.gateways()
        default = gateways["default"][netifaces.AF_INET][0]
        return default
    except IndexError:
        return None


def tls_cert_names(host, port=443):
    x509 = pyopenssl.OpenSSL.crypto.load_certificate(
        pyopenssl.OpenSSL.crypto.FILETYPE_PEM,
        pyopenssl.ssl.get_server_certificate((host, port)),
    )
    return [name for type, name in pyopenssl.get_subj_alt_name(x509)]


def get_default_gateway_name():
    default = get_default_gateway()
    name = get_canonical_name(default)
    if name is None:
        return None

    resolved = socket.gethostbyname(name)
    return name if default == resolved else None


class CertManager(object):
    def __init__(self, host, client_id, client_token):
        self.host = host
        self.id = client_id
        self.token = client_token
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"{client_id} {client_token}"})
        self.session.verify = False

    @property
    def endpoint(self):
        return f"https://{self.host}/api/v1/system/certificate"

    def create(self, cert, private_key, name):
        with cert.open("rb") as c:
            with private_key.open("rb") as p:
                payload = {
                    "method": "import",
                    "cert": base64.b64encode(c.read()),
                    "key": base64.b64encode(p.read()),
                    "descr": name,
                    "active": True,
                }

        return self.session.post(self.endpoint, json=payload)

    def delete(self, name):
        payload = {
            "descr": name,
        }

        return self.session.delete(self.endpoint, json=payload)

    def get(self):
        return json.loads(self.session.get(self.endpoint).text)

