"""Tiny LDAP Wrapper module"""

class LDAP(object):

        def connected(self, meta):
            """Connect to LDAP server"""
            pass

        def is_connected(self):
            """are we connected to LDAP server?

            :returns true if we are.
            """
            pass

        def get_users(self, search_options=None):
            """Get users from LDAP

            :search_options may contain search parameters as:

            BaseDN, isUserSubTree?, ObjectClass required, UserFilter
            UserIDAttribute, RealNameAttribute, EmailAttribute
            """
            pass

        def get_groups(self, username, search_options=None):
            """Get group given user name

            :username groupmembership for given username
            :search_options search meta for group fetching:

            GroupTye (Static|Dynamic), BaseDN, Group Subtree,
            ObjectClass, GroupIDAttribute, GroupMemberAttribute,
            GroupMemeberFormat"""
            pass
