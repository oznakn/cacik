import itertools
from collections import OrderedDict
from operator import attrgetter

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from reversion import revisions
from reversion.models import Version

from judge.models.choices import TIMEZONE, ACE_THEMES, MATH_ENGINES_CHOICES, EFFECTIVE_MATH_ENGINES
from judge.models.contest import Contest, ContestTag, ContestParticipation, ContestProblem, ContestSubmission, Rating
from judge.models.interface import MiscConfig, validate_regex, NavigationBar, BlogPost, Solution
from judge.models.problem import ProblemGroup, ProblemType, Problem, ProblemTranslation, TranslatedProblemQuerySet, \
    TranslatedProblemForeignKeyQuerySet, License, LanguageLimit
from judge.models.problem_data import problem_data_storage, problem_directory_file, ProblemData, ProblemTestCase, \
    CHECKERS
from judge.models.profile import Profile, Organization, OrganizationRequest
from judge.models.runtimes import Language, RuntimeVersion
from judge.models.submission import SUBMISSION_RESULT, Submission, SubmissionTestCase


class Comment(MPTTModel):
    author = models.ForeignKey(Profile, verbose_name=_('commenter'))
    time = models.DateTimeField(verbose_name=_('posted time'), auto_now_add=True)
    page = models.CharField(max_length=30, verbose_name=_('associated Page'), db_index=True,
                            validators=[RegexValidator('^[pc]:[a-z0-9]+$|^b:\d+$|^s:',
                                                       _('Page code must be ^[pc]:[a-z0-9]+$|^b:\d+$'))])
    score = models.IntegerField(verbose_name=_('votes'), default=0)
    title = models.CharField(max_length=200, verbose_name=_('title of comment'))
    body = models.TextField(verbose_name=_('body of comment'))
    hidden = models.BooleanField(verbose_name=_('hide the comment'), default=0)
    parent = TreeForeignKey('self', verbose_name=_('parent'), null=True, blank=True, related_name='replies')
    versions = GenericRelation(Version, object_id_field='object_id_int')

    class Meta:
        verbose_name = _('comment')
        verbose_name_plural = _('comments')

    class MPTTMeta:
        order_insertion_by = ['-time']

    @classmethod
    def most_recent(cls, user, n, batch=None):
        queryset = cls.objects.filter(hidden=False).select_related('author__user') \
            .defer('author__about', 'body').order_by('-id')
        if user.is_superuser:
            return queryset[:n]
        if batch is None:
            batch = 2 * n
        output = []
        for i in itertools.count(0):
            slice = queryset[i * batch:i * batch + batch]
            if not slice:
                break
            for comment in slice:
                if comment.page.startswith('p:'):
                    if Problem.objects.get(code=comment.page[2:]).is_accessible_by(user):
                        output.append(comment)
                else:
                    output.append(comment)
                if len(output) >= n:
                    return output
        return output

    @cached_property
    def link(self):
        link = None
        if self.page.startswith('p:'):
            link = reverse('problem_detail', args=(self.page[2:],))
        elif self.page.startswith('c:'):
            link = reverse('contest_view', args=(self.page[2:],))
        elif self.page.startswith('b:'):
            key = 'blog_slug:%s' % self.page[2:]
            slug = cache.get(key)
            if slug is None:
                try:
                    slug = BlogPost.objects.get(id=self.page[2:]).slug
                except ObjectDoesNotExist:
                    slug = ''
                cache.set(key, slug, 3600)
            link = reverse('blog_post', args=(self.page[2:], slug))
        elif self.page.startswith('s:'):
            link = reverse('solution', args=(self.page[2:],))
        return link

    @cached_property
    def page_title(self):
        try:
            if self.page.startswith('p:'):
                return Problem.objects.get(code=self.page[2:]).name
            elif self.page.startswith('c:'):
                return Contest.objects.get(key=self.page[2:]).name
            elif self.page.startswith('b:'):
                return BlogPost.objects.get(id=self.page[2:]).title
            elif self.page.startswith('s:'):
                return Solution.objects.get(url=self.page[2:]).title
            return '<unknown>'
        except ObjectDoesNotExist:
            return '<deleted>'

    def get_absolute_url(self):
        return '%s#comment-%d' % (self.link, self.id)

    def __unicode__(self):
        return self.title

        # Only use this when queried with
        # .prefetch_related(Prefetch('votes', queryset=CommentVote.objects.filter(voter_id=profile_id)))
        # It's rather stupid to put a query specific property on the model, but the alternative requires
        # digging Django internals, and could not be guaranteed to work forever.
        # Hence it is left here for when the alternative breaks.
        # @property
        # def vote_score(self):
        #    queryset = self.votes.all()
        #    if not queryset:
        #        return 0
        #    return queryset[0].score


