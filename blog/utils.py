from django.shortcuts import get_object_or_404
from django.http import (
    Http404, HttpResponseRedirect)
from django.views.generic.dates import (
    DateMixin, MonthMixin as BaseMonthMixin,
    YearMixin as BaseYearMixin, _date_from_string)
from .models import Tag
from django.forms.models import model_to_dict
from django.shortcuts import render, redirect
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.messages import success, error
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy






class PageLinksMixin:
    page_kwarg = 'page'

    def _page_urls(self, page_number):
        return "?{pkw}={n}".format(
            pkw=self.page_kwarg,
            n=page_number)

    def first_page(self, page):
        # don't show on first page
        if page.number > 1:
            return self._page_urls(1)
        return None

    def previous_page(self, page):
        if (page.has_previous()
                and page.number > 2):
            return self._page_urls(
                page.previous_page_number())
        return None

    def next_page(self, page):
        last_page = page.paginator.num_pages
        if (page.has_next()
                and page.number < last_page - 1):
            return self._page_urls(
                page.next_page_number())
        return None

    def last_page(self, page):
        last_page = page.paginator.num_pages
        if page.number < last_page:
            return self._page_urls(last_page)
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(
            **kwargs)
        page = context.get('page_obj')
        if page is not None:
            context.update({
                'first_page_url':
                    self.first_page(page),
                'previous_page_url':
                    self.previous_page(page),
                'next_page_url':
                    self.next_page(page),
                'last_page_url':
                    self.last_page(page),
            })
        return context



class AllowFuturePermissionMixin():

    def get_allow_future(self):
        return self.request.user.has_perm(
            'blog.view_future_post')


class MonthMixin(BaseMonthMixin):
    month_format = '%m'
    month_query_kwarg = 'month'
    month_url_kwarg = 'month'

    def get_month(self):
        month = self.month
        if month is None:
            month = self.kwargs.get(
                self.month_url_kwarg,
                self.request.GET.get(
                    self.month_query_kwarg))
        if month is None:
            raise Http404("No month specified")
        return month


class YearMixin(BaseYearMixin):
    year_query_kwarg = 'year'
    year_url_kwarg = 'year'

    def get_year(self):
        year = self.year
        if year is None:
            year = self.kwargs.get(
                self.year_url_kwarg,
                self.request.GET.get(
                    self.year_query_kwarg))
        if year is None:
            raise Http404("No year specified")
        return year


class DateObjectMixin(
        AllowFuturePermissionMixin,
        YearMixin, MonthMixin, DateMixin):

    def get_object(self, queryset=None):
        year = self.get_year()
        month = self.get_month()
        date = _date_from_string(
            year, self.get_year_format(),
            month, self.get_month_format(),
        )
        if queryset is None:
            queryset = self.get_queryset()
        if (not self.get_allow_future()
                and date > date.today()):
            raise Http404(
                "Future {} not available because "
                "{}.allow_future is False."
                .format(
                    (queryset.model
                     ._meta.verbose_name_plural),
                    self.__class__.__name__))
        filter_dict = (
            self._make_single_date_lookup(date))
        queryset = queryset.filter(**filter_dict)
        return super().get_object(
            queryset=queryset)

    def _make_single_date_lookup(self, date):
        date_field = self.get_date_field()
        if self.uses_datetime_field:
            since = self._make_date_lookup_arg(
                date)
            until = self._make_date_lookup_arg(
                self._get_next_month(date))
            return {
                '%s__gte' % date_field: since,
                '%s__lt' % date_field: until,
            }
        else:
            return {
                '%s__gte' % date_field: date,
                '%s__lt' % date_field:
                    self._get_next_month(date),
            }


class PostFormValidMixin:

    def form_valid(self, form):
        self.object = form.save(self.request)
        return HttpResponseRedirect(
            self.get_success_url())

#class TagFormMixin:

#    def post(self, request, *args, **kwargs):
#        self.object = Tag
#        return super().post(request, *args, **kwargs)


class TagCreateMixin:
    model = None
    form_class = None
    template_name = ''
    redirect_url_namespace = ''
    initial = {}
    context_object_name = None


    def get(self, request):
        tag_form = self.form_class()
        context = {'form': tag_form}

        return render(request, self.template_name, context)


    @method_decorator(csrf_protect)
    def post(self, request):

        if request.user.is_authenticated:
            tag_form = self.form_class(request.POST)

            if tag_form.is_valid():
                tag_form.save(request=request)
                success(request, _('Tag Created!!'))
                return redirect(self.get_success_url(request))
            else:
                context = {'form':tag_form}
                error(request, _('Please correct the error(s) below'))
                return render(request, self.template_name, context)

    def get_success_url(self, request):
        name = request.POST['name']
        self.success_url = reverse_lazy('{}:{}_detail'.format(
            self.redirect_url_namespace, self.model.__name__.lower()),
            kwargs={'slug':slugify(name)})
        return self.success_url


