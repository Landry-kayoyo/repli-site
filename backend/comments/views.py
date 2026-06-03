from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.contenttypes.models import ContentType
from .models import Comment
from .serializers import CommentSerializer
import threading


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
            comment = serializer.save(content_type=ct, object_id=object_id, is_approved=True)
            # Send email notification to admin in background
            threading.Thread(
                target=_notify_admin_new_comment,
                args=(comment, request),
                daemon=True
            ).start()
            return Response({'success': True, 'message': 'Commentaire publié !', 'comment': serializer.data}, status=201)
        return Response(serializer.errors, status=400)


def _notify_admin_new_comment(comment, request):
    try:
        from core.models import SiteSettings
        from newsletter.utils import _build_smtp_connection
        from django.core.mail import EmailMultiAlternatives

        s = SiteSettings.objects.first()
        if not s:
            return
        admin_email = s.contact_email or s.author_email or s.email_host_user
        if not admin_email or not s.email_host_user or not s.email_host_password:
            return

        # Determine content URL
        try:
            ct = comment.content_type
            obj = ct.get_object_for_this_type(pk=comment.object_id)
            content_url = request.build_absolute_uri(f'/{ct.app_label}/{obj.slug}/')
            content_title = getattr(obj, 'title', str(obj))
        except Exception:
            content_url = request.build_absolute_uri('/')
            content_title = 'une publication'

        subject = f'💬 Nouveau commentaire — {comment.author_name}'
        html = f"""
        <div style="font-family:-apple-system,Arial,sans-serif;max-width:560px;margin:0 auto;background:#f8fafc;padding:32px 16px;">
          <div style="background:#fff;border-radius:12px;padding:32px;box-shadow:0 2px 12px rgba(79,70,229,.08);">
            <div style="text-align:center;margin-bottom:24px;">
              <span style="font-size:2rem;">💬</span>
              <h2 style="color:#1e293b;margin:8px 0 4px;">Nouveau commentaire</h2>
              <p style="color:#64748b;font-size:14px;margin:0;">sur <strong>{content_title}</strong></p>
            </div>
            <div style="background:#f1f5f9;border-radius:8px;padding:16px 20px;margin-bottom:20px;border-left:4px solid #4f46e5;">
              <p style="margin:0 0 8px;font-size:13px;color:#64748b;">
                <strong>De :</strong> {comment.author_name} ({comment.author_email or 'email non fourni'})
              </p>
              <p style="margin:0;color:#1e293b;font-size:15px;line-height:1.6;">{comment.content}</p>
            </div>
            <div style="text-align:center;">
              <a href="{content_url}" style="display:inline-block;background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;text-decoration:none;padding:12px 28px;border-radius:8px;font-weight:600;font-size:14px;">
                Voir la publication →
              </a>
            </div>
          </div>
        </div>
        """

        conn = _build_smtp_connection(s)
        msg = EmailMultiAlternatives(
            subject=subject,
            body=comment.content,
            from_email=f'{s.site_name} <{s.email_host_user}>',
            to=[admin_email],
            connection=conn,
        )
        msg.attach_alternative(html, 'text/html')
        msg.send()
    except Exception:
        pass
