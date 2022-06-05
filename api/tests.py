from django.conf import settings
from rest_framework.test import APITestCase


class TestUnitMetrobusList(APITestCase):
    def setUp(self):
        pass

    def test_list(self):
        api_url = "/api/units-metrobus/"
        resp = self.client.get(api_url)

        self.assertEqual(resp.status_code, 200)
        assert isinstance(resp.data["result"]["records"], list)

    def test_retrive(self):

        api_url = "/api/units-metrobus/1/"
        resp = self.client.get(api_url)

        try:
            self.assertEqual(resp.status_code, 200)
            assert resp.data["district"] in settings.DISTRICTS
            assert isinstance(resp.data, dict)
        except Exception:
            self.assertEqual(resp.status_code, 502)


class TestDistricts(APITestCase):
    def setUp(self):
        pass

    def test_list(self):
        api_url = "/api/districts/"
        resp = self.client.get(api_url)

        self.assertEqual(resp.status_code, 200)
        assert isinstance(resp.data, list)
        if resp.data:
            self.assertEqual(resp.data, settings.DISTRICTS)

    def test_retrive(self):

        api_url = f"/api/districts/{settings.DISTRICTS[0]}/"
        resp = self.client.get(api_url)

        self.assertEqual(resp.status_code, 200)
        assert isinstance(resp.data, dict)
        assert "token" in resp.data["url"]

        resp = self.client.get(resp.data["url"])

        self.assertEqual(resp.status_code, 200)
        assert isinstance(resp.data, dict)
        assert "units" in resp.data
        assert "query_completed" in resp.data
        assert "query_succes" in resp.data
