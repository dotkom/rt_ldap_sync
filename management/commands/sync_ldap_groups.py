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

class Command(BaseCommand):
    help = 'Synchronizes the LDAP groups and membership to RequestTracker'

    def handle(self, *args, **options):
        self.stdout.write("This management command doesn't exactly nothing atm!")
