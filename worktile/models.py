from django.db import models
from django.utils.timezone import now

from django.utils import timezone

class ProjectMessage(models.Model):
    projectId = models.IntegerField(u'项目id')
    userId = models.IntegerField(u'用户ID')
    choice = (
        (0, "未读"),
        (1, "已读"),
    )
    ifread = models.IntegerField(u'是否读过', choices=choice, default=0)

class TaskMessage(models.Model):
    taskId = models.IntegerField(u'任务id')
    userId = models.IntegerField(u'用户ID')
    choice = (
        (0, "未读"),
        (1, "已读"),
    )
    ifread = models.IntegerField(u'是否读过', choices=choice, default=0)

class User(models.Model):
    time = models.DateTimeField(u'创建时间', default=now)
    username = models.CharField(u'用户名',max_length=50)
    password = models.CharField(u'密码', max_length=150, null=False)
    avatar = models.ImageField(u'头像',upload_to='user',default='user/1.jpg')
    telephone = models.CharField(u'手机号', max_length=11, )
    email = models.EmailField(u'邮箱')
    birthday = models.CharField(u'生日', max_length=20, null=True)
    age = models.IntegerField(u'年龄', null=True)
    profession = models.CharField(u'职业', max_length=50, null=True)
    constellation = models.CharField(u'星座', max_length=20, null=True)
    introduction = models.CharField(u'个人介绍', max_length=500, null=True)
    gender = models.CharField(u'性别', max_length=5, null=True)
    choice = (
        (0, "未登录"),
        (1, "已登录"),
    )
    state = models.IntegerField(u'登录状态',choices=choice,default=0)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = '用户信息'

class Friend(models.Model):
    friend = models.ForeignKey(User, verbose_name='好友在User中的id', related_name='friend_id',on_delete=models.CASCADE)
    user = models.IntegerField(u'用户id', null=False)
    avatar = models.ImageField(u'好友头像', upload_to='user')
    username = models.CharField(u'好友名', max_length=50)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = '通讯录'
        verbose_name_plural = '通讯录'

class Agenda(models.Model):
    time = models.DateTimeField(u'创建时间', default=now)
    user = models.ForeignKey(User, related_name = 'user_agenda', on_delete=models.CASCADE)
    description = models.CharField(u'日程描述', max_length=300)
    starttime = models.DateTimeField(u'起始时间', default = now)
    endtime = models.DateTimeField(u'截止时间', default=now)
    choice = (
        (0, "进行中"),
        (1, "已完成"),
    )
    state = models.IntegerField(u'完成状态', choices=choice, default=0)

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = '日程'
        verbose_name_plural = '日程'

class Project(models.Model):
    time = models.DateTimeField(u'创建时间', default=now)
    user = models.ManyToManyField(User, verbose_name='项目成员' )
    creator = models.ForeignKey(User, verbose_name="项目创建者", related_name="project_creator",on_delete=models.CASCADE, null=True)
    name = models.CharField(u'项目名称', max_length=50)
    choice1 = (
        (0, "进行中"),
        (1, "已完成"),
    )
    state = models.IntegerField(u'完成状态', choices=choice1, default=0)
    description = models.CharField(u'项目描述', max_length=300)
    rate = models.IntegerField(u'项目进度', default=0)
    choice2 = (
        (0, "未读"),
        (1, "已读"),
    )
    ifread = models.IntegerField(u'是否读过', choices=choice2,default=0)
    alltask = models.IntegerField(u'任务总数', default=0)
    notstart = models.IntegerField(u'未开始的任务数量', default=0)
    isgoing = models.IntegerField(u'正在进行中的任务数量', default=0)
    ended = models.IntegerField(u'已完成的任务数量', default=0)


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '项目信息'
        verbose_name_plural = '项目信息'

class Task(models.Model):
    time = models.DateTimeField(u'创建时间', default=now)
    user = models.ManyToManyField(User, verbose_name='任务成员')
    name = models.CharField(u'任务名称', max_length=50)
    choice1 = (
        (0, "未开始"),
        (1, "进行中"),
        (2, "已完成"),
    )
    state = models.IntegerField(u'完成状态', choices=choice1, default=0)
    choice2 = (
        (0, "未读"),
        (1, "已读"),
    )
    ifread = models.IntegerField(u'是否读过', choices=choice2,default=0)
    description = models.CharField(u'任务描述', max_length=300)
    project = models.ForeignKey(Project, verbose_name='所属项目', related_name='project_task',on_delete=models.CASCADE)
    starttime = models.DateTimeField(u'起始时间', default = now)
    endtime = models.DateTimeField(u'截止时间', default=now)
    manager = models.ForeignKey(User, verbose_name='负责人', related_name='task_manager',on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '任务信息'
        verbose_name_plural = '任务信息'

class sonTask(models.Model):
    ifsubtask = models.IntegerField(u'是否是子任务', default=1)
    time = models.DateTimeField(u'创建时间', default=now)
    user = models.ManyToManyField(User, verbose_name='子任务成员')
    name = models.CharField(u'任务名称', max_length=50)
    choice1 = (
        (0, "未开始"),
        (1, "进行中"),
        (2, "已完成"),
    )
    choice2 = (
        (0, "未读"),
        (1, "已读"),
    )
    ifread = models.IntegerField(u'是否读过', choices=choice2, default=0)
    state = models.IntegerField(u'完成状态', choices=choice1, default=0)
    description = models.CharField(u'任务描述', max_length=300)
    task = models.ForeignKey(Task, verbose_name='父任务', related_name='task_sontask',on_delete=models.CASCADE)
    starttime = models.DateTimeField(u'起始时间', default = now)
    endtime = models.DateTimeField(u'截止时间', default=now)
    manager = models.ForeignKey(User, verbose_name='负责人', related_name='sontask_manager',on_delete=models.CASCADE)
    project = models.ForeignKey(Project, verbose_name='所属项目', related_name='sontask_project',on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '子任务信息'
        verbose_name_plural = '子任务信息'
# Create your models here.
