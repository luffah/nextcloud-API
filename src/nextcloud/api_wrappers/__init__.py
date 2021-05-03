from nextcloud.base import API_WRAPPER_CLASSES

from .activity import Activity
from .apps import Apps
from .capabilities import Capabilities
from .federated_cloudshares import FederatedCloudShare
from .group import Group
from .group_folders import GroupFolders
from .notifications import Notifications
from .share import Share
from .user import User
from .user_ldap import UserLDAP
from .webdav import WebDAV
from .systemtags import SystemTags, SystemTagsRelation
