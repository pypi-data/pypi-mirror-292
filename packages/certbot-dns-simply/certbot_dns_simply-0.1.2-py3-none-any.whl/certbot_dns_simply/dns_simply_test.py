"""Tests for certbot_dns_simply.dns_simply."""

import unittest
from unittest import mock

import requests_mock
from certbot.compat import os
from certbot.errors import PluginError
from certbot.plugins import dns_test_common
from certbot.plugins.dns_test_common import DOMAIN
from certbot.tests import util as test_util

from certbot_dns_simply.dns_simply import Authenticator, SimplyClient

patch_display_util = test_util.patch_display_util

FAKE_RECORD = {
    "record": {
        "id": "123Fake",
    }
}


class TestAuthenticator(
    test_util.TempDirTestCase, dns_test_common.BaseAuthenticatorTest
):
    """
    Test for Simply DNS Authenticator
    """

    def setUp(self):
        super().setUp()
        path = os.path.join(self.tempdir, "fake_credentials.ini")
        dns_test_common.write(
            {
                "simply_account_name": "account_name",
                "simply_api_key": "api_key",
            },
            path,
        )

        super().setUp()
        self.config = mock.MagicMock(
            simply_credentials=path, simply_propagation_seconds=0
        )

        self.auth = Authenticator(config=self.config, name="simply")

        self.mock_client = mock.MagicMock()

        mock_client_wrapper = mock.MagicMock()
        mock_client_wrapper.__enter__ = mock.MagicMock(return_value=self.mock_client)

        # _get_simply_client | pylint: disable=protected-access
        self.auth._get_simply_client = mock.MagicMock(return_value=mock_client_wrapper)

    @patch_display_util()
    def test_perform(self, _unused_mock_get_utility):
        self.mock_client.add_txt_record.return_value = FAKE_RECORD
        self.auth.perform([self.achall])
        self.mock_client.add_txt_record.assert_called_with(
            DOMAIN, "_acme-challenge." + DOMAIN, mock.ANY
        )

    def test_perform_but_raises_plugin_error(self):
        self.mock_client.add_txt_record.side_effect = mock.MagicMock(
            side_effect=PluginError()
        )
        self.assertRaises(PluginError, self.auth.perform, [self.achall])
        self.mock_client.add_txt_record.assert_called_with(
            DOMAIN, "_acme-challenge." + DOMAIN, mock.ANY
        )

    @patch_display_util()
    def test_cleanup(self, _unused_mock_get_utility):
        self.mock_client.add_txt_record.return_value = FAKE_RECORD
        # _attempt_cleanup | pylint: disable=protected-access
        self.auth.perform([self.achall])
        self.auth._attempt_cleanup = True
        self.auth.cleanup([self.achall])

        self.mock_client.del_txt_record.assert_called_with(
            DOMAIN, "_acme-challenge." + DOMAIN, mock.ANY
        )

    @patch_display_util()
    def test_cleanup_but_raises_plugin_error(self, _unused_mock_get_utility):
        self.mock_client.add_txt_record.return_value = FAKE_RECORD
        self.mock_client.del_txt_record.side_effect = mock.MagicMock(
            side_effect=PluginError()
        )
        # _attempt_cleanup | pylint: disable=protected-access
        self.auth.perform([self.achall])
        self.auth._attempt_cleanup = True

        self.assertRaises(PluginError, self.auth.cleanup, [self.achall])
        self.mock_client.del_txt_record.assert_called_with(
            DOMAIN, "_acme-challenge." + DOMAIN, mock.ANY
        )


