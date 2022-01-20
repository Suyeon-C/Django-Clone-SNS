from django.db import models


# 메인 화면-왼쪽 박스에 들어갈 데이터
#유저이미지, 유저아이디,본문이미지,본문내용,박스 당 좋아요 수
class Box(models.Model):
    user_img = models.ImageField(blank=True) # 작성자 이미지(회원가입 시 등록)
    user_id = models.CharField(max_length=200, db_index=True) # 작성자 아이디
    user_email = models.EmailField(max_length=100, blank=True, null=True)
    box_img = models.ImageField(blank=True) # 글 이미지
    box_content = models.TextField() # 글 내용
    num_of_like = models.IntegerField() # 글 좋아요 수

    class Meta:
       index_together = [['id','user_id']]
    def __str__(self):
        return self.user_id

# 좋아요를 누른 박스
class Like(models.Model):
    box_id = models.IntegerField() #좋아요를 누른 박스의 ID
    user_email = models.CharField(max_length=255, blank=True, null=True) #누른 사람의 이메일
    like = models.BooleanField(default=False) #좋아요 여부(취소시, 업데이트하기 위해서 bool형)

# 댓글
class Comment(models.Model):
    box_id = models.IntegerField() #댓글을 남긴 박스
    user_id = models.CharField(max_length=30, blank=True, null=True) # 댓글을 남긴 유저의 닉네임(=아이디)
    content = models.TextField() #댓글 내용
    user_email = models.EmailField(max_length=255, blank=True, null=True) #댓글을 남긴 유저의 이메일

    class Meta:
        indexes = [
            models.Index(fields=['box_id'])
        ]

# 북마크
class Bookmark(models.Model):
    user_email = models.EmailField(max_length=255)
    box_id = models.IntegerField()
    bookmark = models.BooleanField(default=False)
