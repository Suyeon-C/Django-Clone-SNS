from django.contrib import admin
from box.models import Box


class BoxAdmin(admin.ModelAdmin):
    list_display = ['user_img','user_id','box_img','box_content','num_of_like']

admin.site.register(Box, BoxAdmin)