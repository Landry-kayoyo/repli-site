from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Subscriber
from .serializers import SubscriberSerializer
import threading


class SubscribeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SubscriberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        name = serializer.validated_data.get('name', '')

        subscriber, created = Subscriber.objects.get_or_create(
            email=email,
            defaults={'name': name, 'status': 'active', 'confirmed': True}
        )

        if not created and subscriber.status == 'unsubscribed':
            subscriber.status = 'active'
            subscriber.save()
            created = True

        if created:
            threading.Thread(
                target=_send_welcome_async,
                args=(email, name),
                daemon=True
            ).start()
            msg = 'Inscription réussie ! Vérifiez votre boîte mail.'
        else:
            msg = 'Vous êtes déjà inscrit(e) à la newsletter.'

        return Response({'success': True, 'message': msg}, status=status.HTTP_200_OK)


def _send_welcome_async(email, name):
    try:
        from .utils import send_welcome_email
        send_welcome_email(subscriber_email=email, subscriber_name=name)
    except Exception:
        pass


class UnsubscribeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.GET.get('token')
        email = request.GET.get('email')
        return self._unsubscribe(token, email)

    def post(self, request):
        token = request.data.get('token') or request.GET.get('token')
        email = request.data.get('email') or request.GET.get('email')
        return self._unsubscribe(token, email)

    def _unsubscribe(self, token, email):
        try:
            if token:
                sub = Subscriber.objects.get(token=token)
            elif email:
                sub = Subscriber.objects.get(email=email)
            else:
                return Response({'success': False, 'message': 'Token ou email requis.'}, status=400)
            sub.status = 'unsubscribed'
            sub.save()
            return Response({'success': True, 'message': 'Désabonnement réussi. Vous ne recevrez plus nos emails.'})
        except Subscriber.DoesNotExist:
            return Response({'success': False, 'message': 'Email non trouvé.'}, status=404)
