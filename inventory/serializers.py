from rest_framework import serializers
from .models import Cuboid

class CuboidSerializer(serializers.ModelSerializer):
    def validate(self, data):
        if data['length'] <= 0 or data['breadth'] <= 0 or data['height'] <= 0:
            raise serializers.ValidationError("Length, breadth, and height must be positive values.")
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request', None)
        if request and not request.user.is_staff:
            representation.pop('created_at', None)
            representation.pop('created_by', None)
            representation.pop('updated_at', None)
        return representation

    class Meta:
        model = Cuboid
        fields = ['id', 'length', 'breadth', 'height', 'area', 'volume', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['area', 'volume', 'created_by', 'created_at', 'updated_at']