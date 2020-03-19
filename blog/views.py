from django.views.generic import (View, DetailView, CreateView, UpdateView, DeleteView,
                                  ListView, ArchiveIndexView, MonthArchiveView,
                                  YearArchiveView)
from django.urls import reverse_lazy



from .models import Tag, Post
from .forms import TagForm, PostForm
from .utils import (PageLinksMixin, AllowFuturePermissionMixin, DateObjectMixin,
                    PostFormValidMixin, TagUpdateMixin, TagCreateMixin, PageLinksMixin2,
                    GetPreviousUrl)


class TagCreate(TagCreateMixin, View):
    form_class = TagForm
    model = Tag
    template_name = 'blog/tag_form.html'
    redirect_url_namespace = 'tag_urls'



class TagDelete(DeleteView):
    model = Tag
    success_url = reverse_lazy('tag_urls:tag_list')
    context_object_name = 'tag'
    template_name = 'blog/tag_confirm_delete.html'


class TagDetail(DetailView):
    model = Tag
    slug_url_kwarg = 'slug'
    context_object_name = 'tag'
    template_name = 'blog/tag_detail.html'



class TagList(PageLinksMixin, ListView):
    model = Tag
    paginate_by = 5


class TagUpdate(TagUpdateMixin, View):
    model = Tag
    form_class = TagForm
    template_name = 'blog/tag_form_update.html'
    redirect_url_namespace = 'tag_urls'
    context_object_name = 'tag'

    #def get_object(self, queryset=None):
        #slug = self.model.objects.filter(slug=)



class PostArchiveMonth(
    AllowFuturePermissionMixin,
    MonthArchiveView):
    model = Post
    date_field = 'pub_date'
    month_format = '%m'


class PostArchiveYear(
    AllowFuturePermissionMixin,
    YearArchiveView):
    model = Post
    date_field = 'pub_date'
    make_object_list = True


#@require_authenticated_permission(
#    'blog.add_post')
class PostCreate(PostFormValidMixin, CreateView):
    form_class = PostForm
    model = Post
    context_object_name = 'post'
    template_name = 'blog/post_form.html'


#@require_authenticated_permission(
#    'blog.delete_post')
class PostDelete(GetPreviousUrl,DateObjectMixin, DeleteView):
    date_field = 'pub_date'
    model = Post
    success_url = reverse_lazy('blog_post_urls:blog_post_list')
    context_object_name = 'post'
    template_name = 'blog/post_confirm_delete.html'


class PostDetail(DateObjectMixin, DetailView):
    date_field = 'pub_date'
    model = Post
    #queryset = (
    #    Post.objects
    #        .select_related('authors__profile')
    #        .prefetch_related('tags')
    #)
    context_object_name = 'post'
    template_name = 'blog/post_detail.html'

class PostList(PageLinksMixin2,
    AllowFuturePermissionMixin,
    ArchiveIndexView):
    allow_empty = True
    context_object_name = 'post_list'
    date_field = 'pub_date'
    make_object_list = True
    model = Post
    paginate_by = 1
    template_name = 'blog/post_list.html'
    order_by = '-pub_date'


#@require_authenticated_permission(
#    'blog.change_post')
class PostUpdate(GetPreviousUrl,PostFormValidMixin,
                 DateObjectMixin, UpdateView):
    date_field = 'pub_date'
    form_class = PostForm
    model = Post
    template_name = 'blog/post_form_update.html'
    context_object_name = 'post'




