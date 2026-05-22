from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from .models import Reaction


class ReactionView(APIView):
    permission_classes = [AllowAny]

    def get_session_key(self, request):
        if not request.session.session_key:
            request.session.create()
        return request.session.session_key

    def get(self, request):
        content_type_str = request.GET.get('content_type')
        object_id = request.GET.get('object_id')
        if not content_type_str or not object_id:
            return Response({'error': 'content_type and object_id required'}, status=400)
        try:
            app_label, model = content_type_str.split('.')
            ct = ContentType.objects.get(app_label=app_label, model=model)
        except (ValueError, ContentType.DoesNotExist):
            return Response({'error': 'Invalid content_type'}, status=400)

        session_key = self.get_session_key(request)
        reactions = Reaction.objects.filter(content_type=ct, object_id=object_id)
        counts = reactions.values('reaction_type').annotate(count=Count('id'))
        user_reactions = list(reactions.filter(session_key=session_key).values_list('reaction_type', flat=True))

        result = {}
        for item in counts:
            rt = item['reaction_type']
            result[rt] = {'count': item['count'], 'reacted': rt in user_reactions}
        return Response(result)

    def post(self, request):
        content_type_str = request.data.get('content_type')
        object_id = request.data.get('object_id')
        reaction_type = request.data.get('reaction_type')
        if not all([content_type_str, object_id, reaction_type]):
            return Response({'error': 'content_type, object_id, reaction_type required'}, status=400)
        try:
            app_label, model = content_type_str.split('.')
            ct = ContentType.objects.get(app_label=app_label, model=model)
        except (ValueError, ContentType.DoesNotExist):
            return Response({'error': 'Invalid content_type'}, status=400)

        session_key = self.get_session_key(request)
        reaction, created = Reaction.objects.get_or_create(
            content_type=ct, object_id=object_id,
            reaction_type=reaction_type, session_key=session_key
        )
        if not created:
            reaction.delete()
            return Response({'action': 'removed', 'reaction_type': reaction_type})
        return Response({'action': 'added', 'reaction_type': reaction_type})
