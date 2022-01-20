import json
import uuid

import boto3
from django.contrib.auth import login, logout
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password
from django.template.loader import render_to_string
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib import messages

from box.models import Box, Like, Comment, Bookmark
from config.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME
from .forms import CustomSetPasswordForm
from .helper import email_auth_num, send_mail
from .models import User, Follow


# 회원가입
class Signup(APIView):
    def get(self, request): #get으로 요청
        return render(request,'user/user_signup.html')

    def post(self,request):
        password = request.data.get('password')
        user_email = request.data.get('user_email')
        user_id = request.data.get('user_id')
        user_name = request.data.get('user_name')
        # 중복 체크가 안됨
        # 이미 가입된 이메일이라면
        if User.objects.filter(user_email=user_email).exists():
            return Response(status=500, data='이미 가입된 정보가 있는 이메일 입니다')
        elif User.objects.filter(user_id=user_id).exists():
            return Response(status=500, data='다른 닉네임을 골라주세요')

        # make_password 암호화
        User.objects.create(password=make_password(password),
                            user_email=user_email,
                            user_id=user_id,
                            user_name=user_name)

        return Response(status=200, data="회원가입 성공했습니다.")

# 회원가입 완료 후 성공 화면
class Success(APIView):
    def get(self,request):
        return render(request,'user/success.html')


# 로그인
class Login(APIView):
    def get(self, request):
        return render(request, 'user/user_login.html')

    def post(self, request):
        user_email = request.data.get('user_email',None)
        password = request.data.get('password',None)
         #  user 전까지 작동안함
        if user_email is None:
            return Response(status=500, data='이메일을 입력하세요 ')
        if password is None :
            return Response(status=500, data='비밀번호를 입력하세요')

        user = User.objects.filter(user_email=user_email).first()

        if user is None:
            return Response(status=500, data='가입된 정보가 없습니다.')
        if check_password(password, user.password) is False:
            return Response(status=500, data='잘못된 비밀번호 입니다.')

        request.session['loginCheck'] = True
        request.session['user_email'] = user.user_email
        request.session['user_id'] = user.user_id

        return Response(status=200, data='로그인 성공')

# 로그아웃
class Logout(APIView):
    def get(self,request):
        # 세션 날림
        request.session.flush()
        return render(request,'user/user_login.html')

# 이메일 찾기
class Ajax_email_search(APIView):
    def get(self,request):
        return render(request,'user/user_email_search.html')

    def post(self,request):
        user_name = request.data.get('user_name')
        user_id = request.data.get('user_id')
        result_email = User.objects.get(user_name=user_name, user_id=user_id)

        return HttpResponse(json.dumps({"result_email": result_email.user_email}, cls=DjangoJSONEncoder),
                            content_type = "application/json")


# 비밀번호 찾기 AJAX통신 - 인증번호 이메일 보내기
class Ajax_pw_auth_send(APIView):
    def get(self,request):
        return render(request, 'user/user_pw_search.html')

    def post(self,request):
        user_email = request.data.get('user_email')
        user_name = request.data.get('user_name')
        result_user = User.objects.get(user_email=user_email, user_name=user_name)
        if result_user:
            auth_num = email_auth_num()
            result_user.auth = auth_num
            result_user.save()

            send_mail(
                'DALIY SHARE: 비밀번호 찾기 인증번호 입니다.',
                [user_email],
                html= render_to_string('user/send_mail_pw.html', {
                    'auth_num':auth_num,
                }),
            )
        return HttpResponse(json.dumps({"result": result_user.user_email}, cls=DjangoJSONEncoder), content_type = "application/json")

# 비밀번호 찾기- 인증번호 확인
class Ajax_pw_auth_confirm(APIView):
    def post(self, request):
        user_email = request.data.get('user_email')
        input_auth_num = request.data.get('input_auth_num')
        result_user = User.objects.get(user_email=user_email, auth=input_auth_num)
        result_user.auth = ""
        result_user.save()
        request.session['auth'] = result_user.user_email

        return HttpResponse(json.dumps({"result": result_user.user_email}, cls=DjangoJSONEncoder),
                        content_type="application/json")

# 인증번호가 맞으면 비밀번호 변경
def auth_pw_reset_view(request):
    if request.method == 'GET':
        if not request.session.get('auth',False):
            raise PermissionError
        return render(request, 'user/pw_change.html')

    if request.method == 'POST':
        session_user = request.session['auth']
        current_user = User.objects.get(user_email = session_user)
        login(request,current_user)

        reset_password = CustomSetPasswordForm(request.user, request.POST)

        if reset_password.is_valid():
            reset_password.save()
            messages.success(request,'비밀번호 변경 완료! 변경된 비밀번호로 로그인하세요')
            logout(request)
            return render(request,'user/user_login.html')
        else:
            logout(request)
            request.session['auth'] = session_user
    else:
        reset_password = CustomSetPasswordForm(request.user)

    return render(request,'user/pw_change.html', {'result':reset_password})

