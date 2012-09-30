"""Sync LDAP Groups management command

This management command will connect to LDAP,
and syncronhize group relationship from LDAP
to RequestTracker.

This is done like something like this I assume:

Fetch RTUsers and associated RTGroups.

Fetch LDAP Users and LDAP Groups

Create missing LDAP groups that aren't RTGroups
Process one user at the time and do:
* Add groups that the user is associated with in LDAP and the user doesn't have.
* Remove groups that the user isn't associated with anylonger in LDAP
"""
from django.core.management import BaseCommand
import itertools
from rt_ldap_sync.ldap import LdapController
from rt_ldap_sync.models import RtGroup, RtUser, RtGroupMember, USER_DEFINED

class Command(BaseCommand):
    args = '<ldap_group> <ldap_group ...>'
    help = 'Synchronizes the LDAP groups and membership to RequestTracker'

    def handle(self, *args, **options):
        self.ldap = LdapController()
        ldap_groups = list(itertools.chain.from_iterable([group['cn'] for group in self.ldap.get_groups()]))

        groups_to_create = RtGroup.objects.find_groups_not_listed(ldap_groups)
        if groups_to_create:
            for group in groups_to_create:
                RtGroup.objects.create(name=group, typed=USER_DEFINED)

        tmp_set_for_unique_usernames = set()
        for ldap_groupname in args:
            tmp_set_for_unique_usernames.update(self.ldap.get_groups_member(ldap_groupname))
        ldap_username_list = list(tmp_set_for_unique_usernames)

        rt_users = RtUser.objects.filter(name__in=ldap_username_list)
        for user in rt_users:
            user_groups = self._get_groups_from_ldap_user(user)

            for group in RtGroupMember.objects.extra_ldap_groups(user, user_groups):
                RtGroupMember.objects.create(group=RtGroup.objects.get(name=group), member=user)

            RtGroupMember.objects.filter(group__in=RtGroupMember.objects.extra_rt_groups(user, user_groups), member=user).delete()


    def _get_groups_from_ldap_user(self, ldap_username):
        return self.ldap.get_groups(ldap_username)
