# pf_cert_import
Automatically import certs into pfSense.

# About
This script is mainly intended for automating the import of LetsEncrypt certs
from other machines into pfSense.

# Setup
Install the [pfSense API](https://github.com/jaredhendrickson13/pfsense-api)
package on your firewall, and create an API token. Save the created token
(shown only once near the top of the page on token creation), and then client
ID (shown near the bottom) into a credentials file for later use.
