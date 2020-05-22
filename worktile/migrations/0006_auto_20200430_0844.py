# Generated by Django 3.0.5 on 2020-04-30 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('worktile', '0005_auto_20200430_0844'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(max_length=50, null=True, verbose_name='项目名称'),
        ),
        migrations.AlterField(
            model_name='project',
            name='user',
            field=models.ManyToManyField(to='worktile.User', verbose_name='对应用户'),
        ),
    ]