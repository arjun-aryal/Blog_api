from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializers(serializers.Serializer):
    
    class Meta:
        model= User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
        ]
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.is_superuser:
            representation["admin"]=True
        return representation