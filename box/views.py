import boto3
from rest_framework.views import APIView
from rest_framework.response import Response
from box.models import Box, Comment, Like, Bookmark
from config.settings import AWS_STORAGE_BUCKET_NAME, AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID

# 박스 업로드 하기
class Box_upload(APIView):
    def post(self,request):
        file = request.FILES['file']
        filename = file.name
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
		                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
	    )
        s3.upload_fileobj(file,AWS_STORAGE_BUCKET_NAME,'static/'+filename,ExtraArgs={
                                                              "ContentType": file.content_type,
         })

        box_content = request.data.get('box_content')
        box_img = filename
        user_img = request.data.get('user_img')
        user_id = request.data.get('user_id')
        user_email = request.data.get('user_email')
        Box.objects.create(box_content=box_content,
                           box_img=box_img,
                           user_img=user_img,
                           user_id=user_id,
                           user_email=user_email,
                           num_of_like=0)

        return Response(status=200)

# 댓글 달기
class Create_comment(APIView):
    def post(self,request):
        box_id = request.data.get('box_id')
        user_id = request.data.get('user_id')
        content = request.data.get('content')
        user_email = request.data.get('user_email')
        Comment.objects.create(box_id=box_id,
                               user_id=user_id,
                               content=content,
                               user_email=user_email
                               )
        return Response(status=200)

# 댓글 지우기 - 본인의 댓글만 삭제 가능
class Delete_comment(APIView):
    def post(self,request):
        comment_id = request.data.get('comment_id')
        user_email = request.data.get('user_email')
        print(comment_id , user_email)
        comment = Comment.objects.filter(id=comment_id).first()

        print(comment)
        if comment is None:
            return Response(status=500, data=dict(message='삭제 실패'))
        if comment.user_email == user_email:
            comment.delete()
            return Response(status=200, data=dict(message='성공'))
        else:
            return Response(status=500, data=dict(message='본인의 댓글만 삭제 가능합니다.'))

# 좋아요 누르기
class Click_like(APIView):
    def post(self,request):
        box_id = request.data.get('box_id')
        user_email = request.data.get('user_email')
        like = request.data.get('like')

        state = Like.objects.filter(user_email=user_email,box_id=box_id).first()
        print(state)
        print(user_email)
        print(box_id)
        print(like)

        if like.lower() == 'false':
            like = False
        else:
            like = True

        if state is None:
            Like.objects.create(box_id=box_id,user_email=user_email, like= like)

        else:
           state.like = like
           state.save()

        print(like)
        return Response(status=200)
# 북마크 누르기
class Click_bookmark(APIView):
    def post(self,request):
        box_id = request.data.get('box_id')
        user_email = request.data.get('user_email')
        bookmark = request.data.get('bookmark',True)

        if bookmark.lower() == 'false':
            bookmark = False
        else:
            bookmark = True

        state = Bookmark.objects.filter(box_id=box_id,user_email=user_email).first()

        if state is None:
            Bookmark.objects.create(box_id=box_id,user_email=user_email,bookmark=bookmark)
        else:
            state.bookmark = bookmark
            state.save()

        return Response(status=200)