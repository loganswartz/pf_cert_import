#!/usr/bin/env python3

# Imports {{{
# builtins
import json
import os
import pathlib

# 3rd party
import click

# local modules
from pf_cert_manager.utils import CertManager, get_config, get_default_gateway_name

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
            "--config",
            default=pathlib.Path("~").expanduser() / ".pf_cert_manager.conf",
            type=pathlib.Path,
            show_default=True,
            help="Path to the credentials config file",
        ),
        click.option(
            "--client-id",
            default=lambda: os.environ.get("CLIENT_ID", None),
            help="pfSense API client ID. Can also be passed via the CLIENT_ID environment variable, or via a config file.",
        ),
        click.option(
            "--client-token",
            default=lambda: os.environ.get("CLIENT_TOKEN", None),
            help="pfSense API client token. Can also be passed via the CLIENT_TOKEN environment variable, or via a config file.",
        ),
        click.option(
            "--host",
            default=lambda: os.environ.get("HOST", get_default_gateway_name()),
            help=f"Hostname of the pfSense router  [default: {get_default_gateway_name()}]",
        ),
        click.option(
            "--no-verify-ssl",
            is_flag=True,
            help=f"Ignore SSL cert errors when communicating with pfSense. If you are communicating with the router via IP as opposed to a hostname, or your cert expired, this flag will always be needed.",
        ),
    ]

    for option in options:
        func = option(func)

    return func


@cli.command("import", help="Import a certificate into pfSense.")
@config_options
@click.option(
    "-p",
    "--path",
    type=pathlib.Path,
    default=lambda: os.environ.get("RENEWED_LINEAGE", None),
    help="Path prefix to the cert and private key files. If using the typical LetsEncrypt setup, this will be '/etc/letsencrypt/live/<your site>'. When running from a certbot deploy hook, this will be automatically picked up via the 'RENEWED_LINEAGE' environment variable.",
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
def _import(
    config,
    client_id,
    client_token,
    host,
    no_verify_ssl,
    path,
    cert_chain,
    private_key,
    import_name,
):
    client_id, client_token = config_override(config, client_id, client_token)
    manager = CertManager(host, client_id, client_token, no_verify_ssl)

    existing = [cert["descr"] for cert in manager.get().get("data", {}).get("cert", {})]
    if import_name in existing:
        manager.delete(import_name)

    if path:
        cert_chain = path / cert_chain
        private_key = path / private_key

    resp = manager.create(cert_chain, private_key, import_name)
    print(resp)


@cli.command(help="Get a list of existing certs from pfSense.")
@config_options
def get(config, client_id, client_token, host, no_verify_ssl):
    client_id, client_token = config_override(config, client_id, client_token)
    manager = CertManager(host, client_id, client_token, no_verify_ssl)

    print(json.dumps(manager.get(), indent=4))


def config_override(config: pathlib.Path, client_id, client_token):
    data = get_config(config)

    client_id = data["client_id"] if not client_id else client_id
    client_token = data["client_token"] if not client_token else client_token

    return client_id, client_token


if __name__ == "__main__":
    cli()
