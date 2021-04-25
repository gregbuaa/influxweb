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


class DatabaseGroup(models.Model):
    database_group_id = models.AutoField(primary_key=True)
    database_group_name = models.CharField(max_length=255, blank=True, null=True)
    database_number = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'database_group'


class DatabaseInfo(models.Model):
    db_id = models.AutoField(primary_key=True)
    sid = models.IntegerField(blank=True, null=True)
    dbgroup_id = models.IntegerField(blank=True, null=True)
    db_type = models.CharField(max_length=20, blank=True, null=True)
    nick_name = models.CharField(max_length=255, blank=True, null=True)
    db_name = models.CharField(max_length=255, blank=True, null=True)
    db_user = models.CharField(max_length=255, blank=True, null=True)
    db_password = models.CharField(max_length=255, blank=True, null=True)
    db_port = models.IntegerField(blank=True, null=True)
    comments = models.CharField(max_length=255, blank=True, null=True)
    mysqldb_type = models.CharField(max_length=20, blank=True, null=True)
    masterdb_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'database_info'


class DatabaseSplit(models.Model):
    split_id = models.AutoField(primary_key=True)
    split_key = models.CharField(max_length=255, blank=True, null=True)
    split_value = models.CharField(max_length=255, blank=True, null=True)
    db_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'database_split'


class DeviceInfo(models.Model):
    device_name = models.CharField(max_length=255, blank=True, null=True)
    device_chinese_name = models.CharField(max_length=255)
    data_name = models.CharField(max_length=255, blank=True, null=True)
    data_chinese_name = models.CharField(max_length=255)
    table_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'device_info'


class Deviceinfo2(models.Model):
    device_name = models.CharField(max_length=255, blank=True, null=True)
    device_chinese_name = models.CharField(max_length=255)
    data_name = models.CharField(max_length=255, blank=True, null=True)
    data_chinese_name = models.CharField(max_length=255)
    table_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'deviceinfo2'


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
    modified = models.IntegerField(blank=True, null=True)
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
    config_file = models.CharField(max_length=255, blank=True, null=True)

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


class Menu(models.Model):
    m_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, blank=True, null=True)
    p_id = models.IntegerField(blank=True, null=True)
    url = models.CharField(max_length=100, blank=True, null=True)
    m_type = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'menu'


class Siteinfo(models.Model):
    site_chinese_name = models.CharField(max_length=255, blank=True, null=True)
    site_name = models.CharField(max_length=255, blank=True, null=True)
    site_level = models.CharField(max_length=5, blank=True, null=True)
    site_address = models.CharField(max_length=255, blank=True, null=True)
    site_longitude = models.FloatField(blank=True, null=True)
    site_latitude = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'siteinfo'


class Tableinfo(models.Model):
    table_name = models.CharField(max_length=20)
    type = models.IntegerField(blank=True, null=True)
    table_chinese_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tableinfo'


class Telemetry(models.Model):
    site_name = models.CharField(max_length=25, blank=True, null=True)
    device_name = models.CharField(max_length=255, blank=True, null=True)
    data_name = models.CharField(max_length=255, blank=True, null=True)
    base = models.CharField(max_length=255, blank=True, null=True)
    offset = models.IntegerField(blank=True, null=True)
    ratio = models.IntegerField(blank=True, null=True)
    upper_limit = models.FloatField(blank=True, null=True)
    lower_limit = models.FloatField(blank=True, null=True)
    alarm_upper_limit = models.FloatField(blank=True, null=True)
    alarm_lower_limit = models.FloatField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    blocked = models.IntegerField(blank=True, null=True)
    alarm_state = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'telemetry'


class TelemetryStatics(models.Model):
    site_name = models.CharField(primary_key=True, max_length=255)
    device_name = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    statype = models.CharField(db_column='STATYPE', max_length=50)  # Field name made lowercase.
    pump1_cool_current = models.FloatField(blank=True, null=True)
    pump1_work_current = models.FloatField(blank=True, null=True)
    pump2_cool_current = models.FloatField(blank=True, null=True)
    pump2_work_current = models.FloatField(blank=True, null=True)
    input_optical_power = models.FloatField(blank=True, null=True)
    output_optical_power = models.FloatField(blank=True, null=True)
    transmission_peak_voltage = models.FloatField(blank=True, null=True)
    light_output_wavelength = models.FloatField(blank=True, null=True)
    real_time_link_delay = models.FloatField(db_column='real-time_link_delay', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    receiving_error_signal_sampling1 = models.FloatField(blank=True, null=True)
    receiving_error_signal_sampling2 = models.FloatField(blank=True, null=True)
    receiving_error_signal_sampling3 = models.FloatField(blank=True, null=True)
    receiving_error_signal_sampling4 = models.FloatField(blank=True, null=True)
    receiving_error_signal_sampling5 = models.FloatField(blank=True, null=True)
    receiving_error_signal_sampling6 = models.FloatField(blank=True, null=True)
    receiving_error_signal_sampling7 = models.FloatField(blank=True, null=True)
    receiving_error_signal_sampling8 = models.FloatField(blank=True, null=True)
    receiving_error_signal_sampling9 = models.FloatField(blank=True, null=True)
    receiving_error_signal_sampling10 = models.FloatField(blank=True, null=True)
    input_power = models.FloatField(blank=True, null=True)
    output_power = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'telemetry_statics'
        unique_together = (('site_name', 'device_name', 'timestamp', 'statype'),)


class Telesignalling(models.Model):
    site_name = models.CharField(max_length=25, blank=True, null=True)
    device_name = models.CharField(max_length=255, blank=True, null=True)
    data_name = models.CharField(max_length=255, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    blocked = models.TextField(blank=True, null=True)  # This field type is a guess.
    normal_value = models.IntegerField(blank=True, null=True)
    warning_value = models.IntegerField(blank=True, null=True)
    alarm_value = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'telesignalling'


class TelesignallingStatics(models.Model):
    site_name = models.CharField(primary_key=True, max_length=255)
    device_name = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    statype = models.CharField(db_column='STATYPE', max_length=50)  # Field name made lowercase.
    pump1_tec_current_alarm = models.IntegerField(db_column='pump1_TEC_current_alarm', blank=True, null=True)  # Field name made lowercase.
    pump1_work_current_alarm = models.IntegerField(blank=True, null=True)
    pump2_tec_current_alarm = models.IntegerField(db_column='pump2_TEC_current_alarm', blank=True, null=True)  # Field name made lowercase.
    pump2_work_current_alarm = models.IntegerField(blank=True, null=True)
    input_optical_power_alarm = models.IntegerField(blank=True, null=True)
    output_optical_power_alarm = models.IntegerField(blank=True, null=True)
    running_status = models.IntegerField(blank=True, null=True)
    blocked_status = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'telesignalling_statics'
        unique_together = (('site_name', 'device_name', 'timestamp', 'statype'),)
