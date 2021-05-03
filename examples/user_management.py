import sys
import os
from os.path import dirname
from os.path import join

sys.path.insert(0, join(dirname(__file__), 'src'))

from nextcloud import NextCloud

NEXTCLOUD_URL = "http://{}:80".format(os.environ['NEXTCLOUD_HOSTNAME'])
NEXTCLOUD_USERNAME = os.environ.get('NEXTCLOUD_ADMIN_USER')
NEXTCLOUD_PASSWORD = os.environ.get('NEXTCLOUD_ADMIN_PASSWORD')

# True if you want to get response as JSON
# False if you want to get response as XML
to_js = True

nxc = NextCloud(endpoint=NEXTCLOUD_URL, user=NEXTCLOUD_USERNAME, password=NEXTCLOUD_PASSWORD, json_output=to_js)

# Quick start
nxc.get_users()
new_user_id = "new_user_username"
add_user_res = nxc.add_user(new_user_id, "new_user_password321_123")
group_name = "new_group_name"
add_group_res = nxc.add_group(group_name)
add_to_group_res = nxc.add_to_group(new_user_id, group_name)
# End quick start

assert add_group_res.status_code == 100
assert new_user_id in nxc.get_group(group_name).data['users']
assert add_user_res.status_code == 100
assert add_to_group_res.status_code == 100

# remove user
remove_user_res = nxc.delete_user(new_user_id)
assert remove_user_res.status_code == 100
user_res = nxc.get_user(new_user_id)
assert user_res.status_code == 404
