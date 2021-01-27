import copy
import json
from hashlib import md5
from io import StringIO

from django.contrib.auth.models import User, Permission
from django.urls import reverse
from rest_framework import status

from kpi.models import Asset
from kpi.constants import PERM_VIEW_ASSET, PERM_CHANGE_ASSET, \
    PERM_SHARE_ASSET
from kpi.models.object_permission import get_anonymous_user
from kpi.serializers.v2.asset import AssetListSerializer
from kpi.serializers.v2.reports import ReportsDetailSerializer, ReportsListSerializer
from kpi.tests.base_test_case import BaseAssetTestCase, BaseTestCase
from kpi.tests.kpi_test_case import KpiTestCase
from kpi.urls.router_api_v2 import URL_NAMESPACE as ROUTER_URL_NAMESPACE

class ReportsDetailsApiTests(BaseAssetTestCase):
    fixture = ['test_data']

    URL_NAMESPACE = ROUTER_URL_NAMESPACE

    def setUp(self):
        self.client.login(username='someuser', password='someuser')
        url = reverse(self._get_endpoint('asset-list'))
        data = {'content': '{}', 'asset_type': 'survey'}
        self.r = self.client.post(url, data, format='json')
        self.asset = Asset.objects.get(uid=self.r.data.get('uid'))
        self.asset_url = self.r.data['url']
        self.assertEqual(self.r.status_code, status.HTTP_201_CREATED)
        self.asset_uid = self.r.data['uid']
        

    def test_reports_exist(self):
        resp = self.client.get(self._get_endpoint('report-list'), args=(self.asset_uid), format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # def test_submission_count(self):
    #     anotheruser = User.objects.get(username='anotheruser')
    #     self.asset.deploy(backend='mock', active=True)