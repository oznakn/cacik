"""
Django settings for dmoj project.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

from django.utils.translation import ugettext_lazy as _
from django_jinja.builtins import DEFAULT_EXTENSIONS
from jinja2 import select_autoescape

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '5*9f5q57mqmlz2#f$x1h76&jxy#yortjl1v+l*6hd18$d*yx#0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

SITE_ID = 1

PYGMENT_THEME = 'pygment-github.css'
ACE_THEME = 'chrome'


WPADMIN = {
    'admin': {
        'title': 'DMOJ Admin',
        'menu': {
            'top': 'wpadmin.menu.menus.BasicTopMenu',
            'left': 'wpadmin.menu.custom.CustomModelLeftMenuWithDashboard',
        },
        'custom_menu': [
            {
                'model': 'judge.Problem',
                'icon': 'fa-question-circle',
                'children': [
                    'judge.ProblemGroup',
                    'judge.ProblemType',
                ],
            },
            {
                'model': 'judge.Submission',
                'icon': 'fa-check-square-o',
                'children': [
                    'judge.Language',
                    'judge.Judge',
                ],
            },
            {
                'model': 'judge.Contest',
                'icon': 'fa-bar-chart',
                'children': [
                    'judge.ContestParticipation',
                    'judge.ContestTag',
                ],
            },
            {
                'model': 'auth.User',
                'icon': 'fa-user',
                'children': [
                    'auth.Group',
                    'registration.RegistrationProfile',
                ],
            },
            {
                'model': 'judge.Profile',
                'icon': 'fa-user-plus',
                'children': [
                ],
            },
            {
                'model': 'judge.NavigationBar',
                'icon': 'fa-bars',
                'children': [
                    'judge.License',
                    'sites.Site',
                    'redirects.Redirect',
                ],
            },
            ('judge.BlogPost', 'fa-rss-square'),
            ('judge.Comment', 'fa-comment-o'),
            ('flatpages.FlatPage', 'fa-file-text-o'),
            ('judge.SitePreferences', 'fa-file-text-o'),
            ('judge.Solution', 'fa-pencil'),
        ],
        'dashboard': {
            'breadcrumbs': True,
        },
    },
}

INSTALLED_APPS = (
    'wpadmin',
    'django.contrib.admin',
    'judge',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.flatpages',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.redirects',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'registration',
    'mptt',
    'django_social_share',
    'social_django',
    'compressor',
    'sass_processor',
    'django_ace',
    'pagedown',
    'statici18n',
    'impersonate',
    'django_jinja',
    'preferences',
)

MIDDLEWARE = (
    'judge.middleware.ShortCircuitMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'judge.middleware.DMOJLoginMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'judge.user_log.LogUserAccessMiddleware',
    'judge.timezone.TimezoneMiddleware',
    'impersonate.middleware.ImpersonateMiddleware',
    'judge.middleware.DMOJImpersonationMiddleware',
    'judge.middleware.ContestMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'judge.social_auth.SocialAuthExceptionMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
)

IMPERSONATE_REQUIRE_SUPERUSER = True
IMPERSONATE_DISABLE_LOGGING = True

ACCOUNT_ACTIVATION_DAYS = 7

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

SILENCED_SYSTEM_CHECKS = ['urls.W002', 'fields.W342']

ROOT_URLCONF = 'dmoj.urls'
LOGIN_REDIRECT_URL = '/'
WSGI_APPLICATION = 'dmoj.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django_jinja.backend.Jinja2',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': False,
        'OPTIONS': {
            'match_extension': ('.html', '.txt'),
            'match_regex': '^(?!admin/)',
            'context_processors': [
                'django.template.context_processors.media',
                'django.template.context_processors.tz',
                'django.template.context_processors.i18n',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'judge.template_context.comet_location',
                'judge.template_context.get_resource',
                'judge.template_context.general_info',
                'judge.template_context.site',
                'judge.template_context.event_config',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'preferences.context_processors.preferences_cp',
            ],
            'autoescape': select_autoescape(['html', 'xml']),
            'trim_blocks': True,
            'lstrip_blocks': True,
            'extensions': DEFAULT_EXTENSIONS + [
                'compressor.contrib.jinja2ext.CompressorExtension',
                'judge.jinja2.DMOJExtension',
                'judge.jinja2.spaceless.SpacelessExtension',
            ],
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.media',
                'django.template.context_processors.tz',
                'django.template.context_processors.i18n',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

LANGUAGES = [
    ('de', _('German')),
    ('en', _('English')),
    ('es', _('Spanish')),
    ('fr', _('French')),
    ('hr', _('Croatian')),
    ('hu', _('Hungarian')),
    ('ko', _('Korean')),
    ('ro', _('Romanian')),
    ('ru', _('Russian')),
    ('sr-latn', _('Serbian (Latin)')),
    ('tr', _('Turkish')),
    ('vi', _('Vietnamese')),
    ('zh-hans', _('Simplified Chinese')),
]

MARKDOWN_ADMIN_EDITABLE_STYLE = {
    'safe_mode': False,
    'math': True,
}

MARKDOWN_DEFAULT_STYLE = {
    'safe_mode': True,
    'nofollow': True,
    'math': True,
}

MARKDOWN_USER_LARGE_STYLE = {
    'safe_mode': True,
    'nofollow': True,
    'math': True,
}

MARKDOWN_STYLES = {
    'comment': MARKDOWN_DEFAULT_STYLE,
    'self-description': MARKDOWN_USER_LARGE_STYLE,
    'problem': MARKDOWN_ADMIN_EDITABLE_STYLE,
    'contest': MARKDOWN_ADMIN_EDITABLE_STYLE,
    'language': MARKDOWN_ADMIN_EDITABLE_STYLE,
    'license': MARKDOWN_ADMIN_EDITABLE_STYLE,
    'judge': MARKDOWN_ADMIN_EDITABLE_STYLE,
    'blog': MARKDOWN_ADMIN_EDITABLE_STYLE,
    'solution': MARKDOWN_ADMIN_EDITABLE_STYLE,
    'contest_tag': MARKDOWN_ADMIN_EDITABLE_STYLE,
    'ticket': MARKDOWN_USER_LARGE_STYLE,
}

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dmoj',
        'USER': 'root',
        'PASSWORD': 'pass',
        'HOST': '127.0.0.1',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'sql_mode': 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION',
        },
    },
}

# Bridged configuration
BRIDGED_JUDGE_ADDRESS = [('localhost', 9999)]
BRIDGED_DJANGO_ADDRESS = [('localhost', 9998)]
BRIDGED_DJANGO_CONNECT = None

# Event Server configuration
EVENT_DAEMON_USE = False
EVENT_DAEMON_POST = 'ws://localhost:9997/'
EVENT_DAEMON_GET = 'ws://localhost:9996/'
EVENT_DAEMON_POLL = '/channels/'
EVENT_DAEMON_KEY = None
EVENT_DAEMON_SUBMISSION_KEY = '6Sdmkx^%pk@GsifDfXcwX*Y7LRF%RGT8vmFpSxFBT$fwS7trc8raWfN#CSfQuKApx&$B#Gh2L7p%W!Ww'

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

# Whatever you do, this better be one of the entries in `LANGUAGES`.
LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
DEFAULT_USER_TIME_ZONE = 'America/Toronto'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Cookies
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

DMOJ_RESOURCES = os.path.join(BASE_DIR, 'resources')
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
    'sass_processor.finders.CssFinder',
)
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'resources'),
]
STATIC_URL = '/static/'

# Django compressor settings
COMPRESS_OUTPUT_DIR = 'cache'
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter',
]
COMPRESS_JS_FILTERS = ['compressor.filters.jsmin.JSMinFilter']
COMPRESS_STORAGE = 'compressor.storage.GzipCompressorFileStorage'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Define a cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Authentication
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'judge.social_auth.GitHubSecureEmailOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'judge.social_auth.verify_email',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'judge.social_auth.choose_username',
    'social_core.pipeline.user.create_user',
    'judge.social_auth.make_profile',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

SOCIAL_AUTH_GITHUB_SECURE_SCOPE = ['user:email']
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_SLUGIFY_USERNAMES = True
SOCIAL_AUTH_SLUGIFY_FUNCTION = 'judge.social_auth.slugify_username'

MOSS_API_KEY = None

CELERY_WORKER_HIJACK_ROOT_LOGGER = False

PROBLEM_PDF_CACHE = os.path.join(BASE_DIR, 'static')
DMOJ_PDF_PROBLEM_CACHE = PROBLEM_PDF_CACHE

# Path to a PhantomJS executable.
PHANTOMJS = '/usr/bin/phantomjs'

try:
    with open(os.path.join(os.path.dirname(__file__), 'local_settings.py')) as f:
        exec(f.read(), globals())
except IOError:
    pass
