import recentchanges
from recentchanges import RecentChanges

from models import Comment


class CommentChanges(RecentChanges):
    classname = 'comments'

    def queryset(self, start_at=None):
        if start_at:
            return Comment.versions.filter(version_info__date__gte=start_at)
        return Comment.versions.all()

    def page(self, obj):
        return obj.page

    def title(self, obj):
        return 'Comment on page "%s"' % self.page(obj).name

    def diff_url(self, obj):
        return None

    def as_of_url(self, obj):
        return None

recentchanges.register(CommentChanges)
