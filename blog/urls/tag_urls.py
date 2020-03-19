from django.urls import re_path, path


from ..views import (TagCreate, TagDelete, TagDetail,
                     TagList, TagUpdate)


app_name = 'blog'

urlpatterns = [
    path('', TagList.as_view(), name='tag_list'),
    path('create/', TagCreate.as_view(), name='tag_create'),
    path('<slug:slug>/delete/', TagDelete.as_view(), name='tag_delete'),
    path('<slug:slug>/', TagDetail.as_view(), name='tag_detail'),
    path('<slug:slug>/update/', TagUpdate.as_view(), name='tag_update'),

]