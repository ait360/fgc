from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.urls import reverse_lazy, reverse
from taggit.managers import TaggableManager


class Tag(models.Model):
    name = models.CharField(max_length=31, unique=True)
    slug = models.SlugField(max_length=31, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tag_urls:tag_detail', kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse('tag_urls:tag_update', kwargs={'slug': self.slug})

    def get_delete_url(self):
        return reverse('tag_urls:tag_delete', kwargs={'slug': self.slug})

    def get_create_url(self):
        return reverse('tag_urls:tag_create')


def post_title_directory_path(instance, filename):
    return 'post_title_{0}/{1}'.format(instance.slug, filename)


class Post(models.Model):
    title = models.CharField(max_length=200)
    post_title_picture = models.ImageField(upload_to=post_title_directory_path, blank=True)
    slug = models.SlugField(max_length=200, unique_for_month='pub_date')
    body = RichTextUploadingField()

    pub_date = models.DateField(_('date published'), auto_now_add=True)
    modified_date = models.DateField(_('date modified'),
                                     auto_now=True)
    authors = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='blog_posts')
    #tags = models.ManyToManyField(Tag, related_name='blog_posts')
    taggit = TaggableManager()


    class Meta:
        verbose_name = 'blog post'
        ordering = ['-pub_date', 'title']
        get_latest_by = 'pub_date'
        permissions = (('view_future_post', 'Can view unplished Post'),)
        index_together = ('slug', 'pub_date')



    def __str__(self):
        return "{} first published {}".format(
            self.title,
            self.pub_date.strftime('%d-%m-%Y')
        )

    def get_archive_year_url(self):
        pass

    def get_update_url(self):
        return reverse('blog_post_urls:blog_post_update',
                                        kwargs={'month': self.pub_date.month,
                                                'year': self.pub_date.year,
                                                'slug': self.slug})

    def get_absolute_url(self):
        return reverse('blog_post_urls:blog_post_detail',
                                        kwargs={'month': self.pub_date.month,
                                                'year': self.pub_date.year,
                                                'slug': self.slug})

    def get_delete_url(self):
        return reverse('blog_post_urls:blog_post_delete',
                                        kwargs={'month': self.pub_date.month,
                                                'year': self.pub_date.year,
                                                'slug': self.slug})

    def get_create_url(self):
        return reverse('blog_post_urls:blog_post_create')
