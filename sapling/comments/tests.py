from django.core.urlresolvers import reverse
from django.test import TestCase

from models import Comment, CommentConfiguration
from pages.models import Page


class CommentTest(TestCase):

    def setUp(self):
        self.page_default = Page.objects.create(
                                name="Page with Default Configuration",
                                content="All good out of the gate?")
        self.page_enabled = Page.objects.create(
                                name="Page For Commenting",
                                content="This page allows comments.")
        self.page_disabled = Page.objects.create(
                                name="Page Without Comments",
                                content="This page disallows comments.")
        self.page_closed = Page.objects.create(
                                name="Page With Old Comments",
                                content="This page formerly allowed comments.")

        Comment.objects.create(page=self.page_closed,
                               content="Boogers!")

        for p, ena in [(self.page_enabled, True),
                       (self.page_disabled, False),
                       (self.page_closed, False)]:
            cfg, cre = CommentConfiguration.objects.get_or_create(
                            page=p)
            cfg.enabled = ena
            cfg.save()

    def _page_req(self, page):
        url = reverse('pages:show', kwargs={'slug': page.slug})
        return self.client.get(url)

    def test_comment_form_display_default(self):
        # Ensures that the comment form is displayed when expected.
        response = self._page_req(self.page_default)
        self.assertContains(response, 'class="comment-box"')

    def test_comment_form_display_enabled(self):
        # Ensures that the comment form is displayed when expected.
        response = self._page_req(self.page_enabled)
        self.assertContains(response, 'class="comment-box"')

    def test_comment_form_display_disabled(self):
        # Ensures that the comment form is not displayed when unexpected.
        response = self._page_req(self.page_disabled)
        self.assertNotContains(response, 'class="comment-box"')

    def test_comment_form_display_closed(self):
        # Ensures that the comment form is not displayed when unexpected.
        response = self._page_req(self.page_closed)
        self.assertNotContains(response, 'class="comment-box"')

    def test_comment_form_heading_change(self):
        # Modify the displayed heading, make sure it works
        cfg = CommentConfiguration.objects.get(page=self.page_enabled)
        cfg.heading = "Technicolor Yawns"
        cfg.save()

        response = self._page_req(self.page_enabled)
        self.assertContains(response, 'Technicolor Yawns')

    def test_comment_form_submit_enabled(self):
        # Try submitting a comment to a page with commenting
        # enabled, make sure it works.

        # First, we log in.
        from django.contrib.auth.models import User, Permission
        u = User.objects.create(username='bob', password='bob',
                                email='bob@example.com')
        u.set_password('bob')
        u.user_permissions = [Permission.objects.get(codename='change_page')]
        u.save()
        response = self.client.post('/Users/login/',
                {'next': '/%s' % self.page_enabled.slug,
                 'username': 'bob',
                 'password': 'bob',
                 'content2': '',
                 'content2_js': '1',
                }, follow=True)
        self.assertContains(response, '/Users/bob')

        # Now that we're logged in, try submitting a comment.
        data = {'content': "This is some content, eh!",
                'next': '/%s' % self.page_enabled.slug,
                'content2': '',
                'content2_js': '1',
               }
        response = self.client.post('/%s/_comments/' % self.page_enabled.slug,
            data, follow=True)

        response = self._page_req(self.page_enabled)
        self.assertContains(response, data['content'])

    def test_comment_form_submit_disabled(self):
        # Try submitting a comment to a page with commenting
        # disabled, make sure it fails.

        # First, we log in.
        from django.contrib.auth.models import User, Permission
        from django.db.utils import IntegrityError
        u = User.objects.create(username='bob', password='bob',
                                email='bob@example.com')
        u.set_password('bob')
        u.user_permissions = [Permission.objects.get(codename='change_page')]
        u.save()
        response = self.client.post('/Users/login/',
                {'next': '/%s' % self.page_disabled.slug,
                 'username': 'bob',
                 'password': 'bob',
                 'content2': '',
                 'content2_js': '1',
                }, follow=True)
        self.assertContains(response, '/Users/bob')

        # Now that we're logged in, try submitting a comment.
        data = {'content': "This is some content, eh!",
                'next': '/%s' % self.page_disabled.slug,
                'content2': '',
                'content2_js': '1',
               }
        with self.assertRaises(IntegrityError):
            response = self.client.post(
                '/%s/_comments/' % self.page_disabled.slug, data, follow=True)

        response = self._page_req(self.page_disabled)
        self.assertNotContains(response, data['content'])

    def test_comment_list_display_closed(self):
        # Did the comment list display properly?
        response = self._page_req(self.page_closed)
        self.assertContains(response, 'Boogers!')

    def test_comment_list_display_new_comment(self):
        # Post a comment, make sure it displays.
        cmt = Comment.objects.create(page=self.page_enabled,
                                     content="Heyyyyyy")
        response = self._page_req(self.page_enabled)
        self.assertContains(response, cmt.content)

    def test_comment_model_disabled_page(self):
        # Ensure that we can't add comments to a page without
        # comments enabled.
        content = "Nayyyyyy"

        from django.db.utils import IntegrityError
        with self.assertRaises(IntegrityError):
            Comment.objects.create(page=self.page_disabled,
                                   content=content)

        response = self._page_req(self.page_disabled)
        self.assertNotContains(response, content)
