NextCloud Python API
====================

Overview
--------

Python wrapper for NextCloud's API.

The lib tends to support most common features i.e. :

* User provisioning
* OCS Share
* WebDAV (files)
* Tags
* Activity app
* Notifications app
* LDAP configuration
* Capabilities
* Group Folders

Tested with :

* NextCloud 14, python 3.7 (automated test)
* NextCloud 20, python 2.7
* NextCloud 20, python 3.6

The main lines :

* `NextCloud(URL, auth=…)` provide you a connection manager. You can use it with `with … as nxc:` to open a session.
* The session is the connection object that make the requests.
* The requests are initiated by a requester associated to an API wrapper.
* API wrappers are the definition of how to use the NextCloud REST API : it provide functions that will be attached to the `NextCloud` object.
* Functions can return :
  - Response object with attributes `is_ok`, `data`. If `is_ok` is False, you can use `get_error_message`.
  - Data objects (File, Tag…) or None.
* Data objects are useable as dict object or with attribute. They provide operations. If the operation fails, you'll get an exception.

For quick start, check out `examples`_ and the `tests`_.

Install
-------

.. code-block:: sh
    
    # use 'pip3' for python3 or 'python -m pip' instead of pip
    pip install nextcloud-api-wrapper
    # the associated python lib is nammed 'nextcloud'
    # beware the conflicts


Fork Changes
------------

This version is a fork (mainly refactoring, fixes and optimization) of `nextcloud-API <https://github.com/EnterpriseyIntranet/nextcloud-API>`_ .

Testing
~~~~~~~
The integration to Travis and CodeCov provided by the original repository are lost.

There is now 2 branches `develop` and `main`.
All `tests`_ are validated using `test.sh docker` before merging `develop` to `main`.


Documentation
~~~~~~~~~~~~~
The integration with readthedoc.io is lost.
You still can build the documentation with Sphinx source.

Looking at the code docstrings is recommended.
Significative changes will be reported in `CHANGELOG.md` file.

Too, you can check out the original `nextcloud API documentation <https://nextcloud-api.readthedocs.io/en/latest/introduction.html>`_, but the use could have changed.


Contributing
------------

Pull Request
~~~~~~~~~~~~
According to the testing procedure, you shall fork and PR on branch `develop`.

.. _tests: https://github.com/luffah/nextcloud-API/tree/main/tests
.. _examples: https://github.com/luffah/nextcloud-API/tree/main/examples
