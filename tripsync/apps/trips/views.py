# from rest_framework.response import Response
# from rest_framework.generics import (
#     ListCreateAPIView,
#     RetrieveUpdateDestroyAPIView,
#     CreateAPIView,
#     DestroyAPIView,
# )
# from rest_framework.permissions import IsAuthenticated
# from apps.trips.permissions import (
#     IsTripOrganizerOrReadOnly,
#     IsTripAdmin,
#     IsTripOrganizer,
# )
# from apps.trips.serializers import (
#     TripSerializer,
#     TripParticipantSerializer,
#     TripJoinRequestActionSerializer,
#     TripJoinRequestSerializer,
# )
# from apps.trips.models import Trip, TripParticipant, TripUserRelation, TripJoinRequest
# from django.db.models import Q
# from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
# from rest_framework import status, generics, permissions, serializers
# from .emails import send_join_request_notification
# from django.core.exceptions import ValidationError


# class TripListCreateView(ListCreateAPIView):
#     serializer_class = TripSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         return Trip.objects.filter(
#             Q(trip_visibility="public")
#             | Q(trip_organizer=user)
#             | Q(participants__user=user)
#         ).distinct()

#     def perform_create(self, serializer):
#         serializer.save(trip_organizer=self.request.user)


# class TripDetailView(RetrieveUpdateDestroyAPIView):
#     queryset = Trip.objects.all()
#     serializer_class = TripSerializer
#     permission_classes = [IsAuthenticated, IsTripOrganizerOrReadOnly]


# class TripParticipantCreateView(CreateAPIView):
#     queryset = TripParticipant.objects.all()
#     serializer_class = TripParticipantSerializer
#     permission_classes = [IsAuthenticated]


# class TripParticipantListView(ListAPIView):
#     serializer_class = TripParticipantSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         trip_id = self.kwargs.get("trip_id")
#         return TripParticipant.objects.filter(trip_id=trip_id)


# class TripParticipantUpdateView(RetrieveUpdateAPIView):
#     queryset = TripParticipant.objects.all()
#     serializer_class = TripParticipantSerializer
#     permission_classes = [IsAuthenticated]


# class TripParticipantDeleteView(DestroyAPIView):
#     queryset = TripParticipant.objects.all()
#     serializer_class = TripParticipantSerializer
#     permission_classes = [IsAuthenticated, IsTripOrganizerOrReadOnly]

#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         instance.delete()
#         # Return a custom response
#         return Response(
#             {"message": "Trip participant deleted successfully!"},
#             status=status.HTTP_200_OK,
#         )


# # 1. Submit a Trip Join Request
# class TripJoinRequestCreateView(generics.CreateAPIView):
#     queryset = TripJoinRequest.objects.all()
#     serializer_class = TripJoinRequestSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def perform_create(self, serializer):
#         try:
#             join_request = serializer.save()
#             send_join_request_notification(join_request)  # Notify trip admin via email
#         except ValidationError as e:
#             raise serializers.ValidationError(e.message_dict)


# # 2. Approve/Reject Join Request (Trip Admins only)
# class TripJoinRequestActionView(generics.UpdateAPIView):
#     queryset = TripJoinRequest.objects.all()
#     serializer_class = TripJoinRequestActionSerializer
#     permission_classes = [IsAuthenticated, IsTripOrganizer]

#     def get_queryset(self):
#         return TripJoinRequest.objects.filter(status="pending")


# class TripJoinRequestDetailView(generics.UpdateAPIView):
#     queryset = TripJoinRequest.objects.all()
#     serializer_class = TripJoinRequestActionSerializer
#     permission_classes = [permissions.IsAuthenticated, IsTripOrganizer]

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveUpdateAPIView,
    UpdateAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics, permissions, serializers
from django.db.models import Q
from django.core.exceptions import ValidationError

from apps.trips.permissions import (
    IsTripOrganizerOrReadOnly,
    IsTripAdmin,
    IsTripOrganizer,
    IsTripAdminOrParticipant
)
from apps.trips.serializers import (
    TripSerializer,
    TripParticipantSerializer,
    TripJoinRequestActionSerializer,
    TripJoinRequestSerializer,
    TripPublicPreviewSerializer
)
from apps.trips.models import Trip, TripParticipant, TripJoinRequest
from .emails import send_join_request_notification
from uuid import UUID
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

class TripListCreateView(ListCreateAPIView):
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Trip.objects.filter(
            Q(trip_visibility="public") |
            Q(trip_organizer=user) |
            Q(participants__user=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(trip_organizer=self.request.user)


class TripDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated, IsTripOrganizerOrReadOnly]


class TripParticipantCreateView(CreateAPIView):
    queryset = TripParticipant.objects.all()
    serializer_class = TripParticipantSerializer
    permission_classes = [IsAuthenticated, IsTripAdmin]


class TripParticipantListView(ListAPIView):
    serializer_class = TripParticipantSerializer
    permission_classes = [IsAuthenticated, IsTripAdminOrParticipant]

    def get_queryset(self):
        trip_id = self.kwargs.get("trip_id")
        return TripParticipant.objects.filter(trip_id=trip_id)


class TripParticipantUpdateView(RetrieveUpdateAPIView):
    queryset = TripParticipant.objects.all()
    serializer_class = TripParticipantSerializer
    permission_classes = [IsAuthenticated, IsTripAdmin]


class TripParticipantDeleteView(DestroyAPIView):
    queryset = TripParticipant.objects.all()
    serializer_class = TripParticipantSerializer
    permission_classes = [IsAuthenticated, IsTripAdmin]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"message": "Trip participant deleted successfully!"},
            status=status.HTTP_200_OK,
        )


class TripJoinRequestCreateView(generics.CreateAPIView):
    queryset = TripJoinRequest.objects.all()
    serializer_class = TripJoinRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        try:
            join_request = serializer.save()
            send_join_request_notification(join_request)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)


class TripJoinRequestActionView(UpdateAPIView):
    queryset = TripJoinRequest.objects.filter(status="pending")
    serializer_class = TripJoinRequestActionSerializer
    permission_classes = [IsAuthenticated, IsTripAdmin]


class TripJoinRequestDetailView(UpdateAPIView):
    queryset = TripJoinRequest.objects.all()
    serializer_class = TripJoinRequestActionSerializer
    permission_classes = [IsAuthenticated, IsTripAdmin]


class TripPreviewAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            uuid_token = UUID(token, version=4)
        except ValueError:
            return Response({"detail": "Invalid token format."}, status=400)

        trip = Trip.objects.filter(public_token=uuid_token, is_public=True).first()
        if not trip:
            return Response({"detail": "Trip not found or is not public."}, status=404)

        serializer = TripPublicPreviewSerializer(trip)
        return Response(serializer.data)
    
class CancelJoinRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, request_id):
        join_request = get_object_or_404(TripJoinRequest, id=request_id)

        if join_request.user != request.user:
            return Response({"detail": "Not allowed to cancel this request."}, status=403)

        if join_request.status != 'pending':
            return Response({"detail": "Only pending requests can be canceled."}, status=400)

        join_request.delete()
        return Response({"detail": "Join request canceled."}, status=204)