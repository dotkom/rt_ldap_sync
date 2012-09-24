"""RT LDAP Sync tests"""
from django.test import TestCase
from rt_ldap_sync.models import RtGroup, USER_DEFINED, RT_QUEUE_ROLE, RtUser, RtGroupMember


class User(TestCase):
    """Testcases involving User"""
    def setUp(self):
        self.user1 = RtUser.objects.create(name='norangsh')

    def test_returns_my_username(self):
        self.assertEqual('norangsh', self.user1.name)

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

class GroupMember(TestCase):
    """Testcases involving group membership"""
    def setUp(self):
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
        self.assertRaises(RtGroupMember.objects.create(group=self.group1, member=self.user1))
        self.assertEqual(1, RtGroupMember.objects.filter(group=self.group1).count())


