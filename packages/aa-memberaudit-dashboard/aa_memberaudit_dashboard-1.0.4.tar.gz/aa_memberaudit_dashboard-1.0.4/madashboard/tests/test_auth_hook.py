from unittest.mock import MagicMock

from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse

from app_utils.testing import create_user_from_evecharacter

from madashboard.auth_hooks import MemberCheckDashboardHook, register_membercheck_hook
from madashboard.tests.testdata.load_allianceauth import load_allianceauth
from madashboard.tests.testdata.load_memberaudit import load_memberaudit


class TestAuthHooks(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_allianceauth()
        load_memberaudit()
        cls.factory = RequestFactory()
        cls.user, cls.character_ownership = create_user_from_evecharacter(1001)

    def test_render_returns_empty_string_for_user_without_permission(self):
        # given
        request = self.factory.get("/")
        request.user = self.user
        ledger_menu_item = MemberCheckDashboardHook()

        # when
        response = ledger_menu_item.render(request)
        # Convert SafeString to HttpResponse for testing
        response = HttpResponse(response)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            '<div id="memberaudit-check-dashboard-widget" class="col-12 align-self-stretch py-2">',
            response.content.decode("utf-8"),
        )

    def test_register_membercheck_hook(self):
        # given
        hooks = register_membercheck_hook()

        # then
        self.assertIsInstance(hooks, MemberCheckDashboardHook)
