from datetime import timedelta
from django.utils import timezone
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Cuboid
from .serializers import CuboidSerializer
from .permissions import IsStaff, IsCreatorOrStaff
from django.conf import settings
from rest_framework.decorators import action
from rest_framework import viewsets, mixins
from rest_framework.exceptions import MethodNotAllowed


class CuboidViewSet(mixins.CreateModelMixin, 
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    
    queryset = Cuboid.objects.all()
    serializer_class = CuboidSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'my_boxes']:
            return [IsAuthenticated(), IsStaff()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def my_boxes(self, request):
        user_boxes = Cuboid.objects.filter(created_by=request.user)
        serializer = self.get_serializer(user_boxes, many=True)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH')

    def perform_create(self, serializer):
        user = self.request.user

        # Check total boxes added in a week by the user
        one_week_ago = timezone.now() - timedelta(weeks=1)
        user_boxes_this_week = Cuboid.objects.filter(created_by=user, created_at__gte=one_week_ago).count()
        if user_boxes_this_week >= settings.L2:
            return Response({"detail": "You have reached the maximum number of boxes you can add in a week."}, status=status.HTTP_400_BAD_REQUEST)

        # Check total boxes added in a week
        total_boxes_this_week = Cuboid.objects.filter(created_at__gte=one_week_ago).count()
        if total_boxes_this_week >= settings.L1:
            return Response({"detail": "The maximum number of boxes that can be added in a week has been reached."}, status=status.HTTP_400_BAD_REQUEST)

        # Check average volume of boxes added by the user
        user_boxes = Cuboid.objects.filter(created_by=user)
        user_volume_sum = sum(box.volume for box in user_boxes)
        new_box_volume = serializer.validated_data['length'] * serializer.validated_data['breadth'] * serializer.validated_data['height']
        if user_boxes.count() > 0 and (user_volume_sum + new_box_volume) / (user_boxes.count() + 1) > settings.V1:
            return Response({"detail": "The average volume of your boxes exceeds the limit."}, status=status.HTTP_400_BAD_REQUEST)

        # Check average area of all boxes
        all_boxes = Cuboid.objects.all()
        area_sum = sum(box.area for box in all_boxes)
        new_box_area = 2 * (serializer.validated_data['length'] * serializer.validated_data['breadth'] + serializer.validated_data['breadth'] * serializer.validated_data['height'] + serializer.validated_data['height'] * serializer.validated_data['length'])
        if all_boxes.count() > 0 and (area_sum + new_box_area) / (all_boxes.count() + 1) > settings.A1:
            return Response({"detail": "The average area of all boxes exceeds the limit."}, status=status.HTTP_400_BAD_REQUEST)

        # If all checks pass, save the new box
        serializer.save(created_by=user)

    def perform_update(self, serializer):
        user = self.request.user

        # Check average volume of boxes added by the user
        user_boxes = Cuboid.objects.filter(created_by=user)
        user_volume_sum = sum(box.volume for box in user_boxes)
        new_box_volume = serializer.validated_data['length'] * serializer.validated_data['breadth'] * serializer.validated_data['height']
        if user_boxes.count() > 0 and (user_volume_sum + new_box_volume) / (user_boxes.count() + 1) > settings.V1:
            return Response({"detail": "The average volume of your boxes exceeds the limit."}, status=status.HTTP_400_BAD_REQUEST)

        # Check average area of all boxes
        all_boxes = Cuboid.objects.all()
        area_sum = sum(box.area for box in all_boxes)
        new_box_area = 2 * (serializer.validated_data['length'] * serializer.validated_data['breadth'] + serializer.validated_data['breadth'] * serializer.validated_data['height'] + serializer.validated_data['height'] * serializer.validated_data['length'])
        if all_boxes.count() > 0 and (area_sum + new_box_area) / (all_boxes.count() + 1) > settings.A1:
            return Response({"detail": "The average area of all boxes exceeds the limit."}, status=status.HTTP_400_BAD_REQUEST)

        # If all checks pass, save the updated box
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.created_by != request.user:
            return Response({"detail": "Only the creator can delete this box."}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
