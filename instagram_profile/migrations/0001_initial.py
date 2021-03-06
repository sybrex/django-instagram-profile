# Generated by Django 3.1.3 on 2021-01-04 13:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=256)),
                ('access_token', models.CharField(blank=True, help_text='The long lived access token', max_length=256)),
                ('expires_at', models.DateTimeField(blank=True, help_text='The expiry of the stored long lived access token', null=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'instagram_profile',
                'ordering': ['username'],
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media_id', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('IMAGE', 'Image'), ('CAROUSEL_ALBUM', 'Album'), ('VIDEO', 'Video')], default='IMAGE', max_length=20)),
                ('permalink', models.CharField(max_length=256)),
                ('caption', models.TextField(default='')),
                ('thumbnail', models.ImageField(default='', max_length=256, upload_to='instagram/')),
                ('children', models.TextField(default='')),
                ('created', models.DateTimeField()),
                ('profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='instagram_profile.profile')),
            ],
            options={
                'db_table': 'instagram_posts',
                'ordering': ['-created'],
            },
        ),
    ]