# 회원 상세정보
class Profile(APIView):
    def get(self,request):
        user_email = request.session.get('user_email')
        user_id = request.session.get('user_id')
        print(user_email, user_id)
        if user_email is None:
            return render(request, 'user/user_login.html')

        user = User.objects.filter(user_email=user_email).first()
        if user is None:
            return render(request,'user/user_login.html')

        # 게시물 리스트
        all_box_lists = Box.objects.filter(user_id = user_id).order_by('-id')
        print(all_box_lists)
        box_count = all_box_lists.count()  # 등록된 박스의 갯수
        print(box_count)
        box_list = []
        row_box_list = []

        for box in all_box_lists:
            num_of_like = Like.objects.filter(box_id=box.id, like=True).count()  # 좋아요 수
            like = Like.objects.filter(box_id=box.id, like=True, user_email=user_email).exists()  # 좋아요를 누른 박스
            comment_count = Comment.objects.filter(box_id=box.id).count()
            row_box_list.append(dict(
                num_of_like=num_of_like,
                like=like,
                comment_count=comment_count,
                box_id=box.id,
                user_id=box.user_id,
                box_img=box.box_img,
                box_content=box.box_content,
                user_img=box.user_img
            ))

            if len(row_box_list) == 3:
                box_list.append(dict(row_box_list=row_box_list))
                row_box_list = [] # 연속으로 두번 나오는 것을 방지

        if len(row_box_list) > 0:
            box_list.append(dict(row_box_list=row_box_list))
            print(row_box_list)

        following_count = Follow.objects.filter(follower=user_email, active=True).count()
        follower_count = Follow.objects.filter(following=user_email, active=True).count()

        # 북마크 리스트
        all_bookmark_lists = Bookmark.objects.filter(user_email=user_email,bookmark=True).order_by('-id')
        print(all_bookmark_lists)
        bookmark_count = all_bookmark_lists.count()
        print(bookmark_count)
        bookmark_list = []
        row_bookmark_list = []
        for bookmark in all_bookmark_lists:
            box = Box.objects.filter(id=bookmark.box_id).first()
            num_of_like= Like.objects.filter(box_id=box.id, like=True).count()
            like = Like.objects.filter(box_id=box.id, like=True, user_email=user_email).exists()
            comment_count = Comment.objects.filter(box_id=box.id).count()
            row_bookmark_list.append(dict(
                box_id=box.id,
                user_img=box.user_img,
                user_id=box.user_id,
                box_img=box.box_img,
                box_content=box.box_content,
                num_of_like=num_of_like,
                like=like,
                comment_count=comment_count
            ))

            if len(row_bookmark_list) == 3:
                bookmark_list.append(dict(row_bookmark_list=row_bookmark_list))
                row_bookmark_list = []

        if len(row_bookmark_list) > 0:
            bookmark_list.append(dict(row_bookmark_list=row_bookmark_list))

        return render(request, 'user/user_profile.html', context=dict(box_list=box_list, bookmark_list=bookmark_list, box_count= box_count,following_count =following_count,follower_count= follower_count,
                                                          user=user))

# 회원 정보 수정
class UpdateProfile(APIView):
    def post(self,request):
        user_email = request.session.get('user_email')
        user = User.objects.filter(user_email=user_email).first()
        if user is None:
            return render(request,'user/user_signup.html')

        file = request.FILES['file']
        if file is None:
            return Response(status=500)
        filename = file.name
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        s3.upload_fileobj(file, AWS_STORAGE_BUCKET_NAME,'static/users/'+filename,
                          ExtraArgs={"ContentType": file.content_type,}
        )
        user.user_img = filename
        user.save()

        return Response(status=200, data={'filename':filename})

# 팔로우 추가
class InsertFollow(APIView):
    def post(self,request):
        follower = request.session.get('user_email')
        following = request.data.get('following')
        active = request.data.get('active',True)

        if active.lower() == 'false':
            active = True
        else:
            active = False
        print(active)
        state = Follow.objects.filter(follower=follower,following=following).first()

        if state is None:
            Follow.objects.create(follower=follower,following=following,active=active)

        else:
            state.active = active
            state.save()

        return Response(status=200)






