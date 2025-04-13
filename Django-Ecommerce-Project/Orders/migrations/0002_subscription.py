# Generated by Django 4.1.7 on 2023-05-25 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('subscription_id', models.CharField(max_length=200)),
                ('subscription_name', models.CharField(max_length=150)),
                ('date_time', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
