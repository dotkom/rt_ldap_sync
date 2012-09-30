"""Tiny LDAP Wrapper module"""
import simpleldap

class LdapController(object):
    def __init__(self, ldap_impl=None):
        self._connection = None
        self._search_base = None
        self._encryption = None
        self._protocol = None

        self._ldap_impl = ldap_impl if ldap_impl else simpleldap


    def connect(self, hostname, port, search_base='', in_protocol='ldaps'):
        """Connect to LDAP server

        """
        if self._connection:
            return self._connection

        if not hostname:
            raise ValueError('Requires a hostname to connect to')
        if not port or (port and (port <= 0 or port > 65535)):
            raise ValueError('Requires a valid port number.')

        if port == 636:
            self._protocol = 'ldaps'
        else:
            self._protocol = in_protocol

        self.hostname = hostname
        self.port = port
        self._search_base = search_base

        if self._protocol == 'ldapi':
            self._encryption = None
        elif self._protocol == 'ldaps':
            self._encryption = 'ssl'
        else:
            self._encryption = 'tls'



        self._connection = self._ldap_impl.Connection(self.hostname, self.port, '', '', self._encryption )
        return self._connection


    def close(self):
        if self._connection:
            self._connection.close()
        self._connection = None

    def is_connected(self):
        """are we connected to LDAP server?

        :returns true if we are.
        """
        return self._connection is not None

    def get_connection(self):
        return self._connection


    def _get_search_results(self, filter, base_dn, attributes):
        return self.get_connection().search(filter, base_dn, attributes)

    def get_users(self, search_options=None):
        """Get users from LDAP

        :search_options may contain search parameters as:

        BaseDN, isUserSubTree?, ObjectClass required, UserFilter
        UserIDAttribute, RealNameAttribute, EmailAttribute
        """

        #base_dn_users = 'ou=people'
        base_dn_users = self._search_base
        #filter_object_class = '(objectClass=inetOrgPerson)'
        filter_object_class = '(objectClass=posixAccount)'
        attribute_user_id = 'uid'
        attribute_real_name = 'displayName'
        attribute_email = 'mail'

        if self.is_connected():
            return self._get_search_results(filter_object_class, base_dn_users, None)
        else:
            raise simpleldap.ConnectionException('You need to be connected')

    def get_groups(self, username, search_options=None):
        """Get group given user name

        :username groupmembership for given username
        :search_options search meta for group fetching:

        GroupTye (Static|Dynamic), BaseDN, Group Subtree,
        ObjectClass, GroupIDAttribute, GroupMemberAttribute,
        GroupMemeberFormat"""

        is_group_type_static = True
        base_dn_group = 'ou=groups'
        filter_object_class = 'posixGroup'
        attribute_group_id = 'cn'
        attribute_member = 'memberUid'

        filter = "(&(objectClass=%s)(&(%s=*)(%=%)))".format(
            filter_object_class,
            attribute_group_id,
            attribute_member,
            username
        )
        base_filter = "%s,%s".format(base_dn_group, self._search_base)

        if self.is_connected():
            return self.get_connection().search(filter, base_filter,
            [attribute_group_id, attribute_member])
        else:
            raise simpleldap.ConnectionException('You need to be connected')



