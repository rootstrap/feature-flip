# Generated by Django 3.0.2 on 2020-07-31 00:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_feature_flip', '0002_feature_totally_enabled'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, unique=True)),
                ('features', models.ManyToManyField(to='django_feature_flip.Feature')),
            ],
        ),
    ]
