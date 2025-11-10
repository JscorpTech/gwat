from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.db import connection


class ClientSerializer(serializers.Serializer):
    name = serializers.CharField()
    logo = serializers.ImageField()


class UserSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()

    def get_client(self, obj):
        instance = connection.tenant
        if instance is None:
            return None
        return ClientSerializer(instance=instance, context=self.context).data

    class Meta:
        exclude = ["created_at", "updated_at", "password", "groups", "user_permissions"]
        model = get_user_model()


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name"]
