# Generated by Django 4.0.4 on 2022-06-20 04:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carcontrollerserver', '0006_alter_appuser_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appuser',
            old_name='image',
            new_name='picture',
        ),
    ]