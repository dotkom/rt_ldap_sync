"""Models used in rt-ldap-sync app

Models that represent database tables in RequestTracker
"""

from django.db import models
from django.db.models import Q


USER_ID_DEFAULT = 0
GROUP_ID_DEFAULT = 0

class RtUser(models.Model):
    """Represents the 'users' table in RT"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, null=False)
    password = models.CharField(max_length=256)
    authtoken = models.CharField(max_length=16)
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
    creator = models.ForeignKey('self', default=USER_ID_DEFAULT, null=False, db_column='creator', related_name='user_creator_set')
    created = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey('self', default=USER_ID_DEFAULT, null=False, db_column='lastupdatedby', related_name='user_last_updated_by_set')
    last_updated = models.DateTimeField(auto_now=True, db_column='lastupdated')

    class Meta:
        db_table = 'users'



USER_DEFINED = 'UserDefined'
RT_QUEUE_ROLE = 'RT::Queue-Role'

class RTGroupManager(models.Manager):
    def has_group(self, name):
        return self.filter(name=name, domain=USER_DEFINED)

    def find_groups_not_listed(self, groups):
        if not groups:
            return []
        groups = sorted(groups)

        rt_groups = [x.name for x in self.filter(domain=USER_DEFINED).order_by('name')]
        if rt_groups:
            return filter(lambda x: x not in rt_groups, groups)
        else:
            return groups

class RtGroup(models.Model):
    """Represents the 'groups' table in RT"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=255)
    domain = models.CharField(max_length=64)
    type = models.CharField(max_length=64)
    instance = models.IntegerField(null=True)
    creator = models.ForeignKey(RtUser, default=USER_ID_DEFAULT, null=False, blank=False, db_column='creator', related_name='group_creator_set')
    created = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(RtUser, default=USER_ID_DEFAULT, null=False, blank=False, db_column='lastupdatedby', related_name='group_last_updated_by_set')
    last_updated = models.DateTimeField(auto_now=True, db_column='lastupdated')

    objects = RTGroupManager()

    def __repr__(self):
        return u'%s,%s,%s' % (self.name, self.description, self.domain)

    class Meta:
        db_table = 'groups'


class RtGroupMemberManager(models.Manager):
    def extra_ldap_groups(self, user, ldap_groups):
        """Returns a list of ldap groups not added in RT"""
        rt_groups = [x.group.name for x in self.filter(member=user, group__domain=USER_DEFINED).order_by('group__name').all()]
        return filter(lambda x: x not in rt_groups, ldap_groups)

    def extra_rt_groups(self, user, ldap_groups):
        """Returns a list of RT groups that is not a part of ldap_groups"""
        rt_groups = [x.group.name for x in self.filter(member=user, group__domain=USER_DEFINED).order_by('group__name').all()]
        return filter(lambda x: x not in ldap_groups, rt_groups)

class RtGroupMember(models.Model):
    """Represents the 'groupmembers' table in RT"""
    id = models.AutoField(primary_key=True, auto_created=True, default=None)
    group = models.ForeignKey(RtGroup, default=GROUP_ID_DEFAULT, db_column='groupid', null=False)
    member = models.ForeignKey(RtUser, default=USER_ID_DEFAULT, db_column='memberid', null=False)
    creator = models.ForeignKey(RtUser, default=USER_ID_DEFAULT, null=False, db_column='creator', related_name='groupmember_creator_set')
    last_updated_by = models.ForeignKey(RtUser, default=USER_ID_DEFAULT, null=False, db_column='lastupdatedby', related_name='groupmember_last_updated_by_set')
    last_updated = models.DateTimeField(auto_now=True, db_column='lastupdated')

    objects = RtGroupMemberManager()

    class Meta:
        db_table = 'groupmembers'
        unique_together = ('group', 'member')
