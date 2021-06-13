# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2021-06-13
### Changed
 - files and systemtags href are now in standard format (not URL, i.e not '%20' but ' ')
 - for optimization : add exclude parameter on ensure_tree_exists

## [0.2.0] - 2021-05-25
### Changed
 - python2 compatibility
 - refactored again and add a generic result api
 - add systemtags support
 - addition of an option to set alternate auth method and usage as session (working with instruction `with NextCloud as nxc:`)
 - `Nextcloud(json_output=…)` attribute is now deprecated and useless, because almost all result are dict-like
 - addition of AUTHORS.rst, CHANGELOG.md, test.sh
 - update requirements versions to allow to use plugin with pytest
 - moving descriptive content setup.py to setup.cfg; and add a shortcut to publish in PyPi
 - 100% tests passing


## [0.1] - 2019-03-19
### EnterpriseyIntranet/nextcloud-API
 - included dynamic functions assignement
 - refactored to split wrappers
 - added setup.py and all tests
### Main Contributors
 - Matěj Týč `@matejak <https://github.com/matejak>` active from 2018
 - Danil Topchiy  `@danil-topchiy <https://github.com/danil-topchiy>` active 2018-2019


[0.2.0]: https://github.com/luffah/nextcloud-API/compare/6869dd15cca1553713c132d07c967c1bf25d80f5...0.2.0
