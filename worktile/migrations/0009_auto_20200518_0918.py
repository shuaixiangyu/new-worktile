# Generated by Django 3.0.5 on 2020-05-18 09:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('worktile', '0008_auto_20200430_0905'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friend',
            name='avatar',
            field=models.ImageField(upload_to='user', verbose_name='好友头像'),
        ),
        migrations.AlterField(
            model_name='project',
            name='user',
            field=models.ManyToManyField(to='worktile.User', verbose_name='项目成员'),
        ),
        migrations.AlterField(
            model_name='sontask',
            name='user',
            field=models.ManyToManyField(to='worktile.User', verbose_name='子任务成员'),
        ),
        migrations.AlterField(
            model_name='task',
            name='manager',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_manager', to='worktile.User', verbose_name='负责人'),
        ),
        migrations.AlterField(
            model_name='task',
            name='user',
            field=models.ManyToManyField(to='worktile.User', verbose_name='任务成员'),
        ),
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(default='user/1.jpg', upload_to='user', verbose_name='头像'),
        ),
    ]
