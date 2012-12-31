from django import template
from django.template.loader import render_to_string

from comments.forms import CommentForm
from comments.models import Comment, CommentConfiguration

register = template.Library()


@register.simple_tag
def comment_list(page):
    try:
        comment_list = page.comment_set.all()
    except Comment.DoesNotExist:
        comment_list = []
    return render_to_string('comments/comment_list_snippet.html',
        {'comment_list': comment_list})


@register.simple_tag(takes_context=True)
def comment_form(context, page):
    cfg, created = CommentConfiguration.objects.get_or_create(page=page)
    context.push()
    context['comments_enabled'] = cfg.enabled
    context['form'] = CommentForm(comment_config=cfg)
    rendered = render_to_string('comments/comment_form_snippet.html', context)
    context.pop()
    return rendered
