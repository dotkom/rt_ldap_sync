"""RT LDAP Sync tests"""
from django.test import TestCase
from rt_ldap_sync.models import RtGroup


USER_DEFINED = 'UserDefined'
RT_QUEUE_ROLE = 'RT::Queue-Role'

class Group(TestCase):
    def setUp(self):
        self.group2 = RtGroup.objects.create(name='awesomegroup', domain=RT_QUEUE_ROLE)

    def test_returns_null_if_groupname_matches_but_not_user_defined(self):
        self.assertNotEqual(USER_DEFINED, self.group2.domain)
        self.assertFalse(RtGroup.objects.has_group('awesomegroup'))

    def test_returns_true_if_group_found_and_user_defined(self):
        self.group1 = RtGroup.objects.create(name='awesomegroup', domain=USER_DEFINED)
        self.assertEqual(USER_DEFINED, self.group1.domain)
        self.assertTrue(RtGroup.objects.has_group('awesomegroup'))
