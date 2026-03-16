# Generated manually to add professional information fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('superadmin', '0013_add_profile_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='superadminsettings',
            name='department',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='superadminsettings',
            name='role',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='superadminsettings',
            name='employee_id',
            field=models.CharField(max_length=20, blank=True),
        ),
        migrations.AddField(
            model_name='superadminsettings',
            name='join_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='superadminsettings',
            name='skills',
            field=models.TextField(blank=True),
        ),
    ]
