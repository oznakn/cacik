from django.db.models import Count, Max, Q
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import lazy
from django.utils.translation import ugettext as _
from django.views.generic import ListView

from judge.comments import CommentedDetailView
from judge.models import BlogPost, Comment, Contest, Language, Problem, ProblemClarification, Profile, Submission, \
    Ticket
from judge.utils.cachedict import CacheDict
from judge.utils.diggpaginator import DiggPaginator
from judge.utils.problems import user_completed_ids
from judge.utils.tickets import filter_visible_tickets
from judge.utils.views import TitleMixin

from preferences import preferences

class PostList(ListView):
    model = BlogPost
    paginate_by = 10
    context_object_name = 'posts'
    template_name = 'blog/list.html'
    title = None

    def get_paginator(self, queryset, per_page, orphans=0,
                      allow_empty_first_page=True, **kwargs):
        return DiggPaginator(queryset, per_page, body=6, padding=2,
                             orphans=orphans, allow_empty_first_page=allow_empty_first_page, **kwargs)

    def get_queryset(self):
        return (BlogPost.objects.filter(visible=True, publish_on__lte=timezone.now()).order_by('-sticky', '-publish_on')
                .prefetch_related('authors__user'))

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data(**kwargs)
        context['title'] = self.title or _('Page %d of Posts') % context['page_obj'].number
        context['first_page_href'] = reverse('home')
        context['page_prefix'] = reverse('blog_post_list')
        context['comments'] = Comment.most_recent(self.request.user, 10)
        context['new_problems'] = Problem.objects.filter(is_public=True) \
                                         .order_by('-date', '-id')[:7]
        context['page_titles'] = CacheDict(lambda page: Comment.get_page_title(page))

        context['has_clarifications'] = False
        if self.request.user.is_authenticated:
            participation = self.request.profile.current_contest
            if participation:
                clarifications = ProblemClarification.objects.filter(problem__in=participation.contest.problems.all())
                context['has_clarifications'] = clarifications.count() > 0
                context['clarifications'] = clarifications.order_by('-date')

        context['user_count'] = lazy(Profile.objects.count, int, int)
        context['problem_count'] = lazy(Problem.objects.filter(is_public=True).count, int, int)
        context['submission_count'] = lazy(Submission.objects.count, int, int)
        context['language_count'] = lazy(Language.objects.count, int, int)

        context['post_comment_counts'] = {
            int(page[2:]): count for page, count in
            Comment.objects
                   .filter(page__in=['b:%d' % post.id for post in context['posts']], hidden=False)
                   .values_list('page').annotate(count=Count('page')).order_by()
        }

        now = timezone.now()

        # Dashboard stuff
        if self.request.user.is_authenticated:
            user = self.request.profile
            context['recently_attempted_problems'] = (Submission.objects.filter(user=user)
                                                      .exclude(problem__in=user_completed_ids(user))
                                                      .values_list('problem__code', 'problem__name', 'problem__points')
                                                      .annotate(points=Max('points'), latest=Max('date'))
                                                      .order_by('-latest'))[:7]

        visible_contests = Contest.objects.filter(is_visible=True).order_by('start_time')
        q = Q(is_private=False)
        if self.request.user.is_authenticated:
            q |= Q(is_private=True, private_contestants=user)
        visible_contests = visible_contests.filter(q)
        context['past_contests'] = visible_contests.filter(end_time__lt=now).order_by('-start_time')
        context['current_contests'] = visible_contests.filter(start_time__lte=now, end_time__gt=now)
        context['future_contests'] = visible_contests.filter(start_time__gte=now)

        if self.request.user.is_authenticated:
            profile = self.request.profile
            context['own_open_tickets'] = (Ticket.objects.filter(user=profile, is_open=True).order_by('-id')
                                           .prefetch_related('linked_item').select_related('user__user'))
        else:
            profile = None
            context['own_open_tickets'] = []

        # Superusers better be staffs, not the spell-casting kind either.
        if self.request.user.is_staff:
            tickets = (Ticket.objects.order_by('-id').filter(is_open=True).prefetch_related('linked_item')
                             .select_related('user__user'))
            context['open_tickets'] = filter_visible_tickets(tickets, self.request.user, profile)[:10]
        else:
            context['open_tickets'] = []
        return context

    def get(self, request, *args, **kwargs):
        if preferences.SitePreferences.active_contest:
            return HttpResponseRedirect(reverse('contest_view', args=(preferences.SitePreferences.active_contest.key,)))

        return super(PostList, self).get(request, *args, **kwargs)


class PostView(TitleMixin, CommentedDetailView):
    model = BlogPost
    pk_url_kwarg = 'id'
    context_object_name = 'post'
    template_name = 'blog/content.html'

    def get_title(self):
        return self.object.title

    def get_comment_page(self):
        return 'b:%s' % self.object.id

    def get_context_data(self, **kwargs):
        context = super(PostView, self).get_context_data(**kwargs)
        context['og_image'] = self.object.og_image
        return context

    def get_object(self, queryset=None):
        post = super(PostView, self).get_object(queryset)
        if not post.can_see(self.request.user):
            raise Http404()
        return post
