#-*-coding: GBK -*-
from django.contrib import admin
from django.utils.html import format_html
from worktile.models import *

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ['id', 'username', 'telephone', 'email', 'avatar', 'state', 'constellation', 'age', 'profession', 'introduction', 'birthday', 'gender']
    list_filter = (
        ('state', admin.ChoicesFieldListFilter),
    )
    search_fields = ['username']

@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ['id', 'username', 'avatar', "whoseFriend"]
    def whoseFriend(self, obj):
        return User.objects.filter(id=obj.user).first().username
    whoseFriend.short_description = "哪个用户的好友"

@admin.register(ProjectMessage)
class ProjectMessageAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ['id', 'projectId', 'userId', 'ifread']

@admin.register(TaskMessage)
class TaskMessageAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ['id', 'taskId', 'userId', 'ifread']

@admin.register(Agenda)
class AgendaAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ['id','description', "user_name",'starttime', 'endtime', 'state']
    list_filter = (
        ('state', admin.ChoicesFieldListFilter),
    )
    search_fields = ['description']
    def user_name(self, obj):
        return obj.user.username
    user_name.short_description = "对应用户"

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ['id', 'name', 'creator_name','state', 'description', 'members', 'rate', 'ifread', 'alltask', 'notstart', 'isgoing', 'ended']

    def members(self, obj):
        return [a.username for a in obj.user.all()]
    members.short_description = "项目成员"

    def creator_name(self, obj):
        return obj.creator.username
    creator_name.short_description="创建人"

    list_filter = (
        ('state', admin.ChoicesFieldListFilter),
        ('ifread'),
    )
    search_fields = ['name']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ['id', 'name', 'state', 'description','members', 'project_name', 'manager_name','ifread','starttime', 'endtime']
    list_filter = (
        ('state', admin.ChoicesFieldListFilter),
        ('ifread'),
    )
    search_fields = ['name']
    def members(self, obj):
        return [a.username for a in obj.user.all()]
    members.short_description = "任务成员"

    def project_name(self, obj):
        return obj.project.name
    project_name.short_description="所属项目"

    def manager_name(self, obj):
        return obj.manager.username
    manager_name.short_description="负责人"

@admin.register(sonTask)
class sonTaskAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ['id', 'name', 'state', 'description', 'members','project_name', 'task_name', 'manager_name','ifread', 'starttime', 'endtime']
    list_filter = (
        ('state', admin.ChoicesFieldListFilter),
        ('ifread'),
    )
    search_fields = ['name']
    def members(self, obj):
        return [a.username for a in obj.user.all()]
    members.short_description = "任务成员"

    def project_name(self, obj):
        return obj.project.name
    project_name.short_description="所属项目"

    def manager_name(self, obj):
        return obj.manager.username
    manager_name.short_description="负责人"

    def task_name(self,obj):
        return obj.task.name
    task_name.short_description="父任务名"

# Register your models here.
# @admin.register(Good)
# class GoodAdmin(admin.ModelAdmin):
#
#     list_per_page = 5
#     list_display = ['name', 'state', 'stock', 'price', 'hit']
#     list_filter = (
#         ('state', admin.ChoicesFieldListFilter),
#         ('category'),
#     )
#
#     def off_all(self, request, queryset):
#         row_updated = queryset.update(state=1)
#         self.message_user(request, "修改了{}条字段".format(row_updated))
#
#     def on_all(self, request, queryset):
#         row_updated = queryset.update(state=0)
#         self.message_user(request, "修改了{}条字段".format(row_updated))
#     on_all.short_description = "批量上架"
#     off_all.short_description = "批量下架"
#     actions = ['on_all', 'off_all']
#     search_fields = ['name']