"""RT LDAP Sync tests"""
import unittest
import mock
import simpleldap

from django.db import IntegrityError
from django.test import TestCase

from rt_ldap_sync.ldap import LdapController
from rt_ldap_sync.models import RtGroup, USER_DEFINED, RT_QUEUE_ROLE, RtUser, RtGroupMember, USER_ID_DEFAULT


class User(TestCase):
    """Testcases involving User"""
    def setUp(self):
        self.user1 = RtUser.objects.create(name='norangsh')

    def test_returns_my_username(self):
        self.assertEqual('norangsh', self.user1.name)

class Group(TestCase):
    def setUp(self):
        self.group2 = RtGroup.objects.create(name='awesomegroup', domain=RT_QUEUE_ROLE)
        self.ldap_groups = ['awesomegroup', 'foo']

    def test_returns_null_if_groupname_matches_but_not_user_defined(self):
        self.assertNotEqual(USER_DEFINED, self.group2.domain)
        self.assertFalse(RtGroup.objects.has_group('awesomegroup'))

    def test_returns_true_if_group_found_and_user_defined(self):
        self.group1 = RtGroup.objects.create(name='awesomegroup', domain=USER_DEFINED)
        self.assertEqual(USER_DEFINED, self.group1.domain)
        self.assertTrue(RtGroup.objects.has_group('awesomegroup'))

    def test_missing_ldap_groups(self):
        self.group1 = RtGroup.objects.create(name='awesomegroup', domain=USER_DEFINED)


        self.assertEquals(['foo'], RtGroup.objects.find_groups_not_listed(self.ldap_groups))
        self.assertEquals(['foo'], RtGroup.objects.find_groups_not_listed(reversed(self.ldap_groups)))

        self.assertEquals(['bar', 'foo'], RtGroup.objects.find_groups_not_listed(self.ldap_groups+['bar']))
        self.assertEquals(['bar', 'foo'], RtGroup.objects.find_groups_not_listed(['bar']+self.ldap_groups))

    def test_find_groups_not_listed_not_failing_on_empty_list_or_none(self):
        self.assertEquals([], RtGroup.objects.find_groups_not_listed(None))
        self.assertEquals([], RtGroup.objects.find_groups_not_listed([]))

        self.group1 = RtGroup.objects.create(name='group', domain=USER_DEFINED)
        self.assertEquals([], RtGroup.objects.find_groups_not_listed(None))
        self.assertEquals([], RtGroup.objects.find_groups_not_listed([]))

    def test_find_groups_not_listed_has_all_groups_already(self):
        self.group1 = RtGroup.objects.create(name='group', domain=USER_DEFINED)
        self.assertEquals([], RtGroup.objects.find_groups_not_listed(['group']))

    def test_find_groups_not_listed_unsorted_groups_input(self):
        self.assertEquals(['bar', 'foo'], RtGroup.objects.find_groups_not_listed(['bar', 'foo']))
        self.assertEquals(['bar', 'foo'], RtGroup.objects.find_groups_not_listed(['foo', 'bar']))

    def test_not_return_if_not_listed_in_ldap_groups(self):
        self.group1 = RtGroup.objects.create(name='awesomegroup', domain=USER_DEFINED)

        RtGroup.objects.create(name='not_listed_in_ldap_groups', domain=USER_DEFINED)
        self.assertEquals(['foo'], RtGroup.objects.find_groups_not_listed(self.ldap_groups))

