from django.utils.translation import ugettext_lazy as _

from django.core.files import File
from rest_framework import (
    renderers,
    status,
    viewsets
)
from rest_framework.pagination import _positive_int as positive_int
from rest_framework.response import Response
from pydub import AudioSegment

from kpi.deployment_backends.kobocat_backend import KobocatDeploymentBackend
from kpi.models.asset import Asset
from kpi.permissions import (
    EditSubmissionPermission,
    SubmissionPermission,
    ViewSubmissionPermission,
)
from kpi.renderers import SubmissionXMLRenderer


class MediaFileRenderer(renderers.BaseRenderer):
    media_type = '*/*'
    format = None
    charset = 'utf-8'
    render_style = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class AudioConversionViewSet(viewsets.ViewSet):
    # probably nested in Data
    # need the submission ID to get the inputs for the deployment backend method
    lookup_field = 'filename'
    renderer_classes = (
                        MediaFileRenderer,
                        )
    permission_classes = (SubmissionPermission,)

    class Meta:
        pass

    def list(self, request, *args, **kwargs):
        format_type = kwargs.get('format', request.GET.get('format', 'json'))
        # the audio file will probably need to be posted by the UI or user to be accessible
        # filename = kwargs['filename']
        # print(filename, flush=True)

        asset_uid = 'aytEVVy9VNd9b7vJPACm3n'
            # kwargs['parent_lookup_asset']
        data_id = '360'
            # kwargs['parent_lookup_data']
        xpath = 'Upload_a_file'
            # kwargs['path']

        asset = Asset.objects.get(uid=asset_uid)
        print(asset, flush=True)
        submission = asset.deployment.get_submission(
                positive_int(data_id),
                user=request.user,
                format_type=format_type,
                request=request,
        )
        submission_uuid = submission['_uuid']

        file = asset.deployment.get_attachment_content(request.user, submission_uuid, xpath)
        audio = AudioSegment.from_file(file)
        export_path = 'tmp/random_filename.mp3'
        converted = File(audio.export(export_path, format='mp3'))

        with open(f'tmp/random_filename.mp3', encoding='utf8', errors='ignore') as f:
            content = f.read()


        # converted = File(converted)
        return Response(
            content,
            # content_type='audio/mp3',
        )

    # def _filter_mongo_query(self, request):
    #     """
    #     Build filters to pass to Mongo query.
    #     Acts like Django `filter_backends`
    #
    #     :param request:
    #     :return: dict
    #     """
    #     filters = {}
    #
    #     if request.method == "GET":
    #         filters = request.GET.dict()
    #
    #     # Remove `format` from filters. No need to use it
    #     filters.pop('format', None)
    #     # Do not allow requests to retrieve more than `SUBMISSION_LIST_LIMIT`
    #     # submissions at one time
    #     limit = filters.get('limit', settings.SUBMISSION_LIST_LIMIT)
    #     try:
    #         filters['limit'] = positive_int(
    #             limit, strict=True, cutoff=settings.SUBMISSION_LIST_LIMIT
    #         )
    #     except ValueError:
    #         raise ValueError(
    #             {'limit': _('A positive integer is required')}
    #         )
    #
    #     return filters
