"""Models used in rt-ldap-sync app

Models that represent database tables in RequestTracker
"""

from django.db import models


USER_ID_DEFAULT = 0
GROUP_ID_DEFAULT = 0

class RtUser(models.Model):
    """Represents the 'users' table in RT"""
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200, null=False)
    password = models.CharField(max_length=256)
    authtoken = models.CharField(16)
    comments = models.TextField()
    signature = models.TextField()
    emailaddress = models.CharField(max_length=120)
    free_form_contact_info = models.TextField(db_column='freeformcontactinfo')
    organization = models.CharField(max_length=200)
    realname = models.CharField(max_length=120)
    nickname = models.CharField(max_length=16)
    lang = models.CharField(max_length=16)
    email_encoding = models.CharField(max_length=16, db_column='emailencoding')
    web_encoding = models.CharField(max_length=16, db_column='webencoding')
    external_contact_info_id = models.CharField(max_length=100, db_column='externalcontactinfoid')
    contact_info_system = models.CharField(max_length=30, db_column='contactinfosystem')
    external_auth_id = models.CharField(max_length=100, db_column='externalauthid')
    auth_system = models.CharField(max_length=30, db_column='authsystem')
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
    creator = models.ForeignKey('self', default=USER_ID_DEFAULT, null=False, db_column='creator')
    created = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey('self', default=USER_ID_DEFAULT, null=False, db_column='lastupdatedby')
    last_updated = models.DateTimeField(auto_now=True, db_column='lastupdated')

    class Meta:
        db_table = 'users'


class RtGroup(models.Model):
    """Represents the 'groups' table in RT"""
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=255)
    domain = models.CharField(max_length=64)
    type = models.CharField(max_length=64)
    instance = models.IntegerField()
    creator = models.ForeignKey(RtUser, default=USER_ID_DEFAULT, null=False, blank=False, db_column='creator')
    created = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(RtUser, default=USER_ID_DEFAULT, null=False, blank=False, db_column='lastupdatedby')
    last_updated = models.DateTimeField(auto_now=True, db_column='lastupdated')

    class Meta:
        db_table = 'groups'

class RtGroupMember(models.Model):
    """Represents the 'groupmembers' table in RT"""
    id = models.IntegerField(primary_key=True)
    group_id = models.ForeignKey(RtGroup, default=GROUP_ID_DEFAULT, db_column='groupid', null=False)
    member_id = models.ForeignKey(RtUser, default=USER_ID_DEFAULT, db_column='memberid', null=False)
    creator = models.ForeignKey(RtUser, default=USER_ID_DEFAULT, null=False)
    last_updated_by = models.ForeignKey(RtUser, default=USER_ID_DEFAULT, null=False, db_column='lastupdatedby')
    last_updated = models.DateTimeField(auto_now=True, db_column='lastupdated')

    class Meta:
        db_table = 'groupmembers'