class TagUpdateMixin:
    model = None
    form_class = None
    template_name = ''
    redirect_url_namespace = ''
    initial = {}
    context_object_name = None


    def get(self, request, slug):
        tag = get_object_or_404(self.model, slug__iexact=slug)
        self.initial = model_to_dict(tag)

        tag_form = self.form_class(instance=tag, initial=self.initial)
        context = {'form': tag_form, self.context_object_name: tag}

        return render(request, self.template_name, context)


    @method_decorator(csrf_protect)
    def post(self, request, slug):
        tag = get_object_or_404(self.model, slug__iexact=slug)

        if request.user.is_authenticated:
            tag_form = self.form_class(request.POST,
                                       instance=tag, initial=self.initial)

            if tag_form.is_valid():
                tag_form.save(request=request)
                success(request, _('Updated!!'))
                return redirect(self.get_success_url(request))
            else:
                context = {'form':tag_form, self.context_object_name:tag}
                error(request, _('Please correct the error(s) below'))
                return render(request, self.template_name, context)

    def get_success_url(self, request):
        name = request.POST['name']
        self.success_url = reverse_lazy('{}:{}_detail'.format(
            self.redirect_url_namespace, self.model.__name__.lower()),
            kwargs={'slug':slugify(name)})
        return self.success_url


class PageLinksMixin2:
    page_kwargs = 'page'
    num_navigable_links = 5
    page_links = []
    has_previous_ellipsis = False
    has_next_ellipsis = False
    page_num_index = 2


    def _page_urls(self, page_number):
        return "?{pkw}={n}".format(pkw=self.page_kwargs,
                                   n=page_number)

    def _get_navigable_pages(self, page, num_more_pages_list, num_more_pages):
        self.page_links = []
        self.page_links = [(1,self._page_urls(1))]
        for num in num_more_pages_list:
            page_num = page.number + (num - self.page_num_index)
            #if page_num == page.number:
            #   page_num = '<b> ' + str(page_num) + '</b>'
            self.page_links.append((page_num, self._page_urls(page_num)))
        #print('page_links  ', self.page_links)
        return self.page_links


    def get_navigable_pages(self, page):
        last_page_num = page.paginator.num_pages
        page_list = list(range(1, self.num_navigable_links+1))
        #print('page list ', page_list)
        #print('number of pages ', page.paginator.num_pages)
        if last_page_num in page_list:
            self.page_links = []
            for page_num in range(1, last_page_num+1):
                #if page_num == page.number:
                #    page_num = '<b> ' + str(page_num) + '</b>'
                self.page_links.append((page_num , self._page_urls(page_num)))
            #print('page_links ', self.page_links)
            return [self.page_links, self.has_previous_ellipsis,
                    self.has_next_ellipsis]
        else:
            num_more_pages_list = list(range(1,
                                        self.num_navigable_links))

            num_more_pages = last_page_num - page.number
            #print('num_more_pages  ', num_more_pages)


            if page.number <= self.page_num_index+1:
                self.has_next_ellipsis = True
                self.page_links = []
                for page_num in range(1, self.num_navigable_links+ 1):
                    self.page_links.append((page_num, self._page_urls(page_num)))
                return [self.page_links, self.has_previous_ellipsis,
                        self.has_next_ellipsis]

            elif (last_page_num-page.number) >= 0 and (last_page_num-page.number) < (self.num_navigable_links- self.page_num_index): #((last_page_num - self.page_num_index+1)-2):
                self.page_links = []
                self.has_previous_ellipsis = True
                self.page_links = [(1, self._page_urls(1))]
                for num in range(1, self.num_navigable_links):
                    page_num = last_page_num - ((self.num_navigable_links-1)-num)
                    self.page_links.append((page_num, self._page_urls(page_num)))
                return [self.page_links, self.has_previous_ellipsis, self.has_next_ellipsis]





            #if num_more_pages  <= 3: #in num_more_pages_list:
            #    self.has_previous_ellipsis = True
            #    self
            #    return [self._get_navigable_pages(page, num_more_pages_list, num_more_pages),
            #           self.has_previous_ellipsis, self.has_next_ellipsis]


            else:
                #num_more_pages = self.num_navigable_links - (1 + self.num_navigable_links//2)
                self.has_previous_ellipsis = True
                self.has_next_ellipsis = True
                return [self._get_navigable_pages(page, num_more_pages_list, num_more_pages),
                       self.has_previous_ellipsis, self.has_next_ellipsis]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page = context.get('page_obj')
        #print('page ', page)
        if page is not None:
            context.update({'first_page_url': self.get_navigable_pages(page)[0][0][1],
                            'page_url_list': self.get_navigable_pages(page)[0][1:],
                            'has_previous_ellipsis': self.get_navigable_pages(page)[1],
                            'has_next_ellipsis': self.get_navigable_pages(page)[2]})

        return context



class GetPreviousUrl:


    def get(self, request, **kwargs):
        self.previous_url = request.META['HTTP_REFERER']
        print(self.previous_url)
        return super().get(request, **kwargs)


    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context.update({'previous_url': self.previous_url})

        return context

