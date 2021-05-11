# NextCloud Python api

[![Build Status](https://travis-ci.org/EnterpriseyIntranet/nextcloud-API.svg?branch=master)](https://travis-ci.org/EnterpriseyIntranet/nextcloud-API)
[![Documentation Status](https://readthedocs.org/projects/nextcloud-api/badge/?version=latest)](https://nextcloud-api.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/EnterpriseyIntranet/nextcloud-API/branch/master/graph/badge.svg)](https://codecov.io/gh/EnterpriseyIntranet/nextcloud-API)


## Overview

Python wrapper for NextCloud api

This is Python wrapper for NextCloud's API.
With it you can manage your NextCloud instances from Python scripts.

Tested with :
  * NextCloud 14, python 3.7 (automated test)
  * NextCloud 20, python 2.7
  * NextCloud 20, python 3.6


## FAQ


#### Which APIs does it support ?

Check out the corresponding [nextcloud API documentation](https://nextcloud-api.readthedocs.io/en/latest/introduction.html#which-api-does-it-support) section.


#### How do I use it?

Check out [examples](examples) and also check out the [unit tests directory](tests).


#### What is the difference between 'get_' and 'fetch_' methods ?
If you find similar methods `fetch_` and `get_`, the second one is probaly automatically created.
Methods nammed `get_` shall returns objects and usually use `fetch_` methods that allows to get a json output too.

#### What do I do if it doesn't work?

Don't run away and open a GitHub issue!
