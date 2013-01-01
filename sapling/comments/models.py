from django.db import models
from django.db.utils import IntegrityError
from django.utils.translation import ugettext as _

from versionutils import versioning

from ckeditor.models import HTML5FragmentField
from pages.models import Page

allowed_tags = ['p', 'br', 'a', 'em', 'strong', 'u', 'ul', 'ol', 'li', 'pre',
                'table', 'thead', 'tbody', 'tr', 'th', 'td', 'strike', 'sub',
                'sup', 'tt']
allowed_attributes_map = {'a': ['name', 'href'],
                          'th': ['colspan', 'rowspan'],
                          'td': ['colspan', 'rowspan']}
allowed_styles_map = {}
rename_elements = {'b': 'strong', 'i': 'em', 's': 'strike'}


class Comment(models.Model):
    page = models.ForeignKey(Page)
    content = HTML5FragmentField(allowed_elements=allowed_tags,
                                 allowed_attributes_map=allowed_attributes_map,
                                 allowed_styles_map=allowed_styles_map,
                                 rename_elements=rename_elements)

    def __unicode__(self):
        return _(u"Comment by %s on %s as of %s") % (self.commenter,
                                                     self.page.name,
                                                     self.date)

    class Meta:
        verbose_name = _(u'Comment')
        verbose_name_plural = _(u'Comments')

    @property
    def commenter(self):
        # Find the first version of this comment, and return its User
        try:
            orig = self.versions.most_recent()
        except self.DoesNotExist:
            return None
        return orig.history_user

    @property
    def date(self):
        # Find the first version of this comment, and return its date
        try:
            orig = self.versions.most_recent()
        except self.DoesNotExist:
            return None
        return orig.history_date

    def save(self, *args, **kwargs):
        cfg, cre = CommentConfiguration.objects.get_or_create(page=self.page)
        if not cfg.enabled:
            raise IntegrityError("Comments not enabled on '%s'" %
                                 self.page.name)
        super(Comment, self).save(*args, **kwargs)

versioning.register(Comment)


class CommentConfiguration(models.Model):
    page = models.OneToOneField('pages.Page')
    enabled = models.BooleanField(default=True,
                                  help_text=_("Provide a Comments box on "
                                              "this page?"))
    heading = models.CharField(max_length=250, default="Comments",
                               help_text=_("Label for the comments box."))

    def __unicode__(self):
        return _(u"Comment configuration for page %s") % self.page.name

    class Meta:
        verbose_name = _(u'Comment Configuration')
        verbose_name_plural = _(u'Comment Configurations')

versioning.register(CommentConfiguration)

import feeds
