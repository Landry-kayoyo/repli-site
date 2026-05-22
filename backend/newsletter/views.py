from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Subscriber
from .serializers import SubscriberSerializer


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

        msg = 'Inscription réussie!' if created else 'Vous êtes déjà inscrit.'
        return Response({'success': True, 'message': msg}, status=status.HTTP_200_OK)


class UnsubscribeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email') or request.GET.get('email')
        token = request.data.get('token') or request.GET.get('token')
        try:
            if token:
                sub = Subscriber.objects.get(token=token)
            else:
                sub = Subscriber.objects.get(email=email)
            sub.status = 'unsubscribed'
            sub.save()
            return Response({'success': True, 'message': 'Désabonnement réussi.'})
        except Subscriber.DoesNotExist:
            return Response({'success': False, 'message': 'Email non trouvé.'}, status=404)
