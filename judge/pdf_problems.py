import errno
import io
import json
import logging
import os
import shutil
import subprocess
import tempfile
import uuid

from django.conf import settings
from django.utils.translation import gettext

HAS_PHANTOMJS = os.access(getattr(settings, 'PHANTOMJS', ''), os.X_OK)
HAS_SLIMERJS = os.access(getattr(settings, 'SLIMERJS', ''), os.X_OK)

NODE_PATH = getattr(settings, 'NODEJS', '/usr/bin/node')
PUPPETEER_MODULE = getattr(settings, 'PUPPETEER_MODULE', '/usr/lib/node_modules/puppeteer')
HAS_PUPPETEER = os.access(NODE_PATH, os.X_OK) and os.path.isdir(PUPPETEER_MODULE)

HAS_PDF = (os.path.isdir(getattr(settings, 'DMOJ_PDF_PROBLEM_CACHE', '')) and
           (HAS_PHANTOMJS or HAS_SLIMERJS or HAS_PUPPETEER))

EXIFTOOL = getattr(settings, 'EXIFTOOL', '/usr/bin/exiftool')
HAS_EXIFTOOL = os.access(EXIFTOOL, os.X_OK)

logger = logging.getLogger('judge.problem.pdf')


class BasePdfMaker(object):
    title = None

    def __init__(self, dir=None, clean_up=True):
        self.dir = dir or os.path.join(getattr(settings, 'DMOJ_PDF_PROBLEM_TEMP_DIR', tempfile.gettempdir()),
                                       str(uuid.uuid1()))
        self.proc = None
        self.log = None
        self.htmlfile = os.path.join(self.dir, 'input.html')
        self.pdffile = os.path.join(self.dir, 'output.pdf')
        self.clean_up = clean_up

    def load(self, file, source):
        with open(os.path.join(self.dir, file), 'w') as target, open(source) as source:
            target.write(source.read())

    def make(self, debug=False):
        self._make(debug)

        if self.title and HAS_EXIFTOOL:
            try:
                subprocess.check_output([EXIFTOOL, '-Title=%s' % (self.title,), self.pdffile])
            except subprocess.CalledProcessError as e:
                logger.error('Failed to run exiftool to set title for: %s\n%s', self.title, e.output)

    def _make(self, debug):
        raise NotImplementedError()

    @property
    def html(self):
        with io.open(self.htmlfile, encoding='utf-8') as f:
            return f.read()

    @html.setter
    def html(self, data):
        with io.open(self.htmlfile, 'w', encoding='utf-8') as f:
            f.write(data)

    @property
    def success(self):
        return self.proc.returncode == 0

    @property
    def created(self):
        return os.path.exists(self.pdffile)

    def __enter__(self):
        try:
            os.makedirs(self.dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.clean_up:
            shutil.rmtree(self.dir, ignore_errors=True)


class PhantomJSPdfMaker(BasePdfMaker):
    template = '''\
"use strict";
var page = require('webpage').create();
var param = {params};

page.paperSize = {
    format: param.paper, orientation: 'portrait', margin: '1cm',
    footer: {
        height: '1cm',
        contents: phantom.callback(function(num, pages) {
            return ('<center style="margin: 0 auto; font-family: Segoe UI; font-size: 10px">'
                  + param.footer.replace('[page]', num).replace('[topage]', pages) + '</center>');
        })
    }
};

page.onCallback = function (data) {
    if (data.action === 'snapshot') {
        page.render(param.output);
        phantom.exit();
    }
}

page.open(param.input, function (status) {
    if (status !== 'success') {
        console.log('Unable to load the address!');
        phantom.exit(1);
    } else {
        page.evaluate(function (zoom) {
            document.documentElement.style.zoom = zoom;
        }, param.zoom);
        window.setTimeout(function () {
            page.render(param.output);
            phantom.exit();
        }, param.timeout);
    }
});
'''

    def get_render_script(self):
        return self.template.replace('{params}', json.dumps({
            'zoom': getattr(settings, 'PHANTOMJS_PDF_ZOOM', 0.75),
            'timeout': int(getattr(settings, 'PHANTOMJS_PDF_TIMEOUT', 5.0) * 1000),
            'input': 'input.html', 'output': 'output.pdf',
            'paper': getattr(settings, 'PHANTOMJS_PAPER_SIZE', 'Letter'),
            'footer': gettext('Page [page] of [topage]'),
        }))

    def _make(self, debug):
        with io.open(os.path.join(self.dir, '_render.js'), 'w', encoding='utf-8') as f:
            f.write(self.get_render_script())
        cmdline = [settings.PHANTOMJS, '_render.js']
        self.proc = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.dir)
        self.log = self.proc.communicate()[0]

if HAS_PHANTOMJS:
    DefaultPdfMaker = PhantomJSPdfMaker
else:
    DefaultPdfMaker = None
