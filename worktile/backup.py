import datetime

from django.core import serializers
from django.forms import model_to_dict
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json

from Newworktile import settings
from worktile.models import *


# 看一个项目有哪些成员的时候：
# user = User.objects.filter(project=project_id)

def testList(request):
    l = request.POST.getlist('list')
    data = {}
    data['content'] = l
    relist=[]
    for a in l:
        relist.append(int(a))
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
        project = {"project": project}
        return JsonResponse(project,safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
    return JsonResponse({})


# 通讯录页面
def friends(request):
    if request.method == 'POST':
        return redirect('worktile:error')
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        if user_id is None:
            return redirect('worktile:login')
        user_id = int(user_id)
        friends = Friend.objects.filter(user=user_id)
        friends_list=[]
        for a in friends:
            a = (model_to_dict(a, fields=['username', 'avatar', 'friend']))
            a['avatar'] = str(a['avatar'])
            friends_list.append(a)
        friends_list = {"friends_list": friends_list}
        return JsonResponse(friends_list, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


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
        project = Project.objects.create(name=name, description=description)
        project.user.add(User.objects.filter(id=user_id).first())
        project.save()
        return redirect('worktile:workArea')
    return JsonResponse({})


# 创建任务页面,传项目id用url，worktile对url进行了编码加密
def createTask(request, project_id):
    if Project.objects.all().count() == 0:
        return redirect('worktile:error')

    maxn = Project.objects.last().id
    if int(project_id) > int(maxn):
        return redirect('worktile:error')

    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
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
        project = Project.objects.filter(id=project_id).first()
        project.notstart += 1
        project.alltask += 1
        project.rate = 100 * (project.ended) / project.alltask
        project.save()
        return redirect('worktile:ProjectDetail', project_id=project_id)
    data = {
        "project_id": project_id,
    }
    json = {"data": data}
    return JsonResponse(json, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


# 创建子任务页面
def createSubtask(request, project_id, task_id):
    if Project.objects.all().count() == 0 or Task.objects.all().count() == 0:
        return redirect('worktile:error')

    maxn1 = Project.objects.last().id
    if int(project_id) > int(maxn1):
        return redirect('worktile:error')

    maxn2 = Task.objects.last().id
    if int(task_id) > int(maxn2):
        return redirect('worktile:error')

    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
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
        print('ok')
        return redirect('worktile:TaskDetail', project_id=project_id, task_id=task_id)
    elif request.method == 'GET':
        data = {
            "project_id": project_id,
            "task_id": task_id,
        }
        json = {"data":data}
        return JsonResponse(json, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


# 修改任务负责人
def changeTaskManager(request, project_id, task_id):
    if Project.objects.all().count() == 0 or Task.objects.all().count() == 0:
        return redirect('worktile:error')

    maxn1 = Project.objects.last().id
    if int(project_id) > int(maxn1):
        return redirect('worktile:error')

    maxn2 = Task.objects.last().id
    if int(task_id) > int(maxn2):
        return redirect('worktile:error')

    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')

    user_id = int(user_id)
    manager = Task.objects.get(id=task_id).manager_id
    members = Task.objects.get(id=task_id).user.all()
    id_list = []
    for member in members:
        id_list.append(member.id)
    if user_id not in id_list and user_id != manager:
        return redirect('worktile:error')

    if request.method == 'POST':
        manager_id = request.POST.get('manager_id')
        task = Task.objects.filter(id=task_id).first()
        task.manager_id = manager_id
        task.save()
        return redirect('worktile:TaskDetail', project_id=project_id, task_id=task_id)
    friends = Friend.objects.filter(user=user_id).all()
    friends_list = []
    for a in friends:
        friends_list.append(model_to_dict(a, fields=['username', 'avatar', 'friend_id']))
    data = {"friends_list": friends_list}
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


# 修改子任务负责人
def changeSubtaskManager(request, task_id, subtask_id):
    if sonTask.objects.all().count() == 0 or Task.objects.all().count() == 0:
        return redirect('worktile:error')

    maxn1 = Task.objects.last().id
    if int(task_id) > int(maxn1):
        return redirect('worktile:error')

    maxn2 = sonTask.objects.last().id
    if int(subtask_id) > int(maxn2):
        return redirect('worktile:error')

    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user_id = int(user_id)

    manager = sonTask.objects.get(id=subtask_id).manager_id
    members = sonTask.objects.get(id=subtask_id).user.all()
    id_list = []
    for member in members:
        id_list.append(member.id)
    if user_id not in id_list and user_id != manager:
        return redirect('worktile:error')

    if request.method == 'POST':
        manager_id = request.POST.get('manager_id')
        subtask = sonTask.objects.filter(id=subtask_id).first()
        subtask.manager_id = manager_id
        subtask.save()
        return redirect('worktile:SubtaskDetail', task_id=task_id, subtask_id=subtask_id)
    friends = Friend.objects.filter(user=user_id).all()
    friends_list = []
    for a in friends:
        friends_list.append(model_to_dict(a, fields=['username', 'avatar', 'friend_id']))
    data = {"friends_list": friends_list}
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


# 修改任务成员
def changeTaskMembers(request, project_id, task_id):
    if Project.objects.all().count() == 0 or Task.objects.all().count() == 0:
        return redirect('worktile:error')
    maxn1 = Project.objects.last().id
    if project_id > maxn1:
        return redirect('worktile:error')
    maxn2 = Task.objects.last().id
    if task_id > maxn2:
        return redirect('worktile:error')
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user_id = int(user_id)
    manager = Task.objects.get(id=task_id).manager_id
    members = Task.objects.get(id=task_id).user.all()
    id_list = []
    for member in members:
        id_list.append(member.id)
    if user_id not in id_list and user_id != manager:
        return redirect('worktile:error')
    if request.method == 'POST':
        members = request.POST.getlist('members')
        members = list(map(int, members))
        task = Task.objects.filter(id=task_id).first()
        task.user.clear()
        for member in members:
            task.user.add(User.objects.filter(id=member).first())
        task.save()
        return redirect('worktile:TaskDetail', project_id=project_id, task_id=task_id)
    friends = Friend.objects.filter(user=user_id).all()
    friends_list = []
    for a in friends:
        friends_list.append(model_to_dict(a, fields=['username', 'avatar', 'friend_id']))
    data = {"friends_list": friends_list}
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


# 修改子任务成员
def changeSubtaskMembers(request, task_id, subtask_id):
    if sonTask.objects.all().count() == 0 or Task.objects.all().count() == 0:
        return redirect('worktile:error')

    maxn1 = Task.objects.last().id
    if task_id > maxn1:
        return redirect('worktile:error')

    maxn2 = sonTask.objects.last().id
    if subtask_id > maxn2:
        return redirect('worktile:error')

    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user_id = int(user_id)

    manager = sonTask.objects.get(id=subtask_id).manager_id
    members = sonTask.objects.get(id=subtask_id).user.all()
    id_list = []
    for member in members:
        id_list.append(member.id)
    if user_id not in id_list and user_id != manager:
        return redirect('worktile:error')

    if request.method == 'POST':
        members = request.POST.getlist('members')
        members = list(map(int, members))
        subtask = sonTask.objects.filter(id=subtask_id).first()
        subtask.user.clear()
        for member in members:
            subtask.user.add(User.objects.filter(id=member).first())
        subtask.save()
        return redirect('worktile:SubtaskDetail', task_id=task_id, subtask_id=subtask_id)
    friends = Friend.objects.filter(user=user_id).all()
    friends_list = []
    for a in friends:
        friends_list.append(model_to_dict(a, fields=['username', 'avatar', 'friend_id']))
    data = {"friends_list": friends_list}
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


# 修改项目成员
def changeProjectMembers(request, project_id):
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
        return redirect('worktile:error')

    if request.method == 'POST':
        print('ok')
        members = request.POST.getlist('members')
        project = Project.objects.filter(id=project_id).first()
        project.user.clear()
        print(request.POST)
        for member in members:
            a = int(member)
            print(str(a))
            project.user.add(User.objects.filter(id=a).first())
        project.save()
        return redirect('worktile:ProjectDetail', project_id=project_id)
    friends = Friend.objects.filter(user=user_id).all()
    friends_list = []
    for a in friends:
        friends_list.append(model_to_dict(a, fields=['username', 'avatar', 'friend_id']))
    data = {"friends_list": friends_list}
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')

# 修改项目状态
def changeProjectState(request, project_id):
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
        return redirect('worktile:error')
    if request.method == 'POST':
        str = request.POST.get('state')
        if int(str) == 0:
            state = 0
        elif int(str) == 1:
            state = 1
        project = Project.objects.filter(id=project_id).first()
        project.state = state
        project.save()
        return redirect('worktile:ProjectDetail', project_id=project_id)
    return JsonResponse({})


# 修改任务状态
def changeTaskState(request, project_id, task_id):
    if Project.objects.all().count() == 0 or Task.objects.all().count() == 0:
        return redirect('worktile:error')
    maxn1 = Project.objects.last().id
    if project_id > maxn1:
        return redirect('worktile:error')
    maxn2 = Task.objects.last().id
    if task_id > maxn2:
        return redirect('worktile:error')
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user_id = int(user_id)
    manager = Task.objects.get(id=task_id).manager_id
    members = Task.objects.get(id=task_id).user.all()
    id_list = []
    for member in members:
        id_list.append(member.id)
    if user_id not in id_list and user_id != manager:
        return redirect('worktile:error')
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
            project.alltask += 1
            project.rate = 100 * (project.ended) / project.alltask
        elif int(str) == 1:
            state = 1
            project.isgoing += 1
            project.alltask += 1
            project.rate = 100 * (project.ended) / project.alltask
        elif int(str) == 2:
            state = 2
            project.ended += 1
            project.alltask += 1
            project.rate = 100 * (project.ended) / project.alltask
        project.save()
        task = Task.objects.filter(id=task_id).first()
        task.state = state
        task.save()
        return redirect('worktile:TaskDetail', project_id=project_id, task_id=task_id)
    return JsonResponse({})


# 修改子任务状态
def changeSubtaskState(request, task_id, subtask_id):
    if sonTask.objects.all().count() == 0 or Task.objects.all().count() == 0:
        return redirect('worktile:error')

    maxn1 = Task.objects.last().id
    if task_id > maxn1:
        return redirect('worktile:error')

    maxn2 = sonTask.objects.last().id
    if subtask_id > maxn2:
        return redirect('worktile:error')

    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user_id = int(user_id)

    manager = sonTask.objects.get(id=subtask_id).manager_id
    members = sonTask.objects.get(id=subtask_id).user.all()
    id_list = []
    for member in members:
        id_list.append(member.id)
    if user_id not in id_list and user_id != manager:
        return redirect('worktile:error')

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
        return redirect('worktile:SubtaskDetail', task_id=task_id, subtask_id=subtask_id)
    return JsonResponse({})


# 修改项目描述
def changeProjectDescription(request, project_id):
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
        return redirect('worktile:error')

    if request.method == 'POST':
        description = request.POST.get('description')
        project = Project.objects.filter(id=project_id).first()
        project.description = description
        project.save()
        return redirect('worktile:ProjectDetail', project_id=project_id)
    return JsonResponse({})


# 修改任务描述
def changeTaskDescription(request, project_id, task_id):
    if Project.objects.all().count() == 0:
        return redirect('worktile:error')
    if Task.objects.all().count() == 0:
        return redirect('worktile:error')
    maxn1 = Project.objects.last().id
    if project_id > maxn1:
        return redirect('worktile:error')
    maxn2 = Task.objects.last().id
    if task_id > maxn2:
        return redirect('worktile:error')
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user_id = int(user_id)
    manager = Task.objects.get(id=task_id).manager_id
    members = Task.objects.get(id=task_id).user.all()
    id_list = []
    for member in members:
        id_list.append(member.id)
    if user_id not in id_list and user_id != manager:
        return redirect('worktile:error')
    if request.method == 'POST':
        description = request.POST.get('description')
        task = Task.objects.filter(id=task_id).first()
        task.description = description
        task.save()
        return redirect('worktile:TaskDetail', project_id, task_id)
    return JsonResponse({})


# 修改子任务描述
def changeSubtaskDescription(request, task_id, subtask_id):
    if sonTask.objects.all().count() == 0 or Task.objects.all().count() == 0:
        return redirect('worktile:error')

    maxn1 = Task.objects.last().id
    if task_id > maxn1:
        return redirect('worktile:error')

    maxn2 = sonTask.objects.last().id
    if subtask_id > maxn2:
        return redirect('worktile:error')

    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user_id = int(user_id)

    manager = sonTask.objects.get(id=subtask_id).manager_id
    members = sonTask.objects.get(id=subtask_id).user.all()
    id_list = []
    for member in members:
        id_list.append(member.id)
    if user_id not in id_list and user_id != manager:
        return redirect('worktile:error')

    if request.method == 'POST':
        description = request.POST.get('description')
        subtask = sonTask.objects.filter(id=subtask_id).first()
        subtask.description = description
        subtask.save()
        return redirect('worktile:SubtaskDetail', task_id=task_id, subtask_id=subtask_id)
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
    name = project.name
    description = project.description
    state = project.state
    data = {
        "name": name,
        "description": description,
        "state": state,
        "right": 1,
    }
    json = {"data": data}
    return JsonResponse(json, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


# 任务详情
def TaskDetail(request, project_id, task_id):
    print('111')
    if Project.objects.all().count() == 0 or Task.objects.all().count() == 0:
        return redirect('worktile:error')


    maxn1 = Project.objects.last().id
    if project_id > maxn1:
        return redirect('worktile:error')

    maxn2 = Task.objects.last().id
    if task_id > maxn2:
        return redirect('worktile:error')


    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user_id = int(user_id)

    print('ok')
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
    subtask_num = sonTask.objects.filter(task=task_id).count()
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
    }
    json = {"data": data}
    return JsonResponse(json, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')



# 子任务详情
def SubtaskDetail(request, task_id, subtask_id):
    if sonTask.objects.all().count() == 0 or Task.objects.all().count() == 0:
        return redirect('worktile:error')

    maxn1 = Task.objects.last().id
    if int(task_id) > maxn1:
        return redirect('worktile:error')

    maxn2 = sonTask.objects.last().id
    if int(subtask_id) > maxn2:
        return redirect('worktile:error')

    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user_id = int(user_id)

    manager = sonTask.objects.get(id=subtask_id).manager_id
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
    if user_id not in id_list and user_id != manager:
        data = {"message": "抱歉，您没有权限查看该项目"}
        json = {"data": data}
        return JsonResponse(json, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')

    subtask = sonTask.objects.filter(id=subtask_id).first()
    if subtask.ifread == 0:
        subtask.ifread = 1
        subtask.save()
    task_id = task_id
    task_name = Task.objects.filter(id=task_id).first().name
    description = subtask.description
    starttime = subtask.starttime
    endtime = subtask.endtime
    state = subtask.state
    manager_id = subtask.manager_id
    manager_name = User.objects.filter(id=manager_id).first().username
    project_id = subtask.project_id
    project_name = Project.objects.filter(id=project_id).first().name
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
        "task_id": task_id,
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
    if Project.objects.all().count() == 0 or Task.objects.all().count() == 0:
        return redirect('worktile:error')

    maxn1 = Project.objects.last().id
    if project_id > maxn1:
        return redirect('worktile:error')

    maxn2 = Task.objects.last().id
    if task_id > maxn2:
        return redirect('worktile:error')

    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user_id = int(user_id)

    manager = Task.objects.get(id=task_id).manager_id
    members = Task.objects.get(id=task_id).user.all()
    id_list = []
    for member in members:
        id_list.append(member.id)
    if user_id not in id_list and user_id != manager:
        return redirect('worktile:error')

    task = Task.objects.filter(id=task_id).first()
    members_list = task.user.all()
    members = []
    for a in members_list:
        a = (model_to_dict(a, fields=['username', 'avatar', 'id']))
        a['avatar'] = str(a['avatar'])
        members.append(a)
    data = {"members": members}
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


# 查看子任务成员
def viewSubtaskMembers(request, task_id, subtask_id):
    if sonTask.objects.all().count() == 0 or Task.objects.all().count() == 0:
        return redirect('worktile:error')

    maxn1 = Task.objects.last().id
    if task_id > maxn1:
        return redirect('worktile:error')

    maxn2 = sonTask.objects.last().id
    if subtask_id > maxn2:
        return redirect('worktile:error')

    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('worktile:login')
    user_id = int(user_id)

    manager = sonTask.objects.get(id=subtask_id).manager_id
    members = sonTask.objects.get(id=subtask_id).user.all()
    id_list = []
    for member in members:
        id_list.append(member.id)
    if user_id not in id_list and user_id != manager:
        return redirect('worktile:error')

    subtask = sonTask.objects.filter(id=subtask_id).first()
    members_list = subtask.user.all()
    members = []
    for a in members_list:
        a = (model_to_dict(a, fields=['username', 'avatar', 'id']))
        a['avatar'] = str(a['avatar'])
        members.append(a)
    data = {"members": members}
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


# 我的任务页面
def myTasks(request):
    user_id = request.session.get('user_id')
    user_id = int(user_id)
    notstart = Task.objects.filter(user=user_id).filter(state=0).all()
    isgoing = Task.objects.filter(user=user_id).filter(state=1).all()
    ended = Task.objects.filter(user=user_id).filter(state=2).all()
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
    json = {"data": data}
    return JsonResponse(json, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')


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

from django.shortcuts import render,redirect

from worktile.models import *
import re
from django.core import serializers
from django.http import JsonResponse,HttpResponse
import json
from django.core.mail import send_mail
import random
import datetime

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
            elif len(telephone) != 11:
                warning = '手机号不是11位?'
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
                    try:
                        send_mail(subject='注册验证码',
                                  message='欢迎注册，您本次注册的验证码为' + s,
                                  from_email=settings.EMAIL_HOST_USER,
                                  recipient_list=[email])
                        warning = '验证码已发送'
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
                              message='您本次重置密码的验证码为：' + s,
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
                friend_list = Friend.objects.filter(user=user.id)
                for i in friend_list:
                    i.username = name
                    i.save()
                warning = '1'
                data = {'warning': warning}
                return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')
        elif 'newavatar' in request.FILES:
            picture = request.FILES.get('newavatar')
            z = ['jpg', 'JPG', 'png', 'PNG', 'bmp', 'BMP']
            if picture is None:
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
                image = "media/user/" + user.telephone + s + picture.name[-4:]
                user.avatar = image
                user.save()
                friend_list = Friend.objects.filter(user=user.id)
                for i in friend_list:
                    i.avatar = image
                    i.save()
                fname = settings.STATIC_ROOT + "/media/user/" + user.telephone + s + picture.name[-4:]
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
        else:
            user.state = 0
            user.save()
            request.session['user_id'] = None
            return redirect('worktile:login')
    else:
        data = {}
        data['user'] = {}
        data['user']['username'] = user.username
        data['user']['avatar'] = str(user.avatar)
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

