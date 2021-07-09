# pf_cert_manager
Automatically import certs into pfSense.

# About
This script is mainly intended for automating the import of LetsEncrypt certs
from other machines into pfSense, via the pfSense API package. There are 6
things the script needs to know in order to work properly:

* The address / hostname of your pfSense router (by default, we assume your default gateway)
* The path to your cert file (certbot can tell us this)
* The path to your private key (certbot can tell us this)
* Your pfSense API client id
* Your pfSense API client token.
* Should we ignore cert errors when communicating with pfSense? (default: no)

However, if you have a typical LetsEncrypt setup, we can figure out / assume 4
of the 6 pieces of information.

# Setup
Install the [pfSense API](https://github.com/jaredhendrickson13/pfsense-api)
package on your firewall, and create an API token. Save the created token
(shown only once near the top of the page on token creation), and then client
ID (shown near the bottom) into a credentials file for later use. The credentials
file should be a yaml file named `.pf_cert_manager.conf`, formatted like so:
```yaml
client_id: your_id_here
client_token: your_token_here
```
The credentials file can either be placed in the home directory of the user
running the script, or you can specify where the config file is located. Test
that the credentials are working correctly by running `pf_cert_manager get`,
and see that you get a good response back. If the script can't find a config
file, it should tell you where it was looking for one.

Next, add a deploy hook to your certbot cron job like so:
```
--deploy-hook 'pf_cert_manager import'
```
In which case, the full command might look something like this:
```
certbot renew --post-hook 'systemctl reload nginx' --deploy-hook 'pf_cert_manager import'
```
In a case like this, you should make sure to put the config file in the home of
the user running the job, or you should add the `--config` option like so:
```
certbot renew --post-hook 'systemctl reload nginx' --deploy-hook 'pf_cert_manager import --config /path/to/.pf_cert_manager.conf'
```

See `pf_cert_manager import -h` for the full list of options if you have an
atypical setup, or aren't using LetsEncrypt certs.
