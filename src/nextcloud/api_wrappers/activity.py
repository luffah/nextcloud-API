# -*- coding: utf-8 -*-
"""
Activity API wrapper
See https://github.com/nextcloud/activity
    https://doc.owncloud.com/server/user_manual/apps/activity.html
    https://doc.owncloud.com/server/developer_manual/core/apis/
"""
from nextcloud import base


class Activity(base.OCSv2ApiWrapper):
    """ Activity API wrapper """
    API_URL = "/ocs/v2.php/apps/activity/api/v2/activity"

    def get_activities_filters(self):
        """
        Return OCSResponse with all activities filter in datas
        """
        return self.requester.get(url="filters")

    def get_activities(self, filter_name=None,
                       since=None, limit=None, object_type=None, object_id=None, sort=None):
        """
        Get an activity feed showing your file changes and other interesting things going on
        in your Nextcloud

        All args are optional

        Args:
            since (int): ID of the last activity that you’ve seen
            limit (int): How many activities should be returned (default: 50)
            filter_name (string): Name (id) of the filter (e.g. all, self, by,
                                 files_favorites, files, files_sharing, calendar,
                                 calendar_todo, comments, deck)
            object_type (string): Filter the activities to a given object.
                May only appear together with object_id
            object_id (string): Filter the activities to a given object.
                May only appear together with object_type
            sort (str, "asc" or "desc"): Sort activities ascending or descending (from the since)
                (Default: desc)

        Returns:
            OCSResponse
        """
        params = dict(
            since=since,
            limit=limit,
            object_type=object_type,
            object_id=object_id,
            sort=sort
        )

        if not filter_name:
            if params['object_type'] and params['object_id']:
                return self.requester.get(url='filter', params=params)
            return self.requester.get(params=params)
        return self.requester.get(url=filter_name, params=params)
