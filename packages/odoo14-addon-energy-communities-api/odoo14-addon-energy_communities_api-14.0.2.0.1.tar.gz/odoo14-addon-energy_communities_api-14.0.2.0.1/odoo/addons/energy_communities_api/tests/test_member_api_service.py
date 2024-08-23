import random
import string
from unittest.mock import patch

import requests

from odoo.exceptions import AccessError
from odoo.tests import HttpCase, tagged

from odoo.addons.base_rest.tests.common import RegistryMixin

from ..schemas import CommunityInfo

try:
    from .data import client_data, client_data_response, server_auth_url
except:
    pass


@tagged("-at_install", "post_install")
class TestMemberApiService(HttpCase, RegistryMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setUpRegistry()

    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.community_id = "3"
        self.timeout = 600

    @property
    def token(self):
        if not hasattr(self, "_token"):
            data = client_data
            response = requests.post(server_auth_url, data=data)
            self._token = response.json().get("access_token")

        return f"Bearer {self._token}"

    @property
    def bad_token(self):
        token = "".join(random.choices(string.ascii_letters, k=30))
        return f"Bearer {token}"

    def test__me_endpoint__ok(self):
        # given http_client
        # self.url_open
        # and a valid token
        # self.token
        # a member belonging to two energy communities

        community_1_id = self.community_id
        community_2_id = "138"

        # when we call for the personal data fo
        response = self.url_open(
            "/api/energy-communities/me",
            headers={"Authorization": self.token, "CommunityId": community_1_id},
            timeout=self.timeout,
        )
        # then we obtain a 200 response code
        self.assertEqual(response.status_code, 200)
        # and an error response notifying this situation
        self.assertDictEqual(
            response.json(),
            {
                "data": client_data_response,
                "links": {
                    "next_page": None,
                    "previous_page": None,
                    "self_": "http://127.0.0.1:8069/api/energy-communities/me",
                },
            },
        )
        response = self.url_open(
            "/api/energy-communities/me",
            headers={"Authorization": self.token, "CommunityId": community_2_id},
            timeout=self.timeout,
        )
        self.assertNotEqual(
            response.json()["data"]["member_number"],
            client_data_response["member_number"],
        )

    def test__me_endpoint__without_community_header(self):
        # given http_client
        # self.url_open
        # and a valid token
        # self.token

        # when we call for the personal data in api without
        # the CommunityId header
        response = self.url_open(
            "/api/energy-communities/me", headers={"Authorization": self.token}
        )
        # then we obtain a 400 response code
        self.assertEqual(response.status_code, 400)
        # and an error response notifying this situation
        self.assertDictEqual(
            response.json(),
            {
                "code": 400,
                "description": "<p>CommunityId header is missing</p>",
                "name": "Bad Request",
            },
        )

    def test__me_endpoint__unauthorized(self):
        # given http_client
        # self.url_open
        # and a valid token
        # self.token

        # when we call for the personal data in api with a bad token
        response = self.url_open(
            "/api/energy-communities/me",
            headers={"Authorization": self.bad_token, "Content-Type": "app/json"},
        )
        # then we obtain a 401 response code
        self.assertEqual(response.status_code, 401)
        # and we get the correct information
        self.assertDictEqual(
            response.json(),
            {
                "code": 401,
                "description": "<p>The server could not verify that you are authorized to "
                "access the URL requested. You either supplied the wrong "
                "credentials (e.g. a bad password), or your browser doesn't "
                "understand how to supply the credentials required.</p>",
                "name": "Unauthorized",
            },
        )

    @patch(
        "odoo.addons.energy_communities_api.components.partner_api_info.PartnerApiInfo.get_member_info"
    )
    def test__me_endpoint__forbidden_error(self, patcher):
        # given http_client
        # self.url_open
        # and a valid token
        # self.token
        def raise_exception():
            return AccessError("What are you tring to do?? ⛔")

        patcher.side_effect = raise_exception()

        # when we call for the personal data in api with a bad token
        response = self.url_open(
            "/api/energy-communities/me",
            headers={
                "Authorization": self.token,
                "Content-Type": "app/json",
                "CommunityId": self.community_id,
            },
        )
        # then we obtain a 403 response code
        self.assertEqual(response.status_code, 403)
        # and we get the correct information
        self.assertDictEqual(
            response.json(),
            {
                "code": 403,
                "name": "Forbidden",
            },
        )

    @patch(
        "odoo.addons.energy_communities_api.components.partner_api_info.PartnerApiInfo.get_member_info"
    )
    def test__me_endpoint__unexpected_error(self, patcher):
        # given http_client
        # self.url_open
        # and a valid token
        # self.token
        def raise_exception():
            return Exception("AAAAAAAHHHHHHH! 🔪")

        patcher.side_effect = raise_exception()

        # when we call for the personal data in api with a bad token
        response = self.url_open(
            "/api/energy-communities/me",
            headers={
                "Authorization": self.token,
                "Content-Type": "app/json",
                "CommunityId": self.community_id,
            },
        )
        # then we obtain a 500 response code
        self.assertEqual(response.status_code, 500)
        # and we get the correct information
        self.assertDictEqual(
            response.json(),
            {
                "code": 500,
                "name": "Internal Server Error",
            },
        )

    @patch("odoo.addons.energy_communities_api.components.base.ApiInfo.get")
    def test__me_endpoint__partner_undefined(self, patcher):
        # given http_client
        # self.url_open
        # and a valid token
        # self.token
        patcher.return_value = None

        # when we call for the personal for an user without partner
        response = self.url_open(
            "/api/energy-communities/me",
            headers={
                "Authorization": self.token,
                "Content-Type": "app/json",
                "CommunityId": self.community_id,
            },
        )
        # then we obtain a 200 response code
        self.assertEqual(response.status_code, 200)
        # and we get and empty body information
        self.assertDictEqual(
            response.json(),
            {
                "data": None,
                "links": {
                    "next_page": None,
                    "previous_page": None,
                    "self_": "http://127.0.0.1:8069/api/energy-communities/me",
                },
            },
        )

    def test__me_communities_endpoint_real__ok(self):
        # given http_client
        # self.url_open
        # and a valid personal token
        # self.token

        # when we call for the energy_communties that i belong
        response = self.url_open(
            "/api/energy-communities/me/communities?page=2&page_size=2",
            headers={
                "Authorization": self.token,
            },
        )
        # then we obtain a 200 response code
        self.assertEqual(response.status_code, 200)

    @patch(
        "odoo.addons.energy_communities_api.components.partner_api_info.PartnerApiInfo.total_member_communities"
    )
    @patch(
        "odoo.addons.energy_communities_api.components.partner_api_info.PartnerApiInfo.get_member_communities"
    )
    def test__me_communities_endpoint__ok(
        self, patch_member_communites, patch_total_member_communities
    ):
        # given http_client
        # self.url_open
        # and a valid personal token
        # self.token
        def member_communities():
            return [
                CommunityInfo(id=value, name=f"test{value}", image="")
                for value in range(0, 10)
            ]

        patch_member_communites.return_value = member_communities()
        patch_total_member_communities.return_value = len(member_communities())
        # when we call for the energy_communties that i belong
        response = self.url_open(
            "/api/energy-communities/me/communities?page=2&page_size=2",
            headers={"Authorization": self.token},
            timeout=self.timeout,
        )
        # then we obtain a 200 response code
        self.assertEqual(response.status_code, 200)
        # and we get the correct information
        communities = response.json()
        self.assertGreaterEqual(len(communities.get("data", 0)), 1)
        self.assertDictEqual(
            communities.get("links", {}),
            {
                "self_": "http://127.0.0.1:8069/api/energy-communities/me/communities?page=2&page_size=2",
                "next_page": "http://127.0.0.1:8069/api/energy-communities/me/communities?page=3&page_size=2",
                "previous_page": "http://127.0.0.1:8069/api/energy-communities/me/communities?page=1&page_size=2",
            },
        )
        self.assertEqual(communities["total_results"], 10)

    @patch(
        "odoo.addons.energy_communities_api.components.partner_api_info.PartnerApiInfo.total_member_communities"
    )
    @patch(
        "odoo.addons.energy_communities_api.components.partner_api_info.PartnerApiInfo._get_communities"
    )
    def test__me_communities_endpoint__without_communities(
        self, patcher, patch_total_member_communities
    ):
        # given http_client
        # self.url_open
        # and a valid token
        # self.token
        patcher.return_value = []
        patch_total_member_communities.return_value = 0

        # when we call for the personal for an user without partner
        response = self.url_open(
            "/api/energy-communities/me/communities",
            headers={"Authorization": self.token, "Content-Type": "app/json"},
        )
        # then we obtain a 200 response code
        self.assertEqual(response.status_code, 200)
        # and we get and empty body information
        self.assertDictEqual(
            response.json(),
            {
                "data": [],
                "total_results": 0,
                "count": 0,
                "page": 1,
                "links": {
                    "next_page": None,
                    "previous_page": None,
                    "self_": "http://127.0.0.1:8069/api/energy-communities/me/communities",
                },
            },
        )

    @patch(
        "odoo.addons.energy_communities_api.components.partner_api_info.PartnerApiInfo.get_member_communities"
    )
    def test__me_communities_endpoint__bad_request(self, patcher):
        # given http_client
        # self.url_open
        # and a valid personal token
        # self.token
        def member_communities():
            return [
                CommunityInfo(id=value, name=f"test{value}", image="")
                for value in range(0, 10)
            ]

        patcher.return_value = member_communities()
        # when we call for the energy_communties with bad parameters
        response = self.url_open(
            "/api/energy-communities/me/communities?page=fgdhjkl&page_size=2",
            headers={"Authorization": self.token},
        )
        # then we obtain a 400 response code
        self.assertEqual(response.status_code, 400)
        # and we get a bad request response
        self.assertDictEqual(
            response.json(),
            {
                "code": 400,
                "name": "Bad Request",
                "description": "<p>BadRequest [<br>{<br>&quot;loc&quot;: [<br>&quot;page&quot;<br>],<br>&quot;msg&quot;: &quot;value is not a valid integer&quot;,<br>&quot;type&quot;: &quot;type_error.integer&quot;<br>}<br>]</p>",
            },
        )
