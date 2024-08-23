# -*- coding: utf-8; -*-

from wuttaweb.views import common as mod
from tests.util import WebTestCase


class TestCommonView(WebTestCase):

    def make_view(self):
        return mod.CommonView(self.request)

    def test_includeme(self):
        self.pyramid_config.include('wuttaweb.views.common')

    def test_forbidden_view(self):
        view = self.make_view()
        context = view.forbidden_view()
        self.assertEqual(context['index_title'], self.app.get_title())

    def test_notfound_view(self):
        view = self.make_view()
        context = view.notfound_view()
        self.assertEqual(context['index_title'], self.app.get_title())

    def test_home(self):
        self.pyramid_config.add_route('setup', '/setup')
        self.pyramid_config.add_route('login', '/login')
        model = self.app.model
        view = self.make_view()

        # if no users then home page will redirect
        response = view.home(session=self.session)
        self.assertEqual(response.status_code, 302)

        # so add a user
        user = model.User(username='foo')
        self.session.add(user)
        self.session.commit()

        # now we see the home page
        context = view.home(session=self.session)
        self.assertEqual(context['index_title'], self.app.get_title())

        # but if configured, anons will be redirected to login
        self.config.setdefault('wuttaweb.home_redirect_to_login', 'true')
        response = view.home(session=self.session)
        self.assertEqual(response.status_code, 302)

        # now only an auth'ed user can see home page
        self.request.user = user
        context = view.home(session=self.session)
        self.assertEqual(context['index_title'], self.app.get_title())

    def test_setup(self):
        self.pyramid_config.add_route('home', '/')
        self.pyramid_config.add_route('login', '/login')
        model = self.app.model
        auth = self.app.get_auth_handler()
        view = self.make_view()

        # at first, can see the setup page
        self.assertEqual(self.session.query(model.User).count(), 0)
        context = view.setup(session=self.session)
        self.assertEqual(context['index_title'], self.app.get_title())

        # so add a user
        user = model.User(username='foo')
        self.session.add(user)
        self.session.commit()

        # once user exists it will always redirect
        response = view.setup(session=self.session)
        self.assertEqual(response.status_code, 302)

        # delete that user
        self.session.delete(user)
        self.session.commit()

        # so we can see the setup page again
        context = view.setup(session=self.session)
        self.assertEqual(context['index_title'], self.app.get_title())

        # and finally, post data to create admin user
        self.request.method = 'POST'
        self.request.POST = {
            'username': 'barney',
            '__start__': 'password:mapping',
            'password': 'testpass',
            'password-confirm': 'testpass',
            '__end__': 'password:mapping',
            'first_name': "Barney",
            'last_name': "Rubble",
        }
        response = view.setup(session=self.session)
        # nb. redirects on success
        self.assertEqual(response.status_code, 302)
        barney = self.session.query(model.User).one()
        self.assertEqual(barney.username, 'barney')
        self.assertTrue(auth.check_user_password(barney, 'testpass'))
        admin = auth.get_role_administrator(self.session)
        self.assertIn(admin, barney.roles)
        self.assertIsNotNone(barney.person)
        person = barney.person
        self.assertEqual(person.first_name, "Barney")
        self.assertEqual(person.last_name, "Rubble")
        self.assertEqual(person.full_name, "Barney Rubble")
