# Generated by Django 4.0.4 on 2022-06-29 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carcontrollerserver', '0007_rename_image_appuser_picture'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ads',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=255)),
                ('picture', models.ImageField(upload_to='ads/%Y/%m/%d/')),
            ],
        ),
    ]