#!/usr/bin/env python3

# Imports {{{
# builtins
import json
import os
import pathlib

# 3rd party
import click

# local modules
from pf_cert_import.utils import CertManager, get_default_gateway_name

# }}}


@click.group(
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
)
def cli():
    ...


def config_options(func):
    options = [
        click.option(
            "--client-id",
            prompt=True,
            default=lambda: os.environ.get("CLIENT_ID", None),
            help="pfSense API client ID. Can also be passed via the CLIENT_ID environment variable."
        ),
        click.option(
            "--client-token",
            prompt=True,
            default=lambda: os.environ.get("CLIENT_TOKEN", None),
            help="pfSense API client token. Can also be passed via the CLIENT_TOKEN environment variable."
        ),
        click.option(
            "--host",
            default=lambda: os.environ.get("HOST", get_default_gateway_name()),
            help=f"Hostname of the pfSense router  [default: {get_default_gateway_name()}]",
        ),
    ]

    for option in options:
        func = option(func)

    return func


@cli.command(
    "import",
    help="Import a certificate into pfSense."
)
@config_options
@click.option(
    "-p",
    "--path",
    type=pathlib.Path,
    default=lambda: os.environ.get("RENEWED_LINEAGE", None),
    help="Path prefix to the cert and private key files. If using the typical LetsEncrypt setup, this will be '/etc/letsencrypt/live/<your site>'. When running from a certbot deploy hook, export the 'RENEWED_LINEAGE' shell variable to autopopulate this argument, or manually pass it in.",
)
@click.option(
    "-c",
    "--cert-chain",
    type=pathlib.Path,
    default="fullchain.pem",
    show_default=True,
    help="Path to the cert chain file (relative to '--path' if it is specifed).",
)
@click.option(
    "-k",
    "--private-key",
    type=pathlib.Path,
    default="privkey.pem",
    show_default=True,
    help="Path to the private key file (relative to '--path' if it is specifed).",
)
@click.option(
    "-i",
    "--import-name",
    default="LetsEncrypt",
    show_default=True,
    help="Name of the cert on import into pfSense. If a cert with the same name already exists in pfSense, it is deleted and replaced.",
)
def _import(client_id, client_token, host, path, cert, private_key, name):
    manager = CertManager(host, client_id, client_token)

    existing = manager.get()
    if existing.get(name, None):
        manager.delete(name)

    if path:
        cert = path / cert
        private_key = path / private_key

    resp = manager.create(cert, private_key, name)
    print(resp)


@cli.command(
    help="Get a list of existing certs from pfSense."
)
@config_options
def get(client_id, client_token, host):
    manager = CertManager(host, client_id, client_token)
    print(json.dumps(manager.get(), indent=4))


if __name__ == "__main__":
    cli()
