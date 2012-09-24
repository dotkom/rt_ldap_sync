"""Models used in rt-ldap-sync app

Models that represent database tables in RequestTracker
"""

from django.db import models


ROOT_ID_ACCOUNT = 0

class User(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200, null=False)
    password = models.CharField(max_length=256)
    authtoken = models.CharField(16)
    comments = models.TextField()
    signature = models.TextField()
    emailaddress = models.CharField(max_length=120)
    freeformcontactinfo = models.TextField()
    organization = models.CharField(max_length=200)
    realname = models.CharField(max_length=120)
    nickname = models.CharField(max_length=16)
    lang = models.CharField(max_length=16)
    emailencoding = models.CharField(max_length=16)
    webencoding = models.CharField(max_length=16)
    externalcontactinfoid = models.CharField(max_length=100)
    contactinfosystem = models.CharField(max_length=30)
    externalauthid = models.CharField(max_length=100)
    authsystem = models.CharField(max_length=30)
    gecos = models.CharField(max_length=16)
    homephone = models.CharField(max_length=30)
    workphone = models.CharField(max_length=30)
    mobilephone = models.CharField(max_length=30)
    pagerphone = models.CharField(max_length=30)
    address1 = models.CharField(max_length=200)
    address2 = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip = models.CharField(max_length=16)
    country = models.CharField(max_length=50)
    timezone = models.CharField(max_length=50)
    pgpkey = models.TextField()
    creator = models.ForeignKey(User, default=ROOT_ID_ACCOUNT, null=False)
    created = models.DateTimeField(auto_now=True)
    lastupdatedby = models.ForeignKey(User, default=ROOT_ID_ACCOUNT, null=False)
    lastupdated = models.DateTimeField(auto_now=True)


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

class GroupMember(models.Model):
    id = models.IntegerField(primary_key=True)
    group_id = models.ForeignKey(Group, default=0, db_column='groupid', null=False)
    member_id = models.ForeignKey(User, default=0, db_column='memberid', null=False)
    creator = models.ForeignKey(User, default=0, null=False)
    last_updated_by = models.ForeignKey(User, default=0, null=False, db_column='lastupdatedby')
    last_updated = models.DateTimeField(auto_now=True, db_column='lastupdated')
