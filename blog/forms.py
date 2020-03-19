from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from ckeditor.widgets import CKEditorWidget
from django.utils.text import slugify


from .models import Tag, Post



class SlugCleanMixin:
    """Mixin class for slug cleaning method."""

    def clean_slug(self):

        new_slug = (
            self.cleaned_data['slug'].lower())
        disallowed = ['create', 'post', 'tag']
        if new_slug in disallowed:
            notice = 'Slug may not be "{}"'.format(new_slug)
            raise ValidationError(notice)
        return new_slug


class TagForm(SlugCleanMixin, forms.ModelForm):

    class Meta:
        model = Tag
        fields = ['name']

    def clean_name(self):
        return self.cleaned_data['name'].lower()

    def save(self, **kwargs):
        tag = super().save(commit=False)

        tag.slug = slugify(tag.name)
        tag.save()
        self.save_m2m()








class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ['authors', 'slug']
        widgets = {
            'body': CKEditorUploadingWidget()
        }

    def clean_slug(self):
        return self.cleaned_data['slug'].lower()

    def save(self, request, commit=True):
        post = super().save(commit=False)
        if not post.pk:
            # = get_user(request)  # add the author object to the post
            post.slug = slugify(post.title)
        if commit:
            post.save()             # save the post object
            post.authors.add(get_user(request))
            self.save_m2m()         # save all database dependency

        return post
