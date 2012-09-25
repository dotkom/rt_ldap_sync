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
from rt_ldap_sync.models import RtGroup, RtUser, RtGroupMember, USER_DEFINED

class Command(BaseCommand):
    help = 'Synchronizes the LDAP groups and membership to RequestTracker'

    def handle(self, *args, **options):
        self.ldap_username_list =['norangsh', 'sigurf']
        self.ldap_user_group_map = {
            'norangsh': ['xdotkom'],
            'sigurf': ['dotkom']
        }

        self.stdout.write("This management command doesn't exactly nothing atm!")
        groups_to_create = RtGroup.objects.find_groups_not_listed(['dotkom', 'xdotkom'])
        if groups_to_create:
            for group in groups_to_create:
                RtGroup.objects.create(name=group, typed=USER_DEFINED)

        ldap_username_list = ['norangsh', 'sigurf']

        rt_users = RtUser.objects.filter(name__in=ldap_username_list)
        for user in rt_users:
            user_groups = self._get_groups_from_ldap_user(user)

            for group in RtGroupMember.objects.extra_ldap_groups(user, user_groups):
                RtGroupMember.objects.create(group=RtGroup.objects.get(name=group), member=user)

            RtGroupMember.objects.filter(group__in=RtGroupMember.objects.extra_rt_groups(user, user_groups), member=user).delete()


    def _get_groups_from_ldap_user(self, ldap_username):
        try:
            return self.ldap_user_group_map[ldap_username]
        except KeyError:
            return []
