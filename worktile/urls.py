from django.urls import path
from worktile import views

app_name = 'worktile'
urlpatterns = [
    path('work/', views.work, name='workArea'),
    path('project/<int:project_id>', views.ProjectDetail, name='ProjectDetail'),
    path('project/<int:project_id>/task/<int:task_id>', views.TaskDetail, name='TaskDetail'),
    path('task/<int:task_id>/subtask/<subtask_id>', views.SubtaskDetail, name='SubtaskDetail'),
    path('project/<int:project_id>/task/<task_id>/manager', views.changeTaskManager, name='changeTaskManager'),
    path('task/<int:task_id>/subtask/<int:subtask_id>/manager', views.changeSubtaskManager, name='changeSubtaskManager'),
    path('project/<int:project_id>/task/<int:task_id>/new-members', views.changeTaskMembers, name='changeTaskMembers'),
    path('task/<int:task_id>/subtask/<int:subtask_id>/new-members', views.changeSubtaskMembers, name='changeSubtaskMembers'),
    path('project/<int:project_id>/new-members', views.changeProjectMembers, name='changeProjectMembers'),
    path('project/<int:project_id>/state', views.changeProjectState, name='changeProjectState'),
    path('project/<int:project_id>/task/<int:task_id>/state', views.changeTaskState, name='changeTaskState'),
    path('task/<int:task_id>/subtask/<int:subtask_id>/state', views.changeSubtaskState, name='changeSubtaskState'),
    path('project/<int:project_id>/description', views.changeProjectDescription, name='changeProjectDescription'),
    path('project/<int:project_id>/task/<int:task_id>/description', views.changeTaskDescription, name='changeTaskDescription'),
    path('task/<int:task_id>/subtask/<int:subtask_id>/description', views.changeSubtaskDescription, name='changeSubtaskDescription'),
    path('new-project', views.createProject, name='createProject'),
    path('project/<int:project_id>/new-task', views.createTask, name='createTask'),
    path('project/<int:project_id>/task/<int:task_id>/new-subtask', views.createSubtask, name='createSubtask'),
    path('project/<int:project_id>/members', views.viewProjectMembers, name='viewProjectMembers'),
    path('project/<int:project_id>/task/<int:task_id>/members', views.viewTaskMembers, name='viewTaskMembers'),
    path('task/<int:task_id>/subtask/<int:subtask_id>/members', views.viewSubtaskMembers, name='viewSubtaskMembers'),
    path('all-project', views.projectReport, name='projectReport'),
    path('all-tasks', views.myTasks, name='myTasks'),
    path('new-friends', views.add_friend, name='add_friend'),
    path('new-friend/email', views.addFriendsEmail, name='addFriendsEmail'),
    path('new-friend/username', views.addFrinedsUsername, name='addFrinedsUsername'),
    path('new-friend/telephone', views.addFrinedsTelephone, name='addFrinedsTelephone'),
]