# Generated manually to add profile_address field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('superadmin', '0012_alter_payment_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='superadminsettings',
            name='profile_address',
            field=models.TextField(blank=True),
        ),
    ]
