from django.shortcuts import render
from rest_framework.views import APIView
from user.models import User
from box.models import Box, Like, Comment, Bookmark
from django.contrib import messages

class Main(APIView):
    def get(self,request): #GET으로 실행했을 때
        user_email = request.session.get('user_email', None) #로그인 하지 않았을 때
        if user_email is None:
            return render(request, 'user/user_login.html',{'messages': '로그인 후 이용 가능합니다.'})

        others = User.objects.all()
        user = User.objects.filter(user_email=user_email).first()
        print(user_email)
        box_lists = Box.objects.filter(user_email=user_email).order_by('-id') # 등록된 순서대로 나열
        print(box_lists)
        box_list = [] #리스트
        for box in box_lists:
            num_of_like = Like.objects.filter(box_id=box.id, like=True).count() # 좋아요 수
            like = Like.objects.filter(box_id=box.id, like=True).exists() # 좋아요를 누른 박스
            comment_list = Comment.objects.filter(box_id=box.id)
            bookmark = Bookmark.objects.filter(box_id=box.id,bookmark=True, user_email=user_email).exists()
            print(bookmark)
            box_list.append(dict(
                box_id = box.id,
                user_id =box.user_id,
                box_img = box.box_img,
                box_content = box.box_content,
                num_of_like=num_of_like,
                like=like,
                comment_list=comment_list,
                user_img=user.user_img,
                bookmark=bookmark
            ))

        return render(request, 'sns/main.html', context=dict(box_list=box_list,
                                                            user=user, others=others))
    # 회원 찾기: 검색 기능
    def search(self,request, **kwargs):
        context = super().search(**kwargs)
        search_keyword = request.data.get('q', '')

        if len(search_keyword) > 1:
            context['q'] = search_keyword
        return context