class GroupMember(TestCase):
    """Testcases involving group membership"""
    def setUp(self):
        self.root = RtUser.objects.create(name='root', id=USER_ID_DEFAULT)
        self.user1 = RtUser.objects.create(name='norangsh')
        self.group1 = RtGroup.objects.create(name='dotkom', domain=USER_DEFINED)

    def test_add_user_to_group(self):
        self.assertEqual(0, RtGroupMember.objects.filter(group=self.group1).count())

        try:
            self.member = RtGroupMember.objects.create(group=self.group1, member=self.user1)
        except Exception, e:
            print e
            self.fail(msg='Exception thrown, see above for details')

        self.assertEqual(1, RtGroupMember.objects.filter(group=self.group1).count())

    def test_remove_user_from_group(self):
        self.member = RtGroupMember.objects.create(group=self.group1, member=self.user1)
        self.assertEqual(1, RtGroupMember.objects.filter(group=self.group1).count())

        RtGroupMember.objects.filter(group=self.group1, member=self.user1).delete()

        self.assertEqual(0, RtGroupMember.objects.filter(group=self.group1).count())

    def test_fail_to_add_duplicate_user_to_same_group(self):
        self.assertEqual(0, RtGroupMember.objects.filter(group=self.group1).count())
        self.member = RtGroupMember.objects.create(group=self.group1, member=self.user1)
        self.assertEqual(1, RtGroupMember.objects.filter(group=self.group1).count())
        self.assertRaises(IntegrityError, lambda: RtGroupMember.objects.create(group=self.group1, member=self.user1))

    def test_get_extra_groups_from_ldap(self):
        self.member = RtGroupMember.objects.create(group=self.group1, member=self.user1)

        ldap_groups = ['dotkom', 'foobar']

        self.assertEquals(['foobar'],  RtGroupMember.objects.extra_ldap_groups(self.user1, ldap_groups))

    def test_extra_groups_from_rt(self):
        RtGroupMember.objects.create(group=self.group1, member=self.user1)
        self.group_xdotkom = RtGroup.objects.create(name='xdotkom', domain=USER_DEFINED)
        RtGroupMember.objects.create(group=self.group_xdotkom, member=self.user1)

        self.assertEqual(2, RtGroupMember.objects.filter(member=self.user1).count())


        ldap_groups = ['dotkom']

        self.assertEquals(['xdotkom'], RtGroupMember.objects.extra_rt_groups(self.user1, ldap_groups))

    def test_extra_groups_both_both_sides(self):
        RtGroupMember.objects.create(group=self.group1, member=self.user1)
        self.group_xdotkom = RtGroup.objects.create(name='xdotkom', domain=USER_DEFINED)
        RtGroupMember.objects.create(group=self.group_xdotkom, member=self.user1)

        ldap_groups = ['dotkom', 'trollkom']
        extra_ldap = RtGroupMember.objects.extra_ldap_groups(self.user1, ldap_groups)
        extra_rt = RtGroupMember.objects.extra_rt_groups(self.user1, ldap_groups)

        self.assertEqual(['trollkom', 'xdotkom'], sorted(extra_ldap + extra_rt))


#class Troll(object):
#    class Connection(object):
#        def __init__(self, hostname, port, bind_dn, bind_pw, encryption):
#            pass

