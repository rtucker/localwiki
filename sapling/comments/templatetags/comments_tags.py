from django import template
from django.template.loader import render_to_string

from comments.forms import CommentForm
from comments.models import CommentConfiguration
from pages.models import Page

register = template.Library()


@register.simple_tag
def comment_list(page):
    # Render a list of comments.  Note that comment_form must also be
    # included somewhere, so that the right CSS are loaded.
    comment_list = page.comment_set.all()
    return render_to_string('comments/comment_list_snippet.html',
        {'comment_list': comment_list})


@register.simple_tag(takes_context=True)
def comment_form(context, page):
    # Output a form for entering a comment, if comments are enabled.
    context.push()
    if isinstance(page, Page):
        try:
            cfg = CommentConfiguration.objects.get(page=page)
        except CommentConfiguration.DoesNotExist:
            cfg = CommentConfiguration(page=page)
            cfg.save(track_changes=False)
        context['comments_enabled'] = cfg.enabled
        context['form'] = CommentForm(comment_config=cfg)
    rendered = render_to_string('comments/comment_form_snippet.html', context)
    context.pop()
    return rendered
