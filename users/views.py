from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView
from .serializers import UserSerializers

class CustomUserDetailsView(RetrieveUpdateAPIView):
    serializer_class = UserSerializers
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_queryset(self):
        return get_user_model().objects.none()
