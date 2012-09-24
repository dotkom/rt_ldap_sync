"""Models used in rt-ldap-sync app

Models that represent database tables in RequestTracker
"""

from django.db import models


ROOT_ID_ACCOUNT = 0

class Group(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=255)
    domain = models.CharField(max_length=64)
    type = models.CharField(max_length=64)
    instance = models.IntegerField()
    creator = models.IntegerField(default=ROOT_ID_ACCOUNT, null=False, blank=False)
    created = models.DateTimeField(auto_now=True)
    last_updated_by = models.IntegerField(default=ROOT_ID_ACCOUNT, null=False, blank=False, db_column='lastupdatedby')
    last_updated = models.DateTimeField(auto_now=True, db_column='lastupdated')

    class Meta:
        db_table = 'groups'
