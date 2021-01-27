# coding: utf-8
from django.http import Http404
from rest_framework import viewsets, mixins
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.response import Response

from kpi.constants import (
    ASSET_TYPE_SURVEY,
    PERM_PARTIAL_SUBMISSIONS,
    PERM_VIEW_SUBMISSIONS,
)
from kpi.models import Asset
from kpi.models.object_permission import get_objects_for_user, get_anonymous_user
from kpi.serializers.v2.reports import ReportsListSerializer, ReportsDetailSerializer
from kpi.utils.viewset_mixins import AssetNestedObjectViewsetMixin


class ReportsViewSet(AssetNestedObjectViewsetMixin,
                     NestedViewSetMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    """
    ## Reports
    
    <pre class="prettyprint">
    <b>GET</b> /api/v2/assets/<code>{asset_uid}</code>/reports/
    </pre>

    The JSON format is enabled. Other formats are not currently available for this endpoint.

    <pre class="prettyprint">
    <b>GET</b> /api/v2/<code>{asset_uid}</code>/reports/?format=json
    </pre>
    
    or

    <pre class="prettyprint">
    <b>GET</b> /api/v2/<code>{asset_uid}</code>/reports.json
    </pre>

    >Example
    >
    > curl -X GET https://[kpi]/api/v2/assets/aSAvYreNzVEkrWg5Gdcvg/reports/


    ### CURRENT ENDPOINT
    """
    
    lookup_field = 'uid'
    pagination_class = None

    #TO DO:
    #Enable xml and GeoJSON

    # Requesting user must have *any* of these permissions
    required_permissions = [
        PERM_VIEW_SUBMISSIONS,
        PERM_PARTIAL_SUBMISSIONS,
    ]
    
    def get_serializer_class(self):
        return ReportsDetailSerializer

    # def get_object(self):
    #     """
    #     Raise a 404 if the user is not allowed to access this asset or the
    #     asset is not deployed
    #     """
    #     asset = super().get_object()  # uses result of `get_queryset()`
    #     if not asset.has_deployment:
    #         raise Http404
    #     for codename in self.required_permissions:
    #         # `has_perm()` handles anonymous users
    #         if asset.has_perm(self.request.user, codename):
    #             # Having any of the `required_permissions` suffices
    #             return asset
    #     raise Http404

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.asset)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = Asset.objects.filter(asset_type=ASSET_TYPE_SURVEY, uid=self.asset_uid).defer('content')
        return queryset