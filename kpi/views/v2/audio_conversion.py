from io import BytesIO
from tempfile import NamedTemporaryFile

from django.utils.translation import ugettext_lazy as _
from rest_framework import (
    renderers,
from django.utils.translation import ugettext_lazy as _

from django.core.files import File
from rest_framework import (
    renderers,
    status,
    viewsets
)
from rest_framework.pagination import _positive_int as positive_int
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin
from pydub import AudioSegment

from kpi.models.asset import Asset
from kpi.permissions import (
    SubmissionPermission,
)
from kpi.utils.viewset_mixins import AssetNestedObjectViewsetMixin


class MediaFileRenderer(renderers.BaseRenderer):
    media_type = '*/*'
    format = None
    charset = None
    render_style = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class MP3ConversionRenderer(MediaFileRenderer):
    media_type = 'audio/mpeg'
    format = 'mp3'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        audio = AudioSegment.from_file(BytesIO(data))

        with NamedTemporaryFile(suffix='.mp3') as f:
            export = audio.export(f, format='mp3')
            content = export.read()
        return content


class AudioConversionViewSet(
    NestedViewSetMixin,
    AssetNestedObjectViewsetMixin,
    viewsets.ViewSet
):
    renderer_classes = (MediaFileRenderer, MP3ConversionRenderer)
    permission_classes = (SubmissionPermission,)

    def list(self, request, *args, **kwargs):
        """
        ## GET an audio or video file

        <pre class="prettyprint">
        <b>GET</b>  /api/v2/assets/<code>{asset_uid}</code>/data/<code>{data_id}</code>/audio_conversion/?xpath=<code>{xml_path_to_question}</code>
        </pre>

        > Example
        >
        >       curl -X GET https://[kpi]/api/v2/assets/aSAvYreNzVEkrWg5Gdcvg/data/451/audio_conversion/?xpath=Upload_a_file

        ## GET an MP3 file from an audio or video file
        Convert audio and video files. Only conversions to MP3 is supported for this feature

        <pre class="prettyprint">
        <b>GET</b> /api/v2/assets/<code>{asset_uid}</code>/data/<code>{data_id}</code>/audio_conversion/?xpath=<code>{xml_path_to_question}</code>&format=mp3
        </pre>

        > Example
        >
        >       curl -X GET https://[kpi]/api/v2/assets/aSAvYreNzVEkrWg5Gdcvg/data/451/audio_conversion/?xpath=Upload_a_file&format=mp3
        """
        asset_uid = kwargs['parent_lookup_asset']
        data_id = kwargs['parent_lookup_data']
        filters = request.GET.dict()
        try:
            xpath = filters['xpath']
        except KeyError:
            raise Exception(_('xpath not found, please query the path to the file'))

        asset = Asset.objects.get(uid=asset_uid)
        submission = asset.deployment.get_submission(
                positive_int(data_id),
                user=request.user,
                request=request,
        )
        submission_uuid = submission['_uuid']
        content, content_type = asset.deployment.get_attachment_content(
            request.user,
            submission_uuid,
            xpath
        )

        if request.accepted_renderer.format == 'mp3':
            set_content = None
        else:
            set_content = content_type

        return Response(
           content,
           content_type=set_content,
        )
