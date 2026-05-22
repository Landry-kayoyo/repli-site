from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.contenttypes.models import ContentType
from .models import Comment
from .serializers import CommentSerializer


class CommentListCreateView(APIView):
    permission_classes = [AllowAny]

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
        comments = Comment.objects.filter(
            content_type=ct, object_id=object_id,
            is_approved=True, parent=None
        )
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        content_type_str = request.data.get('content_type')
        object_id = request.data.get('object_id')
        if not content_type_str or not object_id:
            return Response({'error': 'content_type and object_id required'}, status=400)
        try:
            app_label, model = content_type_str.split('.')
            ct = ContentType.objects.get(app_label=app_label, model=model)
        except (ValueError, ContentType.DoesNotExist):
            return Response({'error': 'Invalid content_type'}, status=400)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(content_type=ct, object_id=object_id)
            return Response({'success': True, 'message': 'Commentaire soumis et en attente de modération.'}, status=201)
        return Response(serializer.errors, status=400)
