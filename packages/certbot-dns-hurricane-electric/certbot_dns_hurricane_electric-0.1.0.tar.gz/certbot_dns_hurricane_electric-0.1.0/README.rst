certbot-dns-hurricane-electric
======================================

`Hurricane Electric DNS <https://dns.he.net>`_ Authenticator plugin for `Certbot <https://certbot.eff.org>`_

----

Installation
------------

Install `certbot-dns-hurricane-electric <https://pypi.org/project/certbot-dns-hurricane-electric/>`_ to your Certbot's environment with pip. For example, the line below works for me after running ``certbot-auto``.

.. code-block:: bash

  $ sudo /opt/eff.org/certbot/venv/bin/pip install cerbot-dns-hurricane-electric

You can also use ``git+https://github.com/studioeng/certbot-dns-hurricane-electric.git`` or clone the repository and install from the directory, but pip is recommended.

Example usage
-------------

Create a configuration file with your username and password:

.. code-block:: ini

  dns_hurricane_electric_user = Your HE username
  dns_hurricane_electric_pass = Your HE password

and chmod it to ``600``:

.. code-block:: bash

  $ chmod 600 dns_he.ini

Then request a certificate with something like:

.. code-block:: bash

  domain="mail.example.com"
  email="email@example.com"

  $ certbot-auto certonly \
    --server https://acme-v02.api.letsencrypt.org/directory \
    --rsa-key-size 2048 \
    --preferred-challenges dns \
    --authenticator dns-hurricane_electric \
    --dns-hurricane_electric-credentials /data/dns_he.ini \
    --dns-hurricane_electric-propagation-seconds 30 \
    --domain "${domain}" \
    --email "${email}" \
    --agree-tos

You're done!

| ``--dns-hurricane_electric-credentials`` specifies the configuration file path.
| ``--dns-hurricane_electric-propagation-seconds`` controls the duration waited for the DNS record(s) to propagate.

These are stored in cerbot's renewal configuration, so they'll work on your automatic renewals.

Credits
-------

The original plugin by @tsaarist has been unchanged for a number of years.
