# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class CaptchaCaptchastore(models.Model):
    challenge = models.CharField(max_length=32)
    response = models.CharField(max_length=32)
    hashkey = models.CharField(unique=True, max_length=40)
    expiration = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'captcha_captchastore'


class Deviceinfo(models.Model):
    device_name = models.CharField(primary_key=True, max_length=255)
    device_chinese_name = models.CharField(max_length=255, blank=True, null=True)
    data_name = models.CharField(max_length=255)
    data_chinese_name = models.CharField(max_length=255, blank=True, null=True)
    table_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'deviceinfo'
        unique_together = (('device_name', 'data_name'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Domaininfo(models.Model):
    domain_name = models.CharField(max_length=20)
    table_name = models.CharField(max_length=20)
    domain_chinese_name = models.CharField(max_length=200, blank=True, null=True)
    domaintype = models.CharField(max_length=20, blank=True, null=True)
    isoptional = models.IntegerField(blank=True, null=True)
    optional = models.CharField(max_length=2000, blank=True, null=True)
    isrealtime = models.IntegerField(blank=True, null=True)
    scale = models.IntegerField(blank=True, null=True)
    pre = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'domaininfo'


class Influxsite(models.Model):
    no = models.IntegerField(primary_key=True)
    site_no = models.CharField(max_length=255)
    site_name = models.CharField(max_length=255)
    site_chinese_name = models.CharField(max_length=255, blank=True, null=True)
    ip = models.CharField(max_length=64, blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)
    user = models.CharField(max_length=255, blank=True, null=True)
    passwd = models.CharField(max_length=255, blank=True, null=True)
    database = models.CharField(max_length=255, blank=True, null=True)
    database_chinese_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'influxsite'


class LoginUser(models.Model):
    name = models.CharField(unique=True, max_length=128)
    password = models.CharField(max_length=256)
    email = models.CharField(unique=True, max_length=254)
    sex = models.CharField(max_length=32)
    c_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'login_user'


class Siteinfo(models.Model):
    site_name = models.CharField(primary_key=True, max_length=255)
    site_chinese_name = models.CharField(max_length=50, blank=True, null=True)
    site_level = models.CharField(max_length=5, blank=True, null=True)
    site_address = models.CharField(max_length=255, blank=True, null=True)
    site_longitude = models.FloatField(blank=True, null=True)
    site_latitude = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'siteinfo'


class Tableinfo(models.Model):
    table_name = models.CharField(primary_key=True, max_length=20)
    type = models.IntegerField(blank=True, null=True)
    table_chinese_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tableinfo'
