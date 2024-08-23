Welcome to PCCE-API's documentation!
==============================================

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
.. image:: https://img.shields.io/badge/linting-pylint-yellowgreen
   :target: https://github.com/pylint-dev/pylint
.. image:: https://img.shields.io/badge/security-bandit-yellow.svg
   :target: https://github.com/PyCQA/bandit
.. image:: https://gitlab.com/th1nks1mple/pcce-api/badges/main/pipeline.svg
   :target: https://gitlab.com/th1nks1mple/pcce-api/-/commits/main
.. image:: https://gitlab.com/th1nks1mple/pcce-api/badges/main/coverage.svg
   :target: https://gitlab.com/th1nks1mple/pcce-api/-/commits/main
.. image:: https://img.shields.io/pypi/pyversions/pcce-api
   :target: https://pypi.org/project/pcce-api/
.. image:: https://img.shields.io/pypi/v/pcce-api
   :target: https://pypi.org/project/pcce-api/

PCCE-API is a Prisma Cloud Compute Edition API Client.

- Issue Tracker: https://gitlab.com/th1nks1mple/pcce-api/-/issues
- GitLab Repository: https://gitlab.com/th1nks1mple/pcce-api

Features
--------

- Implement the latest Prisma Cloud Compute Edition API.
- Use marshmallow library for validate schema data before send to server.

Installation
------------

To install the most recent published version to pypi, its simply a matter of
installing via pip:

.. code-block:: bash

   pip install pcce-api

If you're looking for bleeding-edge, then feel free to install directly from the
github repository like so:

.. code-block:: bash

   pip install git+git://gitlab.com/th1nks1mple/pcce-api.git#egg=pcce-api

Getting Started
---------------

Lets assume that we want to get the list of users that have been create on our
PCCE application.  Performing this action is as simple as the following:

.. code-block:: python

   from pcce import PCCE
   pcce = PCCE(url='http://console.domain',
                  username='username',
                  password='password')
   for user in pcce.users.list():
      print(user)

Documents
---------

https://pan.dev/compute/api/31-02/

License
-------

The project is licensed under the MIT license.