class TestSimplyClient(unittest.TestCase):
    """
    Test for Simply API Client
    """

    def setUp(self):
        self.client = SimplyClient("account_name", "api_key")
        self.domain = "example.com"
        self.object_id = "<object_id>"
        self.acme_challenge = "_acme-challenge"

    @requests_mock.Mocker()
    def test_add_txt_record(self, request_mock):
        request_mock.post(
            f"https://api.simply.com/2/my/products/{self.object_id}/dns/records/",
            status_code=200,
            json=[{}],
        )
        self._my_products_get_mock(request_mock, self.object_id)
        self.client.add_txt_record(
            self.domain, f"{self.acme_challenge}.{self.domain}", "test_validation"
        )
        self.assertTrue(request_mock.called)

    @requests_mock.Mocker()
    def test_add_txt_record_subdomain(self, request_mock):
        self.domain = "foo.example.com"
        request_mock.post(
            f"https://api.simply.com/2/my/products/{self.object_id}/dns/records/",
            status_code=200,
            json=[{}],
        )
        self._my_products_get_mock(request_mock, self.object_id)
        self.client.add_txt_record(
            self.domain, f"{self.acme_challenge}.{self.domain}", "test_validation"
        )
        self.assertTrue(request_mock.called)

    @requests_mock.Mocker()
    def test_add_txt_record_country_code_top_level_domain(self, request_mock):
        self.domain = "foo.example.co.uk"
        request_mock.post(
            f"https://api.simply.com/2/my/products/{self.object_id}/dns/records/",
            status_code=200,
            json=[{}],
        )
        self._my_products_get_mock(
            request_mock, self.object_id, "example.co.uk", "example.co.uk"
        )
        self.client.add_txt_record(
            self.domain, f"{self.acme_challenge}.{self.domain}", "test_validation"
        )
        self.assertTrue(request_mock.called)

    @requests_mock.Mocker()
    def test_add_txt_record_idn_domain(self, request_mock):
        self.domain = "foo.bar.exampleæøå.com"
        request_mock.post(
            f"https://api.simply.com/2/my/products/{self.object_id}/dns/records/",
            status_code=200,
            json=[{}],
        )
        self._my_products_get_mock(
            request_mock,
            self.object_id,
            "foo.bar.exampleæøå.com",
            "foo.bar.xn--example-kxai4p.com",
        )
        self.client.add_txt_record(
            self.domain, f"{self.acme_challenge}.{self.domain}", "test_validation"
        )
        self.assertTrue(request_mock.called)

    @requests_mock.Mocker()
    def test_add_txt_record_idn_domain_punycode(self, request_mock):
        self.domain = "foo.bar.xn--example-kxai4p.com"
        request_mock.post(
            f"https://api.simply.com/2/my/products/{self.object_id}/dns/records/",
            status_code=200,
            json=[{}],
        )
        self._my_products_get_mock(
            request_mock,
            self.object_id,
            "foo.bar.exampleæøå.com",
            "foo.bar.xn--example-kxai4p.com",
        )
        self.client.add_txt_record(
            self.domain, f"{self.acme_challenge}.{self.domain}", "test_validation"
        )
        self.assertTrue(request_mock.called)

    @requests_mock.Mocker()
    def test_add_txt_record_wildcard(self, request_mock):
        self.domain = "*.example.com"
        request_mock.post(
            f"https://api.simply.com/2/my/products/{self.object_id}/dns/records/",
            status_code=200,
            json=[{}],
        )
        self._my_products_get_mock(request_mock, self.object_id)
        self.client.add_txt_record(
            self.domain, f"{self.acme_challenge}.{self.domain}", "test_validation"
        )
        self.assertTrue(request_mock.called)

    @requests_mock.Mocker()
    def test_add_txt_record_fail(self, request_mock):
        request_mock.post(
            f"https://api.simply.com/2/my/products/{self.object_id}/dns/records/",
            status_code=400,
            json=[{}],
        )
        self._my_products_get_mock(request_mock, self.object_id)

        with self.assertRaises(PluginError):
            self.client.add_txt_record(
                self.domain, f"{self.acme_challenge}.{self.domain}", "test_validation"
            )

    @requests_mock.Mocker()
    def test_del_txt_record(self, request_mock):
        validation_name = f"{self.acme_challenge}.{self.domain}"
        request_mock.get(
            f"https://api.simply.com/2/my/products/{self.object_id}/dns/records/",
            json={
                "records": [
                    {
                        "record_id": 123,
                        "type": "TXT",
                        "name": validation_name,
                        "data": "test_validation",
                    },
                    {
                        "record_id": 333,
                        "type": "NS",
                        "name": "@",
                        "data": "ns1.simply.com",
                    },
                ]
            },
        )
        self._my_products_get_mock(request_mock, self.object_id)
        self._remove_record_delete_mock(request_mock)

        self.client.del_txt_record(self.domain, validation_name, "test_validation")
        self.assertTrue(request_mock.call_count == 3)
        self.assertTrue(request_mock.request_history[0].method == "GET")
        self.assertTrue(request_mock.request_history[1].method == "GET")
        self.assertTrue(request_mock.request_history[2].method == "DELETE")

    @requests_mock.Mocker()
    def test_del_txt_record_subdomain(self, request_mock):
        self.domain = "foo.example.com"
        validation_name = f"{self.acme_challenge}.{self.domain}"
        request_mock.get(
            f"https://api.simply.com/2/my/products/{self.object_id}/dns/records/",
            json={
                "records": [
                    {
                        "record_id": 123,
                        "type": "TXT",
                        "name": validation_name,
                        "data": "test_validation",
                    },
                    {
                        "record_id": 333,
                        "type": "NS",
                        "name": "@",
                        "data": "ns1.simply.com",
                    },
                ]
            },
        )
        self._my_products_get_mock(request_mock, self.object_id)
        self._remove_record_delete_mock(request_mock)

        self.client.del_txt_record(self.domain, validation_name, "test_validation")
        self.assertTrue(request_mock.call_count == 3)
        self.assertTrue(request_mock.request_history[0].method == "GET")
        self.assertTrue(request_mock.request_history[1].method == "GET")
        self.assertTrue(request_mock.request_history[2].method == "DELETE")

    @requests_mock.Mocker()
    def test_del_txt_record_wildcard(self, request_mock):
        self.domain = "*.example.com"
        validation_name = f"{self.acme_challenge}.{self.domain}"
        request_mock.get(
            f"https://api.simply.com/2/my/products/{self.object_id}/dns/records/",
            json={
                "records": [
                    {
                        "record_id": 123,
                        "type": "TXT",
                        "name": validation_name,
                        "data": "test_validation",
                    },
                    {
                        "record_id": 333,
                        "type": "NS",
                        "name": "@",
                        "data": "ns1.simply.com",
                    },
                ]
            },
        )
        self._my_products_get_mock(request_mock, self.object_id)
        self._remove_record_delete_mock(request_mock)

        self.client.del_txt_record(self.domain, validation_name, "test_validation")
        self.assertTrue(request_mock.call_count == 3)
        self.assertTrue(request_mock.request_history[0].method == "GET")
        self.assertTrue(request_mock.request_history[1].method == "GET")
        self.assertTrue(request_mock.request_history[2].method == "DELETE")

    @requests_mock.Mocker()
    def test_del_txt_record_fail(self, request_mock):
        validation_name = f"{self.acme_challenge}.{self.domain}"
        request_mock.get(
            f"https://api.simply.com/2/my/products/{self.object_id}/dns/records/",
            json={
                "records": [
                    {
                        "record_id": 123,
                        "type": "TXT",
                        "name": validation_name,
                        "data": "test_validation",
                    },
                    {
                        "record_id": 333,
                        "type": "NS",
                        "name": "@",
                        "data": "ns1.simply.com",
                    },
                ]
            },
        )
        self._my_products_get_mock(request_mock, self.object_id)
        request_mock.delete(
            f"https://api.simply.com/2/my/products/{self.object_id}/dns/records/123/",
            status_code=400,
            text="Error",
        )

        with self.assertRaises(PluginError):
            self.client.del_txt_record(self.domain, validation_name, "test_validation")

    @requests_mock.Mocker()
    def test_add_txt_record_domain_missing(self, request_mock):
        request_mock.post(
            f"https://api.simply.com/2/my/products/{self.object_id}/dns/records/",
            status_code=400,
            json=[{}],
        )

        self._my_products_get_mock_domain_missing(request_mock)

        with self.assertRaises(PluginError):
            self.client.add_txt_record(
                self.domain, f"{self.acme_challenge}.{self.domain}", "test_validation"
            )

    @staticmethod
    def _my_products_get_mock(
        request_mock,
        object_id: str,
        domain: str = "example.com",
        domain_idn: str = "example.com",
    ):
        request_mock.get(
            "https://api.simply.com/2/my/products/",
            status_code=200,
            json={
                "products": [
                    {
                        "object": f"{object_id}",
                        "name": "example.com",
                        "autorenew": "true",
                        "cancelled": "false",
                        "domain": {"name": f"{domain}", "name_idn": f"{domain_idn}"},
                        "product": {
                            "id": 1,
                            "name": "dnsservice",
                            "date_created": "1695716709",
                            "date_expire": "false",
                        },
                    }
                ],
                "status": 200,
                "message": "success",
            },
        )

    def _my_products_get_mock_domain_missing(self, request_mock):
        request_mock.get(
            "https://api.simply.com/2/my/products/",
            status_code=200,
            json={
                "products": [
                    {
                        "object": f"{self.object_id}",
                        "name": "example.com",
                        "autorenew": "true",
                        "cancelled": "false",
                        "domain": {"name": "missing.com", "name_idn": "missing.com"},
                        "product": {
                            "id": 1,
                            "name": "dnsservice",
                            "date_created": "1695716709",
                            "date_expire": "false",
                        },
                    }
                ],
                "status": 200,
                "message": "success",
            },
        )

    def _remove_record_delete_mock(self, request_mock):
        request_mock.delete(
            f"https://api.simply.com/2/my/products/{self.object_id}/dns/records/123/",
            status_code=200,
            json=[{}],
        )


if __name__ == "__main__":
    unittest.main()
