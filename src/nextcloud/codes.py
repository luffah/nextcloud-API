# -*- coding: utf-8 -*-
"""
Define all known return code from OwnCloud/NextCloud API
"""


class ShareType:
    """ Share types (for files_sharing app)"""
    USER = 0
    GROUP = 1
    PUBLIC_LINK = 3
    FEDERATED_CLOUD_SHARE = 6


class Permission:
    """ Permission for Share have to be sum of selected permissions """
    READ = 1
    UPDATE = 2
    CREATE = 4
    DELETE = 8
    SHARE = 16
    ALL = 31


class ExternalApiCodes:
    """ HTTP codes values for External API """
    SUCCESS = 100
    UNAUTHORIZED = 401
    SERVER_ERROR = 996
    NOT_AUTHORIZED = 997
    NOT_FOUND = 998
    UNKNOWN_ERROR = 999


class ProvisioningCode:
    """ HTTP codes values for Provisioning API """
    SUCCESS = 100
    INVALID_INPUT_DATA = 101
    FAILED = 102
    CREATION_FAILED = 103
    INSUFFICENT_PRIVILIEGES = 104
    CHANGE_FAILED = 105


class OCSCode:
    """ HTTP codes values for OCS API """
    SUCCESS_V1 = 100
    SUCCESS_V2 = 200
    FAILURE = 400
    NOT_FOUND = 404
    SYNC_CONFLICT = 409


class WebDAVCode:
    """ HTTP codes values for DAV API """
    CREATED = 201
    NO_CONTENT = 204
    MULTISTATUS = 207
    NOT_AUTHENTICATED = 401
    ALREADY_EXISTS = 405
    CONFLICT = 409
    PRECONDITION_FAILED = 412


QUOTA_UNLIMITED = -3
