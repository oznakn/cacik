from django.contrib import admin
from django.forms import ModelForm
from django.utils.html import format_html
from django.utils.translation import gettext, gettext_lazy as _, ungettext

from django_ace import AceWidget
from judge.models import Profile
from judge.widgets import AdminPagedownWidget, AdminSelect2Widget


class ProfileForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['current_contest'].queryset = self.instance.contest_history.select_related('contest') \
            .only('contest__name', 'user_id', 'virtual')
        self.fields['current_contest'].label_from_instance = \
            lambda obj: '%s v%d' % (obj.contest.name, obj.virtual) if obj.virtual else obj.contest.name

    class Meta:
        widgets = {
            'timezone': AdminSelect2Widget,
            'language': AdminSelect2Widget,
            'current_contest': AdminSelect2Widget,
        }
        if AdminPagedownWidget is not None:
            widgets['about'] = AdminPagedownWidget


class TimezoneFilter(admin.SimpleListFilter):
    title = _('timezone')
    parameter_name = 'timezone'

    def lookups(self, request, model_admin):
        return Profile.objects.values_list('timezone', 'timezone').distinct().order_by('timezone')

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(timezone=self.value())


class ProfileAdmin(admin.ModelAdmin):
    fields = ('user', 'display_name', 'display_rank', 'about', 'timezone', 'language',
              'last_access', 'ip', 'mute', 'is_unlisted', 'is_totp_enabled',
              'current_contest', 'notes')
    readonly_fields = ('user',)
    list_display = ('admin_user_admin', 'email', 'is_totp_enabled', 'timezone_full',
                    'date_joined', 'last_access', 'ip', 'show_public')
    ordering = ('user__username',)
    search_fields = ('user__username', 'ip', 'user__email')
    list_filter = ('language', TimezoneFilter)
    actions = ('recalculate_points',)
    actions_on_top = True
    actions_on_bottom = True
    form = ProfileForm

    def get_queryset(self, request):
        return super(ProfileAdmin, self).get_queryset(request).select_related('user')

    def get_fields(self, request, obj=None):
        if request.user.has_perm('judge.totp'):
            fields = list(self.fields)
            fields.insert(fields.index('is_totp_enabled') + 1, 'totp_key')
            return tuple(fields)
        else:
            return self.fields

    def get_readonly_fields(self, request, obj=None):
        fields = self.readonly_fields
        if not request.user.has_perm('judge.totp'):
            fields += ('is_totp_enabled',)
        return fields

    def show_public(self, obj):
        return format_html('{0}', obj.display_name)
    show_public.short_description = ''

    def admin_user_admin(self, obj):
        return obj.username
    admin_user_admin.admin_order_field = 'user__username'
    admin_user_admin.short_description = _('User')

    def email(self, obj):
        return obj.user.email
    email.admin_order_field = 'user__email'
    email.short_description = _('Email')

    def timezone_full(self, obj):
        return obj.timezone
    timezone_full.admin_order_field = 'timezone'
    timezone_full.short_description = _('Timezone')

    def date_joined(self, obj):
        return obj.user.date_joined
    date_joined.admin_order_field = 'user__date_joined'
    date_joined.short_description = _('date joined')

    def recalculate_points(self, request, queryset):
        count = 0
        for profile in queryset:
            profile.calculate_points()
            count += 1
        self.message_user(request, ungettext('%d user have scores recalculated.',
                                             '%d users have scores recalculated.',
                                             count) % count)
    recalculate_points.short_description = _('Recalculate scores')
