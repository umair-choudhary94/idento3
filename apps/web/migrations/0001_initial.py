# Generated by Django 3.2.18 on 2023-05-09 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscriber', models.EmailField(max_length=64, verbose_name='Email')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Updated')),
            ],
            options={
                'verbose_name': 'Newsletter',
                'verbose_name_plural': 'Newsletters',
            },
        ),
        migrations.CreateModel(
            name='SiteSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_singleton', models.BooleanField(default=True, editable=False, unique=True)),
                ('website_title', models.CharField(max_length=32, verbose_name='Website Title')),
                ('meta', models.CharField(max_length=32, verbose_name='Meta')),
                ('keyword', models.CharField(max_length=32, verbose_name='Keyword')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='logos', verbose_name='Logo')),
                ('icon', models.ImageField(blank=True, null=True, upload_to='logos', verbose_name='Icon')),
            ],
            options={
                'verbose_name': 'Site Settings',
                'verbose_name_plural': 'Site Settings',
            },
        ),
    ]