class LDAPTestCase(unittest.TestCase):


    def setUp(self):
        mock_ldap = mock.MagicMock(simpleldap)
        self.module = LdapController(mock_ldap)

    def _mock_valid_connection(self):
        connection_mock = mock.MagicMock(name='LdapController._connection')
        connection_mock.return_value = True
        self.module.Connection = connection_mock
        #setattr(self.module, '_connection', connection_mock)

    def test_connect_fail_no_hostname(self):
        self.assertRaises(ValueError, lambda: self.module.connect(None, 412))

    def test_connect_hostname_set(self):
        self.module.connect('a_hostname', 666, None, None)
        self.assertEquals('a_hostname', getattr(self.module, 'hostname'))

    def test_connect_fail_no_port(self):
        self.assertRaises(ValueError, lambda: self.module.connect('foo', None))
        self.assertRaises(ValueError, lambda: self.module.connect('foo', 0))

    def test_connect_fail_port_below_1(self):
        self.assertRaises(ValueError, lambda: self.module.connect('foo', -1))

    def test_connect_fail_port_above_65535(self):
        self.assertRaises(ValueError, lambda: self.module.connect('foo', 65536))

    def test__mock_valid_connection(self):
        self._mock_valid_connection()
        self.assertFalse(getattr(self.module, '_connection'))
        self.assertFalse(self.module.is_connected())
        self.assertTrue(self.module.connect('foo', 1))
        self.assertTrue(getattr(self.module, '_connection'))
        self.assertTrue(self.module.is_connected())

        self.module.close()
        self.assertFalse(getattr(self.module, '_connection'))
        self.assertFalse(self.module.is_connected())

    def test_connect_min_valid_port(self):
        self._mock_valid_connection()
        self.assertTrue(self.module.connect('foo', 1))

    def test_connect_max_valid_port(self):
        self._mock_valid_connection()

        self.assertTrue(self.module.connect('foo', 65535))


    def test_if_protocol_is_ssl_on_ssl_port(self):
        self.module.connect('foo', 636, None, 'ldap')
        self.assertEquals('ldaps', getattr(self.module, '_protocol'))

    def test_if_protocol_ldap(self):
        self.module.connect('foo', 2323, None, 'ldap')
        self.assertEquals('ldap', getattr(self.module, '_protocol'))

    def test_if_protocol_ldaps(self):
        self.module.connect('foo', 2323, None, 'ldaps')
        self.assertEquals('ldaps', getattr(self.module, '_protocol'))

    def test_get_users_without_connection(self):
        self.assertRaises(simpleldap.ConnectionException, lambda: self.module.get_users())

    def test_get_groups_without_connection(self):
        self.assertRaises(simpleldap.ConnectionException, lambda: self.module.get_groups('foo'))

    def test_get_users_single_row(self):
        self._mock_valid_connection()
        self.assertTrue(self.module.connect('foo', 1))
        self.module._get_search_results = mock.MagicMock(name='ldap._get_search_results')
        self.module._get_search_results.return_value = [{'cn': ['tadaa'], 'objectclass': ['account', 'posixAccount'], 'loginshell': ['/bin/bash'], 'uidnumber': ['1000'], 'gidnumber': ['1000'], 'gecos': ['Rockj'], 'homedirectory': ['/home/rockj'], 'uid': ['tadaa']}]

        #[{'cn': ['tadaa'], 'objectclass': ['account', 'posixAccount'], 'loginshell': ['/bin/bash'], 'uidnumber': ['1000'], 'gidnumber': ['1000'], 'gecos': ['Rockj'], 'homedirectory': ['/home/rockj'], 'uid': ['tadaa']}]
        results = self.module.get_users()
        self.assertEquals(1, len(results))

        self.assertEquals('tadaa', results[0]['cn'][0])
        self.assertTrue(results[0]['uidnumber'])
        self.assertEquals('1000', results[0]['uidnumber'][0])

    def test_get_users_multiple_rows(self):
        self._mock_valid_connection()
        self.assertTrue(self.module.connect('foo', 1))
        self.module._get_search_results = mock.MagicMock(name='ldap._get_search_results')
        self.module._get_search_results = mock.MagicMock(name='ldap._get_search_results')
        self.module._get_search_results.return_value = [{'cn': ['tadaa'], 'objectclass': ['account', 'posixAccount'], 'loginshell': ['/bin/bash'], 'uidnumber': ['1000'], 'gidnumber': ['1000'], 'gecos': ['Rockj'], 'homedirectory': ['/home/rockj'], 'uid': ['tadaa']}, {'cn': ['jadda'], 'objectclass': ['account', 'posixAccount'], 'loginshell': ['/bin/bash'], 'uidnumber': ['1001'], 'gidnumber': ['1001'], 'gecos': ['Rasasd'], 'homedirectory': ['/home/sdaf'], 'uid': ['jadda']}]

        results = self.module.get_users()

        self.assertEquals(2, len(results))

    def test_get_groups_no_groups(self):
        self._mock_valid_connection()
        self.assertTrue(self.module.connect('foo', 1))
        self.module._get_search_results = mock.MagicMock(name='ldap._get_search_results')
        self.module._get_search_results.return_value = []
        results = self.module.get_groups('unknown_user')

        self.assertEquals(0, len(results))

    def test_get_groups_for_user_single_row(self):
        self._mock_valid_connection()
        self.assertTrue(self.module.connect('foo', 1))
        self.module._get_search_results = mock.MagicMock(name='ldap._get_search_results')
        self.module._get_search_results.return_value = [{'cn': ['dotkom'],
                                                         'gidNumber': ['22'],
                                                         'memberUid': ['fellingh',
                                                                       'norangsh'
                                                                       'dagolap'],
                                                         'objectClass': ['posixGroup', 'top']}]
        results = self.module.get_groups('norangsh')

        self.assertEquals(1, len(results))

    def test_get_groups_for_user_multiple_rows(self):
        self._mock_valid_connection()
        self.assertTrue(self.module.connect('foo', 1))
        self.module._get_search_results = mock.MagicMock(name='ldap._get_search_results')
        self.module._get_search_results.return_value = [{'cn': ['dotkom'],
                                                         'gidNumber': ['42'],
                                                         'memberUid': ['glennrub',
                                                                       'fellingh',
                                                                       'norangsh'],
                                                         'objectClass': ['posixGroup', 'top']},
                                                        {'cn': ['komiteer'],
                                                         'gidNumber': ['69'],
                                                         'memberUid': ['glennrub',
                                                                       'dagolap',
                                                                       'norangsh'],
                                                         'objectClass': ['posixGroup', 'top']}]

        results = self.module.get_groups('norangsh')
        self.assertEquals(2, len(results))
        self.assertEquals([['dotkom'], ['komiteer']], [group['cn'] for group in results])
