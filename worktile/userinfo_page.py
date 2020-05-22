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
        birthday = user.birthday
        birthday = str(birthday).split('-')
        year = birthday[0]
        month = birthday[1]
        day = birthday[2]
        data['user'] = {}
        data['user']['username'] = user.username
        data['user']['avatar'] = str(user.avatar)
        data['user']['birthday']['year'] = year
        data['user']['birthday']['month'] = month
        data['user']['birthday']['day'] = day
        data['user']['constellation'] = user.constellation
        data['user']['profession'] = user.profession
        data['user']['age'] = user.age
        data['user']['gender'] = user.gender
        data['user']['introduction'] = user.introduction
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, charset='utf-8')