class CommentVote(models.Model):
    voter = models.ForeignKey(Profile, related_name='voted_comments')
    comment = models.ForeignKey(Comment, related_name='votes')
    score = models.IntegerField()

    class Meta:
        unique_together = ['voter', 'comment']
        verbose_name = _('comment vote')
        verbose_name_plural = _('comment votes')


class Judge(models.Model):
    name = models.CharField(max_length=50, help_text=_('Server name, hostname-style'), unique=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('time of creation'))
    auth_key = models.CharField(max_length=100, help_text=_('A key to authenticated this judge'),
                                verbose_name=_('authentication key'))
    online = models.BooleanField(verbose_name=_('judge online status'), default=False)
    start_time = models.DateTimeField(verbose_name=_('judge start time'), null=True)
    ping = models.FloatField(verbose_name=_('response time'), null=True)
    load = models.FloatField(verbose_name=_('system load'), null=True,
                             help_text=_('Load for the last minute, divided by processors to be fair.'))
    description = models.TextField(blank=True, verbose_name=_('description'))
    last_ip = models.GenericIPAddressField(verbose_name='Last connected IP', blank=True, null=True)
    problems = models.ManyToManyField(Problem, verbose_name=_('problems'), related_name='judges')
    runtimes = models.ManyToManyField(Language, verbose_name=_('judges'), related_name='judges')

    def __unicode__(self):
        return self.name

    @cached_property
    def runtime_versions(self):
        qs = (self.runtimeversion_set.values('language__key', 'language__name', 'version', 'name')
              .order_by('language__key', 'priority'))

        ret = OrderedDict()

        for data in qs:
            key = data['language__key']
            if key not in ret:
                ret[key] = {'name': data['language__name'], 'runtime': []}
            ret[key]['runtime'].append((data['name'], (data['version'],)))

        return ret.items()

    @cached_property
    def uptime(self):
        return timezone.now() - self.start_time if self.online else 'N/A'

    @cached_property
    def ping_ms(self):
        return self.ping * 1000

    @cached_property
    def runtime_list(self):
        return map(attrgetter('name'), self.runtimes.all())

    class Meta:
        ordering = ['name']
        verbose_name = _('judge')
        verbose_name_plural = _('judges')


class PrivateMessage(models.Model):
    title = models.CharField(verbose_name=_('message title'), max_length=50)
    content = models.TextField(verbose_name=_('message body'))
    sender = models.ForeignKey(Profile, verbose_name=_('sender'), related_name='sent_messages')
    target = models.ForeignKey(Profile, verbose_name=_('target'), related_name='received_messages')
    timestamp = models.DateTimeField(verbose_name=_('message timestamp'), auto_now_add=True)
    read = models.BooleanField(verbose_name=_('read'), default=False)


class PrivateMessageThread(models.Model):
    messages = models.ManyToManyField(PrivateMessage, verbose_name=_('messages in the thread'))


revisions.register(Profile, exclude=['points', 'last_access', 'ip', 'rating'])
revisions.register(Problem, follow=['language_limits'])
revisions.register(LanguageLimit)
revisions.register(Contest, follow=['contest_problems'])
revisions.register(ContestProblem)
revisions.register(Organization)
revisions.register(BlogPost)
revisions.register(Solution)
revisions.register(Judge, fields=['name', 'created', 'auth_key', 'description'])
revisions.register(Language)
revisions.register(Comment, fields=['author', 'time', 'page', 'score', 'title', 'body', 'hidden', 'parent'])
