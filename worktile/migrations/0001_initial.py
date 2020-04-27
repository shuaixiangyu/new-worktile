# Generated by Django 3.0.5 on 2020-04-22 20:44

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='项目名称')),
                ('state', models.IntegerField(choices=[(0, '进行中'), (1, '已完成')], default=0, verbose_name='完成状态')),
                ('description', models.CharField(max_length=300, verbose_name='项目描述')),
                ('rate', models.IntegerField(default=0, verbose_name='项目进度')),
                ('ifread', models.IntegerField(default=0, verbose_name='是否读过')),
                ('alltask', models.IntegerField(default=0, verbose_name='任务总数')),
                ('notstart', models.IntegerField(default=0, verbose_name='未开始的任务数量')),
                ('isgoing', models.IntegerField(default=0, verbose_name='正在进行中的任务数量')),
                ('ended', models.IntegerField(default=0, verbose_name='已完成的任务数量')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50, verbose_name='用户名')),
                ('password', models.CharField(max_length=150, verbose_name='密码')),
                ('avatar', models.ImageField(default='media/user/1.jpg', upload_to='media/user', verbose_name='头像')),
                ('telephone', models.CharField(max_length=11, verbose_name='手机号')),
                ('email', models.EmailField(max_length=254, verbose_name='邮箱')),
                ('state', models.IntegerField(choices=[(0, '未登录'), (1, '已登录')], default=0, verbose_name='登录状态')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='任务名称')),
                ('state', models.IntegerField(choices=[(0, '未开始'), (1, '进行中'), (2, '已完成')], default=0, verbose_name='完成状态')),
                ('ifread', models.IntegerField(default=0, verbose_name='是否读过')),
                ('description', models.CharField(max_length=300, verbose_name='任务描述')),
                ('starttime', models.DateTimeField(default=django.utils.timezone.now, verbose_name='起始时间')),
                ('endtime', models.DateTimeField(verbose_name='截止时间')),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_manager', to='worktile.User', verbose_name='负责人')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_task', to='worktile.Project', verbose_name='所属项目')),
                ('user', models.ManyToManyField(to='worktile.User', verbose_name='对应用户')),
            ],
        ),
        migrations.CreateModel(
            name='sonTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='任务名称')),
                ('state', models.IntegerField(choices=[(0, '未开始'), (1, '进行中'), (2, '已完成')], default=0, verbose_name='完成状态')),
                ('ifread', models.IntegerField(default=0, verbose_name='是否读过')),
                ('description', models.CharField(max_length=300, verbose_name='任务描述')),
                ('starttime', models.DateTimeField(default=django.utils.timezone.now, verbose_name='起始时间')),
                ('endtime', models.DateTimeField(verbose_name='截止时间')),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sontask_manager', to='worktile.User', verbose_name='负责人')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sontask_project', to='worktile.Project', verbose_name='所属项目')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_sontask', to='worktile.Task', verbose_name='父任务')),
                ('user', models.ManyToManyField(to='worktile.User', verbose_name='对应用户')),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='user',
            field=models.ManyToManyField(to='worktile.User', verbose_name='对应用户'),
        ),
        migrations.CreateModel(
            name='Friend',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.IntegerField(verbose_name='用户id')),
                ('avatar', models.ImageField(upload_to='media/user', verbose_name='好友头像')),
                ('username', models.CharField(max_length=50, verbose_name='好友名')),
                ('friend', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friend_id', to='worktile.User', verbose_name='好友在User中的id')),
            ],
        ),
        migrations.CreateModel(
            name='Agenda',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=300, verbose_name='日程描述')),
                ('starttime', models.DateTimeField(default=django.utils.timezone.now, verbose_name='起始时间')),
                ('endtime', models.DateTimeField(verbose_name='截止时间')),
                ('state', models.IntegerField(choices=[(0, '进行中'), (1, '已完成')], default=0, verbose_name='完成状态')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_agenda', to='worktile.User')),
            ],
        ),
    ]
