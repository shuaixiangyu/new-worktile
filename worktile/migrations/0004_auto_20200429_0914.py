# Generated by Django 3.0.5 on 2020-04-29 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('worktile', '0003_auto_20200429_0750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='ifread',
            field=models.IntegerField(choices=[(0, '未读'), (1, '已读')], default=0, verbose_name='是否读过'),
        ),
        migrations.AlterField(
            model_name='sontask',
            name='ifread',
            field=models.IntegerField(choices=[(0, '未读'), (1, '已读')], default=0, verbose_name='是否读过'),
        ),
        migrations.AlterField(
            model_name='task',
            name='ifread',
            field=models.IntegerField(choices=[(0, '未读'), (1, '已读')], default=0, verbose_name='是否读过'),
        ),
    ]
