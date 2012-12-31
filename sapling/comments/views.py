from django.shortcuts import get_object_or_404

from pages.models import Page
from utils.views import PermissionRequiredMixin, CreateObjectMixin
from versionutils.versioning.views import UpdateView

from forms import CommentForm
from models import Comment


class CommentUpdateView(PermissionRequiredMixin, CreateObjectMixin,
                        UpdateView):
    model = Comment
    form_class = CommentForm
    permission = 'pages.change_page'

    def get_object(self):
        # The page slug is a required keyword argument.
        page_slug = self.kwargs.get('slug')
        page = get_object_or_404(Page, slug=page_slug)
        return Comment(page=page)

    def get_success_url(self):
        next = self.request.POST.get('next', None)
        if next is not None:
            return next
        return self.object.page.get_absolute_url()
