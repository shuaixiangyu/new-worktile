import datetime
from django.shortcuts import render,redirect
from Newworktile import settings
from worktile.models import *
import re
from django.core import serializers
from django.http import JsonResponse,HttpResponse
import json
from django.core.mail import send_mail
import random
import datetime
from django.core import serializers
from django.forms import model_to_dict
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from Newworktile import settings
from worktile.models import *


# 看一个项目有哪些成员的时候：
# user = User.objects.filter(project=project_id)

def testList(request):
    l = request.POST.get('list')
    data = {}
    data['content'] = l
    relist=[]
    list = str(l)
    list = list[1:-1]
    list = list.split(',')
    for i in list:
        relist.append(int(i))
    data['finally'] = relist
    json = {"data": data}
    return JsonResponse(json, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


# 测试
def test(request):
    user_id = 1
    request.session['user_id'] = user_id
    return HttpResponse('你得到了user_id的session！')


# 工作模块主页
def work(request):
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        if user_id is None:
            return redirect('worktile:login')
        user_id = int(user_id)

        user = User.objects.filter(id=user_id).first()
        project_list = user.project_set.all()
        project = []
        for a in project_list:
            project.append(model_to_dict(a, fields=['name', 'id']))
        project.reverse()
        project = {"project": project}
        return JsonResponse(project,safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    return JsonResponse({})


# 通讯录页面
def friends(request):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user_id = int(user_id)
    friends = Friend.objects.filter(user=user_id)
    friends_list=[]
    for a in friends:
        username = User.objects.get(id=a.friend_id).username
        avatar =  str(User.objects.get(id=a.friend_id).avatar)
        friend = a.friend_id
        a = {"username": username, "avatar":avatar, "friend":friend}
        friends_list.append(a)
    friends_list = {"friends_list": friends_list}
    return JsonResponse(friends_list, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


#项目下的所有任务列表
def ProjectTasks(request, project_id):
    project = Project.objects.filter(id=project_id).first()
    temp = project.project_task.all()
    tasks=[]
    for a in temp:
        tasks.append(model_to_dict(a, fields=['name', 'id', 'state']))
    json = {"tasks": tasks}
    return JsonResponse(json, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')

#任务下的所有子任务列表
def TaskSubtasks(request, project_id, task_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user_id = int(user_id)
    task = Task.objects.filter(id=task_id).first()
    temp = task.task_sontask.all()
    subtasks=[]
    for a in temp:
        subtasks.append(model_to_dict(a, fields=['name', 'id', 'state']))
    data = {"subtasks": subtasks}
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')



# 创建项目页面：
def createProject(request):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user_id = int(user_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        # if not members.count(user_id):
        #     members.append(user_id)
        project = Project.objects.create(name=name, description=description, creator_id=user_id)
        project.user.add(User.objects.filter(id=user_id).first())
        project.save()
        project_id = Project.objects.last().id
        message = ProjectMessage.objects.create(userId=user_id, projectId=project_id, ifread=0)
        message.save()
    return JsonResponse({})


# 创建任务页面,传项目id用url，worktile对url进行了编码加密
def createTask(request, project_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        data = {"warning": "没拿到用户的session"}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    user_id = int(user_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        if name is None:
            return redirect('worktile:error')
        description = request.POST.get('description')
        starttime = request.POST.get('starttime')
        endtime = request.POST.get('endtime')
        task = Task.objects.create(name=name, description=description, starttime=starttime, endtime=endtime, project_id=project_id,manager_id=user_id)
        task.user.add(User.objects.filter(id=user_id).first())
        task.save()
        task_id = Task.objects.last().id
        message = TaskMessage.objects.create(userId=user_id, taskId=task_id, ifread=0)
        message.save()
        project = Project.objects.filter(id=project_id).first()
        project.notstart += 1
        project.alltask += 1
        project.rate = 100 * (project.ended) / project.alltask
        project.save()
        data = {"warning": "POST成功"}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    data = {
        "project_id": project_id,
    }
    dict = {"data": data ,"warning": "POST没成功，为什么呢？"}
    return JsonResponse(dict, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


# 创建子任务页面
def createSubtask(request, project_id, task_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        data = {"warning": "没拿到用户session"}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    user_id = int(user_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        if name is None:
            return redirect('worktile:error')
        description = request.POST.get('description')
        starttime = request.POST.get('starttime')
        endtime = request.POST.get('endtime')
        subtask = sonTask.objects.create(name=name, description=description, starttime=starttime, endtime=endtime,
                                         task_id=task_id, project_id=project_id, manager_id=user_id)
        subtask.user.add(User.objects.filter(id=user_id).first())
        subtask.save()
        data = {"warning": "POST成功"}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    elif request.method == 'GET':
        data = {
            "project_id": project_id,
            "task_id": task_id,
        }
        json = {"data":data}
        return JsonResponse(json, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


# 修改任务负责人
def changeTaskManager(request, project_id, task_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    if request.method == 'GET':
        # friends = Friend.objects.filter(user=user_id).all()
        # friends_list = []
        # for a in friends:
        #     friend = a.friend_id
        #     username = User.objects.get(id=friend).username
        #     avatar = str(User.objects.get(id=friend).avatar)
        #     a = {"username":username, "avatar":avatar, "friend":friend}
        #     friends_list.append(a)
        task = Task.objects.get(id=task_id)
        user = task.user.all()
        friends_list=[]
        for i in user:
            ID = i.id
            username = i.username
            avatar = str(i.avatar)
            a = {"username":username, "avatar":avatar, "friend":ID}
            friends_list.append(a)
        data = {"friends_list": friends_list}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    elif request.method == 'POST':
        manager_id = request.POST.get('manager_id')
        task = Task.objects.filter(id=task_id).first()
        task.manager_id = manager_id
        task.save()
        data = {"warning": 1}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    else:
        data = {"warning": 0}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')

# 修改子任务负责人
def changeSubtaskManager(request, task_id, subtask_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user_id = int(user_id)
    if request.method == 'GET':

        # friends = Friend.objects.filter(user=user_id).all()
        # friends_list = []
        # for a in friends:
        #     friend = a.friend_id
        #     username = User.objects.get(id=friend).username
        #     avatar = str(User.objects.get(id=friend).avatar)
        #     a = {"username": username, "avatar": avatar, "friend": friend}
        #     friends_list.append(a)
        friends_list=[]
        subtask = sonTask.objects.get(id=subtask_id)
        user = subtask.user.all()
        for i in user:
            ID = i.id
            username = i.username
            avatar = str(i.avatar)
            a = {"username":username, "avatar":avatar, "friend":ID}
            friends_list.append(a)
        data = {"friends_list": friends_list}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    elif request.method == 'POST':
        manager_id = request.POST.get('manager_id')
        subtask = sonTask.objects.filter(id=subtask_id).first()
        subtask.manager_id = manager_id
        subtask.save()
        data = {"warning": 1}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    else:
        data = {"warning": 0}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')

# 修改任务成员
def changeTaskMembers(request, project_id, task_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user_id = int(user_id)

    if request.method == 'GET':
        friends = Friend.objects.filter(user=user_id).all()
        friends_list = []
        members = Task.objects.get(id=task_id).user.all()
        member_list = []
        for member in members:
            member_list.append(member.id)
        for a in friends:
            if a.id == user_id and a.friend_id == user_id:
                continue
            friend_id = a.friend_id
            avatar = str(User.objects.get(id=friend_id).avatar)
            username = User.objects.get(id=friend_id).username
            b = {"friend_id": friend_id, "avatar": avatar, "username":username}
            if a.friend_id in member_list:
                b['ifin'] = 1
            else:
                b['ifin'] = 0
            friends_list.append(b)
        data = {"friends_list": friends_list}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    elif request.method == 'POST':
        members = request.POST.get('members')
        if str(members) == '[]':
            task = Task.objects.filter(id=task_id).first()
            taskuser=task.user.all()
            for user in taskuser:
                id = user.id
                messagelist=TaskMessage.objects.filter(userId=id, taskId=task_id).all()
                for message in messagelist:
                    message.delete()
            task.user.clear()
            task.user.add(User.objects.filter(id=user_id).first())
            task.save()
            data = {"warning": 1}
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        else:
            members = str(members)
            members = members[1:-1]
            members = members.split(',')
            members = list(map(int, members))
            members.append(user_id)
            task = Task.objects.filter(id=task_id).first()
            taskuser = task.user.all()
            for user in taskuser:
                id = user.id
                messagelist = TaskMessage.objects.filter(userId=id, taskId=task_id).all()
                for message in messagelist:
                    message.delete()
            task.user.clear()
            for member in members:
                message = TaskMessage.objects.create(taskId=task_id, userId=member, ifread=0)
                message.save()
                task.user.add(User.objects.filter(id=member).first())
            task.save()
            data = {"warning": 1}
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    else:
        data = {"warning": 0}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


# 修改子任务成员
def changeSubtaskMembers(request, task_id, subtask_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user_id = int(user_id)

    if request.method == 'GET':
        subtask = sonTask.objects.filter(id=subtask_id).first()
        members = subtask.user.all()
        member_list = []
        for member in members:
            member_list.append(member.id)
        friends = Friend.objects.filter(user=user_id).all()
        friends_list = []
        for a in friends:
            if a.id == user_id and a.friend_id == user_id:
                continue
            friend_id = a.friend_id
            avatar = str(User.objects.get(id=friend_id).avatar)
            username = User.objects.get(id=friend_id).username
            b = {"friend_id": friend_id, "avatar": avatar, "username": username}
            if a.friend_id in member_list:
                b['ifin'] = 1
            else:
                b['ifin'] = 0
            friends_list.append(b)
        data = {"friends_list": friends_list}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    elif request.method == 'POST':
        members = request.POST.get('members')
        if str(members) == '[]':
            subtask = sonTask.objects.filter(id=subtask_id).first()
            subtask.user.clear()
            subtask.user.add(User.objects.filter(id=user_id).first())
            subtask.save()
            data = {"warning": 1}
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        else:
            members = str(members)
            members = members[1:-1]
            members = members.split(',')
            members = list(map(int, members))
            members.append(user_id)
            subtask = sonTask.objects.filter(id=subtask_id).first()
            subtask.user.clear()
            for member in members:
                subtask.user.add(User.objects.filter(id=member).first())
            subtask.save()
            data = {"warning": 1}
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    else:
        data = {"warning": 0}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')




# 修改项目成员
def changeProjectMembers(request, project_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user_id = int(user_id)

    if request.method == 'GET':
        friends = Friend.objects.filter(user=user_id).all()
        friends_list = []
        project = Project.objects.filter(id=project_id).first()
        members = project.user.all()
        member_list = []
        for member in members:
            member_list.append(member.id)
        for a in friends:
            if (a.user == user_id and a.friend_id == user_id):
                continue
            friend_id = a.friend_id
            avatar = str(User.objects.get(id=friend_id).avatar)
            username = User.objects.get(id=friend_id).username
            b = {"friend_id": friend_id, "avatar": avatar, "username": username}
            if a.friend_id in member_list:
                b['ifin'] = 1
            else:
                b['ifin'] = 0
            friends_list.append(b)
        data = {"friends_list": friends_list, "user_id":user_id}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    elif request.method == 'POST':
        members = request.POST.get('members')
        if str(members) == '[]':
            project = Project.objects.filter(id=project_id).first()
            userlist=project.user.all()
            for user in userlist:
                id = user.id
                messagelist=ProjectMessage.objects.filter(userId=id,projectId=project_id).all()
                for message in messagelist:
                    message.delete()
            project.user.clear()
            project.user.add(User.objects.filter(id=user_id).first())
            project.save()
            data = {"warning": 1}
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        else:
            members = str(members)
            members = members[1:-1]
            members = members.split(',')
            members = list(map(int, members))
            members.append(user_id)
            project = Project.objects.filter(id=project_id).first()
            userlist = project.user.all()
            for user in userlist:
                id = user.id
                messagelist = ProjectMessage.objects.filter(userId=id, projectId=project_id).all()
                for message in messagelist:
                    message.delete()
            project.user.clear()
            print(request.POST)
            for member in members:
                a = int(member)
                message = ProjectMessage.objects.create(projectId=project_id, userId=a)
                message.save()
                project.user.add(User.objects.filter(id=a).first())
            project.save()
            data = {"warning": 1}
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    else:
        data = {"warning": 0}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


# 修改项目状态
def changeProjectState(request, project_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        data = {"warning": "没拿到用户session"}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    user_id = int(user_id)
    if request.method == 'POST':
        str = request.POST.get('state')
        if int(str) == 0:
            state = 0
        elif int(str) == 1:
            state = 1
        project = Project.objects.filter(id=project_id).first()
        project.state = state
        project.save()
        data = {"warning": "POST成功"}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    return JsonResponse({})


# 修改任务状态
def changeTaskState(request, project_id, task_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        data = {"warning": "没拿到用户session"}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    user_id = int(user_id)
    if request.method == 'POST':
        origin = Task.objects.filter(id=task_id).first().state
        project = Project.objects.filter(id=project_id).first()
        origin = int(origin)
        if origin == 0:
            project.notstart -= 1
        elif origin == 1:
            project.isgoing -= 1
        elif origin == 2:
            project.ended -= 1
        str = request.POST.get('state')
        if int(str) == 0:
            state = 0
            project.notstart += 1
            project.rate = 100 * (project.ended) / project.alltask
        elif int(str) == 1:
            state = 1
            project.isgoing += 1
            project.rate = 100 * (project.ended) / project.alltask
        elif int(str) == 2:
            state = 2
            project.ended += 1
            project.rate = 100 * (project.ended) / project.alltask
        project.save()
        task = Task.objects.filter(id=task_id).first()
        task.state = state
        task.save()
        data = {"warning": "POST成功"}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    return JsonResponse({})


# 修改子任务状态
def changeSubtaskState(request, task_id, subtask_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        data = {"warning": "没拿到用户session"}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    user_id = int(user_id)
    if request.method == 'POST':
        str = request.POST.get('state')
        if int(str) == 0:
            state = 0
        elif int(str) == 1:
            state = 1
        elif int(str) == 2:
            state = 2
        subtask = sonTask.objects.filter(id=subtask_id).first()
        subtask.state = state
        subtask.save()
        data = {"warning": "POST成功"}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    return JsonResponse({})


# 修改项目描述
def changeProjectDescription(request, project_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        data = {"warning": "没拿到用户session"}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    user_id = int(user_id)
    if request.method == 'POST':
        description = request.POST.get('description')
        project = Project.objects.filter(id=project_id).first()
        project.description = description
        project.save()
        data = {"warning": "POST成功"}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    return JsonResponse({})


# 修改任务描述
def changeTaskDescription(request, project_id, task_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        data = {"warning": "没拿到用户session"}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    user_id = int(user_id)
    if request.method == 'POST':
        description = request.POST.get('description')
        task = Task.objects.filter(id=task_id).first()
        task.description = description
        task.save()
        data = {"warning": "POST成功"}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    return JsonResponse({})


# 修改子任务描述
def changeSubtaskDescription(request, task_id, subtask_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        data = {"warning": "没拿到用户session"}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    user_id = int(user_id)
    if request.method == 'POST':
        description = request.POST.get('description')
        subtask = sonTask.objects.filter(id=subtask_id).first()
        subtask.description = description
        subtask.save()
        data = {"warning": "POST成功"}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    return JsonResponse({})


# 项目详情
def ProjectDetail(request, project_id):
    if Project.objects.all().count() == 0:
        return redirect('worktile:error')
    maxn = Project.objects.last().id
    if project_id > maxn:
        return redirect('worktile:error')
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user_id = int(user_id)

    members = Project.objects.get(id=project_id).user.all()
    id_list = []
    for member in members:
        id_list.append(member.id)
    if user_id not in id_list:
        data = {"message": "抱歉，您没有权限查看该项目", "right": 0}
        json = {"data": data}
        return JsonResponse(json, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')

    project = Project.objects.filter(id=project_id).first()
    if project.ifread == 0:
        project.ifread = 1
        project.save()
    project_message = ProjectMessage.objects.get(projectId=project_id, userId=user_id)
    project_message.ifread = 1
    project_message.save()
    name = project.name
    description = project.description
    state = project.state
    data = {
        "name": name,
        "description": description,
        "state": state,
        "right": 1,
    }
    if user_id == project.creator_id:
        ifcreator = 1
    else:
        ifcreator = 0
    json = {"data": data, "ifcreator": ifcreator}
    return JsonResponse(json, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


# 任务详情
def TaskDetail(request, project_id, task_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user_id = int(user_id)

    manager = Task.objects.get(id=task_id).manager_id
    members1 = Task.objects.get(id=task_id).user.all()
    members2 = Project.objects.get(id=project_id).user.all()
    id_list = []
    print('here')
    for member in members1:
        id_list.append(member.id)
    for member in members2:
        id_list.append(member.id)
    if user_id not in id_list and user_id != manager:
        data = {"message": "抱歉，您没有权限查看该项目", "right": 0}
        json = {"data": data}
        return JsonResponse(json, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


    project = Project.objects.filter(id=project_id).first()
    task = Task.objects.filter(id=task_id).first()
    task_message = TaskMessage.objects.get(taskId=task_id, userId=user_id)
    task_message.ifread=1
    task_message.save()
    if task.ifread == 0:
        task.ifread = 1
        task.save()
    project_name = project.name
    task_name = task.name
    description = task.description
    starttime = task.starttime
    endtime = task.endtime
    state = task.state
    manager_id = task.manager_id
    manager_name = User.objects.filter(id=manager_id).first().username
    manager_pic = str(User.objects.filter(id=manager_id).first().avatar)
    subtask_num = sonTask.objects.filter(task=task_id).count()
    if user_id == manager_id:
        ifmanager = 1
    else:
        ifmanager = 0
    data = {
        "project_name": project_name,
        "task_name": task_name,
        "project_id": project_id,
        "description": description,
        "starttime": starttime,
        "endtime": endtime,
        "state": state,
        "manager_id": manager_id,
        "manager_name": manager_name,
        "subtask_num": subtask_num,
        "right": 1,
        "manager_pic": manager_pic,
        "ifmanager": ifmanager
    }
    json = {"data": data}
    return JsonResponse(json, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')



# 子任务详情
def SubtaskDetail(request, task_id, subtask_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user_id = int(user_id)

    manager1 = sonTask.objects.get(id=subtask_id).manager_id
    manager2 = Task.objects.get(id=task_id).manager_id
    members1 = sonTask.objects.get(id=subtask_id).user.all()
    members2 = Task.objects.get(id=task_id).user.all()
    project_id = sonTask.objects.get(id=subtask_id).project_id
    members3 = Project.objects.get(id=project_id).user.all()
    id_list = []
    for member in members1:
        id_list.append(member.id)
    for member in members2:
        id_list.append(member.id)
    for member in members3:
        id_list.append(member.id)
    id_list.append(manager1)
    id_list.append(manager2)
    if user_id not in id_list :
        data = {"message": "抱歉，您没有权限查看该项目"}
        json = {"data": data}
        return JsonResponse(json, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')

    subtask = sonTask.objects.filter(id=subtask_id).first()
    if subtask.ifread == 0:
        subtask.ifread = 1
        subtask.save()
    task_id = task_id
    task_name = Task.objects.filter(id=task_id).first().name
    name=subtask.name
    description = subtask.description
    starttime = subtask.starttime
    endtime = subtask.endtime
    state = subtask.state
    manager_id = subtask.manager_id
    manager_name = User.objects.filter(id=manager_id).first().username
    manager_pic = str(User.objects.filter(id=manager_id).first().avatar)
    project_id = subtask.project_id
    project_name = Project.objects.filter(id=project_id).first().name
    if user_id == manager_id:
        ifmanager = 1
    else:
        ifmanager = 0
    data = {
        "project_name": project_name,
        "task_name": task_name,
        "project_id": project_id,
        "description": description,
        "starttime": starttime,
        "endtime": endtime,
        "state": state,
        "manager_id": manager_id,
        "manager_name": manager_name,
        "manager_pic":manager_pic,
        "task_id": task_id,
        "name": name,
        "ifmanager": ifmanager
    }
    json = {"data": data}
    return JsonResponse(json, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


# 查看项目成员
def viewProjectMembers(request, project_id):
    if Project.objects.all().count() == 0:
        return redirect('worktile:error')
    maxn = Project.objects.last().id
    if project_id > maxn:
        return redirect('worktile:error')
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:error')
    user_id = int(user_id)
    members = Project.objects.get(id=project_id).user.all()
    id_list = []
    for member in members:
        id_list.append(member.id)
    if user_id not in id_list:
        return redirect('worktile:error')
    project = Project.objects.filter(id=project_id).first()
    if project is None:
        return redirect('404')
    members_list = project.user.all()
    members = []
    for a in members_list:
        a = (model_to_dict(a, fields=['username', 'avatar', 'id']))
        a['avatar'] = str(a['avatar'])
        members.append(a)
    data = {"members": members}
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


# 查看任务成员
def viewTaskMembers(request, project_id, task_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user_id = int(user_id)

    manager = Task.objects.get(id=task_id).manager_id
    members = Task.objects.get(id=task_id).user.all()

    task = Task.objects.filter(id=task_id).first()
    members_list = task.user.all()
    members = []
    for a in members_list:
        a = (model_to_dict(a, fields=['username', 'avatar', 'id']))
        a['avatar'] = str(a['avatar'])
        members.append(a)
    if user_id == manager:
        ifmanager = 1
    else:
        ifmanager = 0
    data = {"members": members, "ifmanager":ifmanager}
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


# 查看子任务成员
def viewSubtaskMembers(request, task_id, subtask_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user_id = int(user_id)

    manager = sonTask.objects.get(id=subtask_id).manager_id
    members = sonTask.objects.get(id=subtask_id).user.all()

    subtask = sonTask.objects.filter(id=subtask_id).first()
    members_list = subtask.user.all()
    members = []
    for a in members_list:
        a = (model_to_dict(a, fields=['username', 'avatar', 'id']))
        a['avatar'] = str(a['avatar'])
        members.append(a)
    if user_id == manager:
        ifmanager = 1
    else:
        ifmanager = 0
    data = {"members": members, "ifmanager": ifmanager}
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


# 统计报表页面
def projectReport(request):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:error')
    user_id = int(user_id)
    user = User.objects.filter(id=user_id).first()
    projects_list = user.project_set.all()
    projects = []
    for a in projects_list:
        projects.append(model_to_dict(a, fields=['name', 'id', 'rate', 'alltask', 'notstart', 'isgoing','ended']))
    data = {"projects": projects}
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')

def useTime(obj):
    return obj.time
# 我的任务页面
def myTasks(request):
    user_id = request.session.get('user_id')
    user_id = int(user_id)
    a = Task.objects.filter(user=user_id).filter(state=0).all()
    b = sonTask.objects.filter(user=user_id).filter(state=0).all()
    notstart = []
    for i in a:
        notstart.append(i)
    for i in b:
        notstart.append(i)
    notstart.sort(key=useTime, reverse=True)

    # # 获取列表的第二个元素
    # def takeSecond(elem):
    #     return elem[1]
    # # 列表
    # random = [(2, 2), (3, 4), (4, 1), (1, 3)]
    # # 指定第二个元素排序
    # random.sort(key=takeSecond)

    a  = Task.objects.filter(user=user_id).filter(state=1).all()
    b = sonTask.objects.filter(user=user_id).filter(state=1).all()
    isgoing = []
    for i in a:
        isgoing.append(i)
    for i in b:
        isgoing.append(i)
    isgoing.sort(key=useTime, reverse=True)
    ended=[]
    a = Task.objects.filter(user=user_id).filter(state=2).all()
    b = sonTask.objects.filter(user=user_id).filter(state=2).all()
    for i in a:
        ended.append(i)
    for i in b:
        ended.append(i)
    ended.sort(key=useTime, reverse=True)
    notstart = serializers.serialize("json", notstart)
    isgoing = serializers.serialize("json", isgoing)
    ended = serializers.serialize("json", ended)
    notstart = json.loads(notstart)

    isgoing = json.loads(isgoing)
    ended = json.loads(ended)
    data = {
        "notstart": notstart,
        "isgoing": isgoing,
        "ended": ended,
    }
    my_json = {"data": data}
    return JsonResponse(my_json, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


# 添加好友
def addFrineds(request):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:error')
    user_id = int(user_id)
    data = {
        "user_id": user_id,
    }
    json = {"data":data}
    return JsonResponse(json, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


# 按照邮箱添加好友
def addFriendsEmail(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email__exact=email).all()
        user_list = []
        for a in user:
            a = model_to_dict(a, fields=['username', 'avatar', 'id', 'email'])
            a['avatar'] = str(a['avatar'])
            user_list.append(a)
        data = {"user_list": user_list}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    return JsonResponse({})


# 按照用户名添加好友
def addFrinedsUsername(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user = User.objects.filter(username__exact=username).all()
        user_list = []
        for a in user:
            a = model_to_dict(a, fields=['username', 'avatar', 'id'])
            a['avatar'] = str(a['avatar'])
            user_list.append(a)
        data = {"user_list": user_list}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    return JsonResponse({})


# 按照手机号添加好友
def addFrinedsTelephone(request):
    if request.method == 'POST':
        telephone = request.POST.get('telephone')
        user = User.objects.filter(telephone__exact=telephone)
        user_list = []
        for a in user:
            a = model_to_dict(a, fields=['username', 'avatar', 'id', 'telephone'])
            a['avatar'] = str(a['avatar'])
            user_list.append(a)
        data = {"user_list": user_list}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    return JsonResponse({})


def error(request):
    return HttpResponse("页面请求错误")



def login_page(request):
    if request.method == "POST":
        telephone = request.POST.get('telephone')
        password = request.POST.get('password')
        if User.objects.filter(telephone=telephone):
            user = User.objects.get(telephone=telephone)
            if user.password == password:
                request.session['user_id'] = user.id
                user.state = 1
                user.save()
                warning = '1'
                data = {'warning':warning}
                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii':False})
            else:
                warning = '密码错误'
                data = {'warning': warning}
                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False},charset='utf-8')
        else:
            warning = '此手机未注册'
            data = {'warning': warning}
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False},charset='utf-8')
    else:
         return HttpResponse()

def register_page(request):
    if request.method == "POST":
        obtain = request.POST
        if 'check' in obtain:
            name = request.POST.get('name')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            telephone = request.POST.get('telephone')
            email = request.POST.get('email')
            check = request.POST.get('check')
            if password1 != password2:
                warning = '两次密码不一致'
                data = {'warning': warning}
                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
            elif telephone != request.session.get('telephone'):
                warning = '已使用本手机注册，请勿中途更改手机号'
                data = {'warning': warning}
                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
            elif len(telephone) > 11:
                warning = '手机号不是只有11位吗？'
                data = {'warning': warning}
                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
            elif email != request.session.get('email'):
                warning = '已使用本邮箱注册，请勿中途更改邮箱'
                data = {'warning': warning}
                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
            elif check != request.session.get('check'):
                warning = '验证码错误'
                data = {'warning': warning}
                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
            else:
                user = User.objects.create(username=name, password=password1, telephone=telephone, email=email)
                user.save()
                friend = Friend.objects.create(user=user.id,avatar=user.avatar,username=user.username,friend=user)
                friend.save()
                warning = '1'
                data = {'warning': warning}
                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        else:
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            telephone = request.POST.get('telephone')
            email = request.POST.get('email')
            if User.objects.filter(telephone=telephone):
                warning = '此手机已注册'
                data = {'warning': warning}
                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
            else:
                if password1 == password2:
                    s = ''.join(random.sample(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
                                           'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'] +
                                          ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
                                           'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'] +
                                          ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], 4))
                    request.session['telephone'] = telephone
                    request.session['email'] = email
                    request.session['check'] = s
                    word1 = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
                    word2 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
                             'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                             'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1',
                             '2', '3', '4', '5', '6', '7', '8', '9']
                    address_list = ['qq.com', '163.com', '126.com', 'Outlook.com', 'stu.ouc.edu.cn']
                    warning = '验证码已发送'
                    identity = email.split('@')[0]
                    address = email.split('@')[1]
                    if address in address_list:
                        if address == 'qq.com':
                            for i in identity:
                                if i not in word1:
                                    warning = '验证码发送失败，请检查邮箱填写是否正确'
                        else:
                            for i in identity:
                                if i not in word2:
                                    warning = '验证码发送失败，请检查邮箱填写是否正确'
                    else:
                        warning = '验证码发送失败，请检查邮箱填写是否正确'
                    try:
                        send_mail(subject='注册验证码',
                                  message='欢迎注册，您本次注册的验证码为' + s,
                                  from_email=settings.EMAIL_HOST_USER,
                                  recipient_list=[email])
                    except:
                        warning = '验证码发送失败，请检查邮箱填写是否正确'
                    data = {'warning': warning}
                    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
                else:
                    warning = '两次密码不一致'
                    data = {'warning': warning}
                    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    else:
        request.session['telephone'] = None
        request.session['email'] = None
        request.session['check'] = None
        return HttpResponse()

def findback_page(request):
    if request.method == "POST":
        obtain = request.POST
        if 'check' in obtain:
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            telephone = request.POST.get('telephone')
            check = request.POST.get('check')
            if password1 != password2:
                warning = '两次密码不一致'
                data = {'warning': warning}
                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
            elif telephone != request.session.get('findbacktelephone'):
                warning = '已使用本手机找回密码，请勿中途更改手机号'
                data = {'warning': warning}
                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
            elif check != request.session.get('findbackcheck'):
                warning = '验证码错误'
                data = {'warning': warning}
                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
            else:
                user = User.objects.get(telephone=telephone)
                user.password = password1
                user.save()
                warning = '1'
                data = {'warning': warning}
                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        else:
            telephone = request.POST.get('telephone')
            if User.objects.filter(telephone=telephone):
                user = User.objects.get(telephone=telephone)
                email = user.email
                s = ''.join(random.sample(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
                                           'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'] +
                                          ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
                                           'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'] +
                                          ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], 4))
                request.session['findbacktelephone'] = telephone
                request.session['findbackcheck'] = s
                try:
                    send_mail(subject='注册验证码',
                              message='欢迎注册，您本次注册的验证码为' + s,
                              from_email=settings.EMAIL_HOST_USER,
                              recipient_list=[email])
                    warning = '验证码已发送'
                except:
                    warning = '验证码发送失败？'
                data = {'warning': warning}
                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
            else:
                warning = '此手机未注册'
                data = {'warning': warning}
                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    else:
        request.session['findbacktelephone'] = None
        request.session['findbackcheck'] = None
        return HttpResponse()

def center_page(request):
    user_id = request.session.get('user_id')
    if user_id is None:
        redirect('worktile:login')
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        data = {}
        data['user'] = {}
        data['user']['user_name'] = user.username
        data['user']['avatar'] = str(user.avatar)
        data['user']['telephone'] = user.telephone
        data['user']['email'] = user.email
        today = str(datetime.datetime.now())
        today_year = int(today[0:4])
        today_month = int(today[5:7])
        today_day = int(today[8:10])
        time1 = datetime.datetime(today_year, today_month, today_day, 0, 0, 0)
        time2 = datetime.datetime(today_year, today_month, today_day, 23, 59, 59)
        schedule_list = user.user_agenda.filter(starttime__gte=time1, endtime__lte=time2)
        schedule = serializers.serialize('json', schedule_list, ensure_ascii=False)
        schedule = json.loads(schedule)
        print(schedule)
        data['schedule'] = schedule
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    else:
        data = {}
        data['user'] = {}
        if user.birthday:
            birthday = user.birthday
            birthday = str(birthday).split('-')
            year = birthday[0]
            month = birthday[1]
            day = birthday[2]
            data['user']['birthday'] = {'year':year, 'month':month, 'day':day}
        else:
            data['user']['birthday'] = {'year':None, 'month':None, 'day':None}
        data['user']['constellation'] = user.constellation
        data['user']['profession'] = user.profession
        data['user']['age'] = user.age
        data['user']['gender'] = user.gender
        data['user']['introduction'] = user.introduction
        data['user']['user_name'] = user.username
        data['user']['avatar'] = str(user.avatar)
        data['user']['telephone'] = user.telephone
        data['user']['email'] = user.email
        today = str(datetime.datetime.now())
        today_year = int(today[0:4])
        today_month = int(today[5:7])
        today_day = int(today[8:10])
        time1 = datetime.datetime(today_year, today_month, today_day, 0, 0, 0)
        time2 = datetime.datetime(today_year, today_month, today_day, 23, 59, 59)
        schedule_list = user.user_agenda.filter(starttime__gte=time1, endtime__lte=time2)
        schedule = serializers.serialize('json', schedule_list, ensure_ascii=False)
        schedule = json.loads(schedule)
        data['schedule'] = schedule
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')

import random

from django.http import JsonResponse
from django.shortcuts import redirect

from Newworktile import settings
from worktile.models import *
from django.utils.timezone import now


def userinfo_page(request):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user = User.objects.get(id=user_id)
    if request.method == "POST":
        obtain = request.POST
        if 'newname' in obtain:
            name = request.POST.get('newname')
            if len(name) > 10:
                warning = '用户名过长'
                data = {'warning': warning}
                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
            elif len(name) == 0:
                warning = '用户名不为空'
                data = {'warning': warning}
                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
            else:
                user.username = name
                user.save()
                friend_list = Friend.objects.filter(user=user.id, friend_id=user_id)
                for i in friend_list:
                    i.username = name
                    i.save()
                warning = '1'
                data = {'warning': warning}
                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        elif 'newavatar' in request.FILES:
            picture = request.FILES.get('newavatar')
            z = ['jpg', 'JPG', 'png', 'PNG', 'bmp', 'BMP']
            if not picture:
                warning = '请选择图片'
                data = {'warning': warning}
                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
            elif picture.name[-3:] in z:
                if picture.size > 2048000:
                    warning = '图片大小不超过2M'
                    data = {'warning': warning}
                    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
                s = ''.join(random.sample(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
                                           'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'] +
                                          ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
                                           'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'] +
                                          ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], 6))
                image = "user/" + user.telephone + s + picture.name[-4:]
                user.avatar = image
                user.save()
                friend_list = Friend.objects.filter(friend_id=user_id)
                for i in friend_list:
                    i.avatar = image
                    i.save()
                fname = settings.MEDIA_ROOT + "/user/" + user.telephone + s + picture.name[-4:]
                with open(fname, 'wb') as pic:
                    for img in picture.chunks():
                        pic.write(img)
                warning = '1'
                data = {'warning': warning}
                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
            else:
                warning = '只允许jpg,png,bmp格式的图片'
                data = {'warning': warning}
                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        elif 'profession' in obtain:
            profession  = request.POST.get('profession')
            user.profession = profession
            user.save()
            data = {'warning': 1}
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        elif 'gender' in obtain:
            gender = request.POST.get('gender')
            user.gender = gender
            user.save()
            data = {'warning': 1}
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        elif 'introduction' in obtain:
            introduction = request.POST.get('introduction')
            user.introduction =introduction
            user.save()
            data = {'warning': 1}
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        elif 'birthday' in obtain:
            birthday = request.POST.get('birthday')  #2001-1-1-白羊座
            tmp = str(birthday).split('-')
            year = int(tmp[0])
            month = int(tmp[1])
            day = int(tmp[2])
            birthday = tmp[0]+'-'+tmp[1]+'-'+tmp[2]
            constellation = tmp[3]
            a = str(timezone.now())
            year1 = int(a[0:4])
            month1 = int(a[5:7])
            day1 = int(a[8:10])
            if month1 > month or (month1 == month and day1 >= day):
                age = year1 - year
            else:
                age = year1 - year + 1
            user.birthday = birthday
            user.constellation = constellation
            user.age = age
            user.save()
            data = {'warning': 1}
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        else:
            user.state = 0
            user.save()
            request.session['user_id'] = None
            return redirect('worktile:login')
    else:
        data = {}
        data['user'] = {}
        if user.birthday:
            birthday = user.birthday
            birthday = str(birthday).split('-')
            year = birthday[0]
            month = birthday[1]
            day = birthday[2]
            data['user']['birthday'] = {'year': year, 'month': month, 'day': day}
        else:
            data['user']['birthday'] = {'year': None, 'month': None, 'day': None}
        a = str(timezone.now())
        year1 = int(a[0:4])
        month1 = int(a[5:7])
        day1 = int(a[8:10])
        data['user']['now'] = {'year':year1, 'month':month1, 'day':day1}
        data['user']['username'] = user.username
        data['user']['avatar'] = str(user.avatar)
        data['user']['constellation'] = user.constellation
        data['user']['profession'] = user.profession
        data['user']['age'] = user.age
        data['user']['gender'] = user.gender
        data['user']['introduction'] = user.introduction
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


def changepassword_page(request):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user = User.objects.get(id=user_id)
    if request.method == "POST":
        password = request.POST.get('password')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password == user.password:
            if password1 == password2:
                user.password = password1
                user.save()
                warning = '1'
                data = {'warning': warning}
                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
            else:
                warning = '两次密码不一致'
                data = {'warning': warning}
                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        else:
            warning = '原密码错误'
            data = {'warning': warning}
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    else:
        return HttpResponse()

def calendar_page(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    if request.method == "POST":
        obtain = request.POST
        if 'time' in obtain:
            today = request.POST.get('time')
            today_year = int(today[0:4])
            today_month = int(today[5:7])
            today_day = int(today[8:10])
            start_year = today_year
            start_month = today_month
            end_year = today_year
            end_month = today_month + 1
            if today_month == 12:
                end_year = today_year + 1
                end_month = 1
            time1 = datetime.datetime(start_year, start_month, 1, 0, 0, 0)
            time2 = datetime.datetime(end_year, end_month, 1, 0, 0, 0)
            daylist = []
            schedule_list = user.user_agenda.filter(starttime__gte=time1, endtime__lte=time2)
            for schedule in schedule_list:
                day = str(schedule.starttime)[0:10]
                if day not in daylist:
                    daylist.append(day)
            daylist.sort()
            data = {}
            data['daylist'] = daylist
            time1 = datetime.datetime(today_year, today_month, today_day, 0, 0, 0)
            time2 = datetime.datetime(today_year, today_month, today_day, 23, 59, 59)
            schedule_list = user.user_agenda.filter(starttime__gte=time1, endtime__lte=time2).order_by('-id')
            schedule = serializers.serialize('json', schedule_list, ensure_ascii=False)
            schedule = json.loads(schedule)
            data['schedule'] = schedule
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        else:
            today = request.POST.get('month')
            today_year = int(today[0:4])
            today_month = int(today[5:7])
            start_year = today_year
            start_month = today_month
            end_year = today_year
            end_month = today_month + 1
            if today_month == 12:
                end_year = today_year + 1
                end_month = 1
            time1 = datetime.datetime(start_year, start_month, 1, 0, 0, 0)
            time2 = datetime.datetime(end_year, end_month, 1, 0, 0, 0)
            daylist = []
            schedule_list = user.user_agenda.filter(starttime__gte=time1, endtime__lte=time2)
            for schedule in schedule_list:
                day = str(schedule.starttime)[0:10]
                if day not in daylist:
                    daylist.append(day)
            daylist.sort()
            data = {}
            data['daylist'] = daylist
            data['schedule'] = []
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    else:
        today = str(datetime.datetime.now())
        today_year = int(today[0:4])
        today_month = int(today[5:7])
        today_day = int(today[8:10])
        start_year = today_year
        start_month = today_month
        end_year = today_year
        end_month = today_month + 1
        if today_month == 12:
            end_year = today_year + 1
            end_month = 1
        time1 = datetime.datetime(start_year, start_month, 1, 0, 0, 0)
        time2 = datetime.datetime(end_year, end_month, 1, 0, 0, 0)
        daylist = []
        schedule_list = user.user_agenda.filter(starttime__gte=time1, endtime__lte=time2)
        for schedule in schedule_list:
            day = str(schedule.starttime)[0:10]
            if day not in daylist:
                daylist.append(day)
        daylist.sort()
        data = {}
        data['daylist'] = daylist
        time1 = datetime.datetime(today_year, today_month, today_day, 0, 0, 0)
        time2 = datetime.datetime(today_year, today_month, today_day, 23, 59, 59)
        schedule_list = user.user_agenda.filter(starttime__gte=time1, endtime__lte=time2).order_by('-id')
        schedule = serializers.serialize('json', schedule_list, ensure_ascii=False)
        schedule = json.loads(schedule)
        data['schedule'] = schedule
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')

def scheduledetail_page(request,schedule_id):
    if request.method == "POST":
        state = request.POST.get('state')
        schedule = Agenda.objects.get(id=schedule_id)
        schedule.state = int(state)
        schedule.save()
        data = {}
        data['schedule'] = {}
        starttime = str(schedule.starttime).replace(' ','T')
        starttime = starttime[0:19] + 'Z'
        endtime = str(schedule.endtime).replace(' ', 'T')
        endtime = endtime[0:19] + 'Z'
        data['schedule']['state'] = schedule.state
        data['schedule']['starttime'] = starttime
        data['schedule']['endtime'] = endtime
        data['schedule']['description'] = schedule.description
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    else:
        schedule = Agenda.objects.get(id=schedule_id)
        data = {}
        data['schedule'] = {}
        starttime = str(schedule.starttime).replace(' ', 'T')
        starttime = starttime[0:19] + 'Z'
        endtime = str(schedule.endtime).replace(' ', 'T')
        endtime = endtime[0:19] + 'Z'
        data['schedule']['state'] = schedule.state
        data['schedule']['starttime'] = starttime
        data['schedule']['endtime'] = endtime
        data['schedule']['description'] = schedule.description
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')

def newschedule_page(request):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    if request.method == "POST":
        description = request.POST.get('description')
        description = description.strip()
        if description == "":
            warning = '日程描述不能为空'
            data = {'warning': warning}
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        description1 = description.replace('\r\n','')
        if len(description) - len(description1) >= 10:
            warning = '回车太多了'
            data = {'warning': warning}
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        starttime = request.POST.get('starttime')
        endtime = request.POST.get('endtime')
        starttime_year = int(starttime[0:4])
        starttime_month = int(starttime[5:7])
        starttime_day = int(starttime[8:10])
        starttime_hour = int(starttime[11:13])
        starttime_minute = int(starttime[14:16])
        endtime_year = int(endtime[0:4])
        endtime_month = int(endtime[5:7])
        endtime_day = int(endtime[8:10])
        endtime_hour = int(endtime[11:13])
        endtime_minute = int(endtime[14:16])
        starttime = datetime.datetime(starttime_year, starttime_month, starttime_day, starttime_hour, starttime_minute, 0)
        endtime = datetime.datetime(endtime_year, endtime_month, endtime_day, endtime_hour, endtime_minute, 0)
        if starttime >= endtime:
            warning = '截止时间应晚于开始时间'
            data = {'warning': warning}
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        time = datetime.datetime(starttime_year, starttime_month, starttime_day, 23, 59, 59)
        if endtime > time:
            warning = '新建日程时间范围为当日'
            data = {'warning': warning}
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        Agenda.objects.create(starttime=starttime,endtime=endtime,description=description,state=0,user_id=user_id)
        warning = '1'
        data = {'warning': warning}
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    else:
        return HttpResponse()

from django.core.paginator import Paginator, EmptyPage

def schedulehelper_page(request):
    user_id = request.session.get('user_id')
    if request.method == "POST":
        obtain = request.POST
        if 'delete' in obtain:
            delete = request.POST.get('delete')
            if request.session.get('schedule_delete') is None:
                request.session['schedule_delete'] = str(delete)
            else:
                request.session['schedule_delete'] = request.session.get('schedule_delete') + ',' + str(delete)
            data = {}
            data['warning'] = '1'
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        user = User.objects.get(id=user_id)
        page = int(request.POST.get('page'))
        data = {}
        today = str(datetime.datetime.now())
        today_year = int(today[0:4])
        today_month = int(today[5:7])
        today_day = int(today[8:10])
        time1 = datetime.datetime(today_year, today_month, today_day, 0, 0, 0)
        time2 = datetime.datetime(today_year, today_month, today_day, 23, 59, 59)
        schedule_list = user.user_agenda.filter(starttime__gte=time1, endtime__lte=time2)
        if page == 1:
            paginator = Paginator(schedule_list, per_page=10)
            schedule_list = paginator.page(1)
            schedule = serializers.serialize('json', schedule_list, ensure_ascii=False)
            schedule = json.loads(schedule)
            data['schedule'] = schedule
            data['warning'] = '1'
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        page = page + 1
        paginator = Paginator(schedule_list, per_page=5)
        try:
            warning = '1'
            schedule_list = paginator.page(page)
        except EmptyPage:
            if page < 1:
                warning = "到顶了"
                schedule_list = paginator.page(1)
            else:
                warning = "到底了"
                schedule_list = paginator.page(paginator.num_pages)
        schedule = serializers.serialize('json', schedule_list, ensure_ascii=False)
        schedule = json.loads(schedule)
        data['schedule'] = schedule
        data['warning'] = warning
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    else:
        delete = request.session.get('schedule_delete')
        if delete is not None:
            delete = delete.split(',')
            for delete_id in delete:
                if delete_id != '':
                    schedule = Agenda.objects.get(id=int(delete_id))
                    schedule.delete()
        request.session['schedule_delete'] = None
        user = User.objects.get(id=user_id)
        data = {}
        today = str(datetime.datetime.now())
        today_year = int(today[0:4])
        today_month = int(today[5:7])
        today_day = int(today[8:10])
        time1 = datetime.datetime(today_year, today_month, today_day, 0, 0, 0)
        time2 = datetime.datetime(today_year, today_month, today_day, 23, 59, 59)
        schedule_list = user.user_agenda.filter(starttime__gte=time1, endtime__lte=time2)
        paginator = Paginator(schedule_list, per_page=10)
        schedule_list = paginator.page(1)
        schedule = serializers.serialize('json', schedule_list, ensure_ascii=False)
        schedule = json.loads(schedule)
        data['schedule'] = schedule
        data['warning'] = '1'
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')

def projecthelper_page(request):
    user_id = request.session.get('user_id')
    if request.method =="POST":
        obtain = request.POST
        if 'read' in obtain:
            projectmessage_list = ProjectMessage.objects.filter(userId=user_id,ifread=0)
            for i in projectmessage_list:
                i.ifread = 1
                i.save()
            warning = '1'
            data = {'warning': warning}
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        if 'delete' in obtain:
            delete = request.POST.get('delete')
            if request.session.get('project_delete') is None:
                request.session['project_delete'] = str(delete)
            else:
                request.session['project_delete'] = request.session.get('project_delete') + ',' + str(delete)
            data = {}
            data['warning'] = '1'
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        choice = request.POST.get('choice')
        if choice == '0':
            page = int(request.POST.get('page'))
            data = {}
            projectmessage_list = ProjectMessage.objects.filter(userId=user_id, ifread=0).order_by('-id')
            paginator = Paginator(projectmessage_list, per_page=4)
            try:
                warning = '1'
                projectmessage_list = paginator.page(page)
            except EmptyPage:
                if page < 1:
                    warning = "到顶了"
                    projectmessage_list = paginator.page(1)
                else:
                    warning = "到底了"
                    projectmessage_list = paginator.page(paginator.num_pages)
            project_list = []
            for projectmessage in projectmessage_list:
                project_list.append(Project.objects.get(id=projectmessage.projectId))
            project = serializers.serialize('json', project_list, ensure_ascii=False)
            project = json.loads(project)
            data['project'] = project
            data['warning'] = warning
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        else:
            page = int(request.POST.get('page'))
            data = {}
            projectmessage_list = ProjectMessage.objects.filter(userId=user_id, ifread=1).order_by('-id')
            paginator = Paginator(projectmessage_list, per_page=4)
            try:
                warning = '1'
                projectmessage_list = paginator.page(page)
            except EmptyPage:
                if page < 1:
                    warning = "到顶了"
                    projectmessage_list = paginator.page(1)
                else:
                    warning = "到底了"
                    projectmessage_list = paginator.page(paginator.num_pages)
            project_list = []
            for projectmessage in projectmessage_list:
                project_list.append(Project.objects.get(id=projectmessage.projectId))
            project = serializers.serialize('json', project_list, ensure_ascii=False)
            project = json.loads(project)
            data['project'] = project
            data['warning'] = warning
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    else:
        delete = request.session.get('project_delete')
        if delete is not None:
            delete = delete.split(',')
            for delete_id in delete:
                if delete_id != '':
                    projectmessage = ProjectMessage.objects.get(userId=user_id,projectId=int(delete_id))
                    projectmessage.delete()
        request.session['project_delete'] = None
        data = {}
        projectmessage_list = ProjectMessage.objects.filter(userId=user_id, ifread=0).order_by('-id')
        project_list = []
        for projectmessage in projectmessage_list:
            project_list.append(Project.objects.get(id=projectmessage.projectId))
        project = serializers.serialize('json', project_list, ensure_ascii=False)
        project = json.loads(project)
        data['project'] = project
        data['warning'] = '1'
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')

def taskhelper_page(request):
    user_id = request.session.get('user_id')
    if request.method == "POST":
        obtain = request.POST
        if 'read' in obtain:
            taskmessage_list = TaskMessage.objects.filter(userId=user_id, ifread=0)
            for i in taskmessage_list:
                i.ifread = 1
                i.save()
            warning = '1'
            data = {'warning': warning}
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        if 'delete' in obtain:
            delete = request.POST.get('delete')
            if request.session.get('task_delete') is None:
                request.session['task_delete'] = str(delete)
            else:
                request.session['task_delete'] = request.session.get('task_delete') + ',' + str(delete)
            data = {}
            data['warning'] = '1'
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        choice = request.POST.get('choice')
        if choice == '0':
            page = int(request.POST.get('page'))
            data = {}
            taskmessage_list = TaskMessage.objects.filter(userId=user_id, ifread=0).order_by('-id')
            paginator = Paginator(taskmessage_list, per_page=4)
            try:
                warning = '1'
                taskmessage_list = paginator.page(page)
            except EmptyPage:
                if page < 1:
                    warning = "到顶了"
                    taskmessage_list = paginator.page(1)
                else:
                    warning = "到底了"
                    taskmessage_list = paginator.page(paginator.num_pages)
            task_list = []
            for taskmessage in taskmessage_list:
                task_list.append(Task.objects.get(id=taskmessage.taskId))
            task = serializers.serialize('json', task_list, ensure_ascii=False)
            task = json.loads(task)
            data['task'] = task
            data['warning'] = warning
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        else:
            page = int(request.POST.get('page'))
            data = {}
            taskmessage_list = TaskMessage.objects.filter(userId=user_id, ifread=1).order_by('-id')
            paginator = Paginator(taskmessage_list, per_page=4)
            try:
                warning = '1'
                taskmessage_list = paginator.page(page)
            except EmptyPage:
                if page < 1:
                    warning = "到顶了"
                    taskmessage_list = paginator.page(1)
                else:
                    warning = "到底了"
                    taskmessage_list = paginator.page(paginator.num_pages)
            task_list = []
            for taskmessage in taskmessage_list:
                task_list.append(Task.objects.get(id=taskmessage.taskId))
            task = serializers.serialize('json', task_list, ensure_ascii=False)
            task = json.loads(task)
            data['task'] = task
            data['warning'] = warning
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    else:
        delete = request.session.get('task_delete')
        if delete is not None:
            delete = delete.split(',')
            for delete_id in delete:
                if delete_id != '':
                    taskmessage = TaskMessage.objects.get(userId=user_id, taskId=int(delete_id))
                    taskmessage.delete()
        request.session['task_delete'] = None
        data = {}
        taskmessage_list = TaskMessage.objects.filter(userId=user_id, ifread=0).order_by('-id')
        task_list = []
        for taskmessage in taskmessage_list:
            task_list.append(Task.objects.get(id=taskmessage.taskId))
        task = serializers.serialize('json', task_list, ensure_ascii=False)
        task = json.loads(task)
        data['task'] = task
        data['warning'] = '1'
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
def helper_page(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    if request.method == "POST":
        data = {}
        search = request.POST.get('search')
        project_list = user.project_set.filter(name__icontains=search)
        project = serializers.serialize('json', project_list, ensure_ascii=False)
        project = json.loads(project)
        data['project'] = project
        task_list = user.task_set.filter(name__icontains=search)
        task = serializers.serialize('json', task_list, ensure_ascii=False)
        task = json.loads(task)
        data['task'] = task
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    else:
        data = {}
        data['state'] = {}
        data['state']['schedulestate'] = {}
        data['state']['projectstate'] = {}
        data['state']['taskstate'] = {}
        today = str(datetime.datetime.now())
        today_year = int(today[0:4])
        today_month = int(today[5:7])
        today_day = int(today[8:10])
        time1 = datetime.datetime(today_year, today_month, today_day, 0, 0, 0)
        time2 = datetime.datetime(today_year, today_month, today_day, 23, 59, 59)
        schedule = user.user_agenda.filter(starttime__gte=time1, endtime__lte=time2, state=0).order_by('-id')
        if schedule:
            data['state']['schedulestate']['state'] = 1
            data['state']['schedulestate']['description'] = schedule[0].description
        else:
            data['state']['schedulestate']['state'] = 0
            data['state']['schedulestate']['description'] = "无"
        project = ProjectMessage.objects.filter(userId=user_id,ifread=0).order_by('-id')
        if project:
            data['state']['projectstate']['state'] = 1
            data['state']['projectstate']['description'] = Project.objects.get(id=project[0].projectId).description
        else:
            data['state']['projectstate']['state'] = 0
            data['state']['projectstate']['description'] = "无"
        task = TaskMessage.objects.filter(userId=user_id,ifread=0).order_by('-id')
        if task:
            data['state']['taskstate']['state'] = 1
            data['state']['taskstate']['description'] = Task.objects.get(id=task[0].taskId).description
        else:
            data['state']['taskstate']['state'] = 0
            data['state']['taskstate']['description'] = "无"
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')

def friendinfo_page(request,friend_id):
    user_id = request.session.get('user_id')
    friend = User.objects.get(id=friend_id)
    if request.method == "POST":
        if Friend.objects.filter(user=user_id, friend_id=friend_id):
            warning = '已添加此好友'
            data = {'warning': warning}
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        else:
            friend = Friend.objects.create(user=user_id, avatar=friend.avatar, username=friend.username, friend=friend)
            friend.save()
            warning = '1'
            data = {'warning': warning}
            return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    else:
        data = {}
        data['friend'] = {}
        if friend.birthday:
            birthday = friend.birthday
            birthday = str(birthday).split('-')
            year = birthday[0]
            month = birthday[1]
            day = birthday[2]
            data['friend']['birthday'] = {'year': year, 'month': month, 'day': day}
        else:
            data['friend']['birthday'] = {'year': None, 'month': None, 'day': None}
        data['friend']['user_name'] = friend.username
        data['friend']['avatar'] = str(friend.avatar)
        data['friend']['constellation'] = friend.constellation
        data['friend']['profession'] = friend.profession
        data['friend']['age'] = friend.age
        data['friend']['gender'] = friend.gender
        data['friend']['introduction'] = friend.introduction
        data['friend']['telephone'] = friend.telephone
        data['friend']['email'] = friend.email
        #if user.friend_id.filter(friend=friend).exists():
        if Friend.objects.filter(friend=friend, user=user_id):
            data['isfriend'] = 1
        else:
            data['isfriend'] = 0
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
