from django import forms
from django.template.defaultfilters import linebreaks, striptags
from django.utils.translation import ugettext as _
from utils.static import static_url
from versionutils.versioning.forms import CommentMixin

from models import Comment


class CommentForm(CommentMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        try:
            # If we were passed in a comment_config, take it.
            cfg = kwargs.pop('comment_config')
        except KeyError:
            cfg = None
        super(CommentForm, self).__init__(*args, **kwargs)
        # Use the heading configured for this page to produce a label.
        if cfg is not None:
            self.fields['content'].label = cfg.heading

    class Meta:
        model = Comment
        fields = ('content',)
        exclude = ('comment',)  # the edit comment itself, auto-generated
        widgets = {'content': forms.widgets.Textarea(attrs={
                    'rows': 2,
                    'class': 'comment-box',
                    'placeholder': _("Please feel free to add a comment to "
                                     "this page."),
                  })}

    class Media:
        css = {
            'all': (static_url('css/comments/comments.css'),),
        }

    def clean_content(self):
        content = self.cleaned_data['content']
        return linebreaks(content)

    def get_save_comment(self):
        # Include the first 80 bytes or so of the content.
        snippets = striptags(self.cleaned_data['content']).split(' ')
        teaser = ""
        for snippet in snippets:
            teaser += snippet + ' '
            if len(teaser) > 80:
                teaser += '...'
                break
        return _("Comment added: %s") % teaser
