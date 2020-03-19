from django.urls import re_path, path


from ..views import (PostDetail, PostDelete, PostUpdate, PostCreate,
                     PostArchiveMonth, PostArchiveYear, PostList)


app_name = 'blog'

urlpatterns = [

    path('', PostList.as_view(), name='blog_post_list'),
    path('create/', PostCreate.as_view(), name='blog_post_create'),
    path('<int:year>/', PostArchiveYear.as_view(), name='blog_post_archive_year'),
    path('<int:year>/<int:month>/', PostArchiveMonth.as_view(),
                                                  name='blog_post_archive_month'),
    path('<int:month>/<int:year>/<slug:slug>/', PostDetail.as_view(),
                                                  name='blog_post_detail'),
    path('<int:month>/<int:year>/<slug:slug>/delete/', PostDelete.as_view(),
                                                  name='blog_post_delete'),
    path('<int:month>/<int:year>/<slug:slug>/update/', PostUpdate.as_view(),
                                                  name='blog_post_update'),

]