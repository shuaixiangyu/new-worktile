import datetime

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json
from worktile.models import *

#看一个项目有哪些成员的时候：
#user = User.objects.filter(project=project_id)


#工作模块主页
def work(request):
    if request.method == 'POST':
        return redirect('/worktile/404')
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        project = Project.objects.filter(user=user_id) #这样写没错
        return JsonResponse({"project": project})

#通讯录页面
def friends(request):
    if request.method == 'POST':
        return redirect('/woktile/404')
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        user_id = int(user_id)
        friends_list = Friend.objects.filter(user=user_id)
        return JsonResponse({"friends_list": friends_list})

#按照用户名搜索添加好友
def addByUsername(request):
    username = request.POST.get('username')


#添加好友
def add_friend(request):
    return

#创建项目页面：
def createProject(request):
    user_id = request.session.get('user_id')
    user_id = int(user_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        # if not members.count(user_id):
        #     members.append(user_id)
        project = Project.objects.create(name=name, description=description)
        project.save()
        return redirect('workArea')
    return JsonResponse({})

#创建任务页面,传项目id用url，worktile对url进行了编码加密
def createTask(request, project_id):
    user_id = request.session.get('user_id')
    user_id = int(user_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        starttime = request.POST.get('starttime')
        endtime = request.POST.get('endtime')
        task = Task.objects.create(name=name, description=description, starttime=starttime, endtime=endtime)
        task.save()
        project=Project.objects.filter(id=project_id).first()
        project.notstart+=1
        project.alltask+=1
        project.rate = 100 * (project.notstart + project.isgoing) / project.alltask
        project.save()
        return redirect('ProjectDetail', project_id=project_id)
    return JsonResponse({})

#创建子任务页面
def createSubtask(request, project_id, task_id):
    user_id = request.session.get('user_id')
    user_id = int(user_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        starttime = request.POST.get('starttime')
        endtime = request.POST.get('endtime')
        subtask = sonTask.objects.create(name=name, description=description, starttime=starttime, endtime=endtime)
        subtask.save()
        return redirect('TaskDetail', project_id=project_id, task_id=task_id)
    return JsonResponse({})


#修改任务负责人
def changeTaskManager(request, project_id, task_id):
    user_id = request.session.get('user_id')
    user_id = int(user_id)
    if request.method == 'POST':
        manager_id = request.POST.get('manager_id')
        task = Task.objects.filter(id=task_id).first()
        task.manager_id = manager_id
        task.save()
        return redirect('TaskDetail', project_id=project_id, task_id=task_id)
    friends_list = Friend.objects.filter(user=user_id)
    return JsonResponse({"friends_list": friends_list})

#修改子任务负责人
def changeSubtaskManager(request, task_id, subtask_id):
    user_id = request.session.get('user_id')
    user_id = int(user_id)
    if request.method == 'POST':
        manager_id = request.POST.get('manager_id')
        subtask = sonTask.objects.filter(id=subtask_id).first()
        subtask.manager_id = manager_id
        subtask.save()
        return redirect('SubtaskDetail', task_id=task_id, subtask_id=subtask_id)
    friends_list = Friend.objects.filter(user=user_id)
    return JsonResponse({"friends_list": friends_list})

#修改任务成员
def changeTaskMembers(request, project_id, task_id):
    user_id = request.session.get('user_id')
    user_id = int(user_id)
    if request.method == 'POST':
        members = request.POST.getlist('members')
        members = list(map(int, members))
        task = Task.objects.filter(id=task_id).first()
        task.user.clear()
        for member in members:
            task.user.add(User.objects.filter(id=member).first())
        task.save()
        return redirect('TaskDetail', project_id=project_id, task_id=task_id)
    friends_list = Friend.objects.filter(user=user_id)
    return JsonResponse({"friends_list": friends_list})

#修改子任务成员
def changeSubtaskMembers(request, task_id, subtask_id):
    user_id = request.session.get('user_id')
    user_id = int(user_id)
    if request.method == 'POST':
        members = request.POST.getlist('members')
        members = list(map(int, members))
        subtask = sonTask.objects.filter(id=subtask_id).first()
        subtask.user.clear()
        for member in members:
            subtask.user.add(User.objects.filter(id=member).first())
        subtask.save()
        return redirect('SubtaskDetail', task_id=task_id, subtask_id=subtask_id)
    friends_list = Friend.objects.filter(user=user_id)
    return JsonResponse({"friends_list": friends_list})

#修改项目成员
def changeProjectMembers(request, project_id):
    user_id = request.session.get('user_id')
    user_id = int(user_id)
    if request.method == 'POST':
        members = request.POST.getlist('members')
        members = list(map(int, members))
        project = Project.objects.filter(id=project_id).first()
        project.user.clear()
        for member in members:
            project.user.add(User.objects.filter(id=member).first())
        project.save()
        return redirect('ProjectDetail', project_id=project_id)
    friends_list = Friend.objects.filter(user=user_id)
    return JsonResponse({"friends_list": friends_list})

#修改项目状态
def changeProjectState(request, project_id):
    if request.method == 'POST':
        str = request.POST.get('state')
        if str == '进行中':
            state = 0
        elif str == '已完成':
            state = 1
        project = Project.objects.filter(id=project_id).first()
        project.state=state
        project.save()
        return redirect('ProjectDetail', project_id=project_id)
    return JsonResponse({})


#修改任务状态
def changeTaskState(request, project_id, task_id):
    if request.method == 'POST':
        origin = Task.objects.filter(id=task_id).get('state')
        project = Project.objects.filter(id=project_id).first()
        origin=int(origin)
        if origin == 0:
            project.notstart-=1
        elif origin == 1:
            project.isgoing-=1
        elif origin == 2:
            project.ended-=1
        str = request.POST.get('state')
        if str == '未开始':
            state = 0
            project.notstart += 1
            project.alltask += 1
            project.rate = 100 * (project.notstart+project.isgoing) / project.alltask
        elif str == '进行中':
            state = 1
            project.isgoing+=1
            project.alltask += 1
            project.rate = 100 * (project.notstart + project.isgoing) / project.alltask
        elif str == '已完成':
            state = 2
            project.ended+=1
            project.alltask += 1
            project.rate = 100 * (project.notstart + project.isgoing) / project.alltask
        project.save()
        task = Task.objects.filter(id=task_id).first()
        task.state=state
        task.save()
        return redirect('TaskDetail', project_id=project_id, task_id=task_id)
    return JsonResponse({})

#修改子任务状态
def changeSubtaskState(request, task_id, subtask_id):
    if request.method == 'POST':
        str = request.POST.get('state')
        if str == '未开始':
            state = 0
        elif str == '进行中':
            state = 1
        elif str == '已完成':
            state = 2
        subtask = sonTask.objects.filter(id=subtask_id).first()
        subtask.state=state
        subtask.save()
        return redirect('SubtaskDetail', task_id=task_id, subtask_id=subtask_id)
    return JsonResponse({})

#修改项目描述
def changeProjectDescription(request, project_id):
    if request.method == 'POST':
        description = request.POST.get('description')
        project = Project.objects.filter(id=project_id).first()
        project.description=description
        project.save()
        return redirect('ProjectDetail', project_id=project_id)
    return JsonResponse({})

#修改任务描述
def changeTaskDescription(request, project_id, task_id):
    if request.method == 'POST':
        description = request.POST.get('description')
        task = Task.objects.filter(id=task_id).first()
        task.description=description
        task.save()
        return redirect('TaskDetail', project_id, task_id)
    return JsonResponse({})

#修改子任务描述
def changeSubtaskDescription(request, task_id, subtask_id):
    if request.method == 'POST':
        description = request.POST.get('description')
        subtask=sonTask.objects.filter(id=subtask_id).first()
        subtask.description = description
        subtask.save()
        return redirect('SubtaskDetail', task_id=task_id, subtask_id=subtask_id)
    return JsonResponse({})

#项目详情
def ProjectDetail(request, project_id):
    project = Project.objects.filter(id=project_id).first()
    if project.ifread == 0:
        project.ifread = 1
        project.save()
    name = project.name
    description = project.description
    state = project.state
    return JsonResponse({"name":name, "description":description, "state":state})

#任务详情
def TaskDetail(request, project_id, task_id):
    project = Project.objects.filter(id=project_id).first()
    task = Task.objects.filter(id=task_id).first()
    if task.ifread == 0:
        task.ifread =1
        task.save()
    project_name=project.name
    task_name=task.name
    description = task.description
    starttime=task.starttime
    endtime=task.endtime
    state=task.state
    manager_id=task.manager_id
    manager_name=User.objects.filter(id=manager_id).get('username')
    subtask_num = sonTask.objects.filter(task=task_id).count()
    return JsonResponse({"project_name":project_name, "task_name":task_name, "project_id":project_id,
                         "description":description, "starttime":starttime, "endtime":endtime,"state":state,
                         "manager_id":manager_id,"manager_name":manager_name,"subtask_num":subtask_num})

#子任务详情
def SubtaskDetail(request, task_id, subtask_id):
    subtask = sonTask.objects.filter(id=subtask_id).first()
    if subtask.ifread == 0:
        subtask.ifread = 1
        subtask.save()
    task_id=task_id
    task_name=Task.objects.filter(id=task_id).get('name')
    description = subtask.description
    starttime=subtask.starttime
    endtime=subtask.endtime
    state=subtask.state
    manager_id=subtask.manager_id
    manager_name=User.objects.filter(id=manager_id).get('username')
    project_id=subtask.project_id
    project_name=Project.objects.filter(id=project_id).get('name')
    return JsonResponse({"project_name":project_name, "task_name":task_name, "project_id":project_id,
                         "description":description, "starttime":starttime, "endtime":endtime,"state":state,
                         "manager_id":manager_id,"manager_name":manager_name,"task_id":task_id})

#查看项目成员
def viewProjectMembers(request, project_id):
    project=Project.objects.filter(id=project_id).first()
    members=project.user.all()
    return JsonResponse({"members":members})

#查看任务成员
def viewTaskMembers(request, project_id, task_id):
    task=Task.objects.filter(id=task_id).first()
    members=task.user.all()
    return JsonResponse({"members":members})

#查看子任务成员
def viewSubtaskMembers(request, task_id, subtask_id):
    subtask = sonTask.objects.filter(id=subtask_id).first()
    members=subtask.user.all()
    return JsonResponse({"members":members})

#统计报表页面
def projectReport(request):
    user_id = request.session.get('user_id')
    user_id = int(user_id)
    user = User.objects.filter(id=user_id).first()
    projects=user.project_set.all()
    return JsonResponse({"projects":projects})

#我的任务页面
def myTasks(request):
    user_id = request.session.get('user_id')
    user_id = int(user_id)
    notstart=Task.objects.filter(user=user_id).filter(state=0).all()
    isgoing=Task.objects.filter(user=user_id).filter(state=1).all()
    ended=Task.objects.filter(user=user_id).filter(state=2).all()
    return JsonResponse({"notstart":notstart, "isgoing":isgoing, "ended":ended})

#添加好友
def addFrineds(request):
    user_id = request.session.get('user_id')
    user_id = int(user_id)
    return JsonResponse({"user_id":user_id})

#按照邮箱添加好友
def addFriendsEmail(request):
    if request.method == 'POST':
        email=request.POST.get('email')
        user_list=User.objects.filter(email__exact=email).all()
        return JsonResponse({"user_list":user_list})
    return JsonResponse({})

#按照用户名添加好友
def addFrinedsUsername(request):
    if request.method == 'POST':
        username=request.POST.get('username')
        user_list=User.objects.filter(username__exact=username).all()
        return JsonResponse({"user_list":user_list})
    return JsonResponse({})

#按照手机号添加好友
def addFrinedsTelephone(request):
    if request.method == 'POST':
        telephone=request.POST.get('username')
        user_list=User.objects.filter(telephone__exact=telephone)
        return JsonResponse({"telephone":telephone})
    return JsonResponse({})





