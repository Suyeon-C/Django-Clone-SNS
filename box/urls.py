from django.urls import path
from .views import Box_upload, Create_comment, Click_like, Click_bookmark, Delete_comment

urlpatterns = [
        path('upload/', Box_upload.as_view(), name='upload_box'),
        path('comment/create',Create_comment.as_view(), name='create_comment'),
        path('comment/delete',Delete_comment.as_view(), name='delete_comment'),
        path('like',Click_like.as_view(),name='click_like'),
        path('bookmark',Click_bookmark.as_view(), name='click_bookmark'),
]