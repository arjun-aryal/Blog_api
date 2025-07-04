
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404



from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser,FormParser
from rest_framework.exceptions import NotFound


from .exceptions import CantFollowYourself
from .pagination import ProfilePagination
from .renderers import ProfileJSONRenderer, ProfilesJSONRenderer 
from .serializers import ProfileSerializer, UpdateProfileSerializer,FollowingSerializer
from .models import Profile



User = get_user_model()

class ProfileListAPIView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    pagination_class = ProfilePagination
    # renderer_classes = [ProfilesJSONRenderer]


class ProfileDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    # renderer_classes = [ProfileJSONRenderer]

    def get_queryset(self):
        queryset = Profile.objects.select_related("user")
        return queryset

    def get_object(self):
        user = self.request.user
        profile = self.get_queryset().get(user=user)
        return profile


class UpdateProfileAPIView(generics.RetrieveAPIView):
    serializer_class = UpdateProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser,FormParser]
    # renderer_classes = [ProfileJSONRenderer]

    def get_object(self):
        profile = self.request.user.profile
        return profile

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            profile = Profile.objects.get(user__id=request.user.id)
            follower_profiles = profile.followers.all()
            serializer = FollowingSerializer(follower_profiles, many=True)
            formatted_response = {
                "status_code": status.HTTP_200_OK,
                "followers_count": follower_profiles.count(),
                "followers": serializer.data,
            }
            return Response(formatted_response, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response(status=404)


class FollowingListView(APIView):
    def get(self, request, user_id, format=None):
        try:
            profile = Profile.objects.get(user__id=user_id)
            following_profiles = profile.following.all()
            users = [p.user for p in following_profiles]
            serializer = FollowingSerializer(users, many=True)
            formatted_response = {
                "status_code": status.HTTP_200_OK,
                "following_count": following_profiles.count(),
                "users_i_follow": serializer.data,
            }
            return Response(formatted_response, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response(status=404)


class FollowAPIView(APIView):
    def post(self, request, user_id, format=None):
        try:
            follower = Profile.objects.get(user=self.request.user)
            user_profile = request.user.profile
            profile = Profile.objects.get(user__id=user_id)
            if profile == follower:
                raise CantFollowYourself

            if user_profile.check_following(profile):
                formatted_response = {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": f"You are already following {profile.user.first_name} {profile.user.last_name}",
                }
                return Response(formatted_response, status=status.HTTP_400_BAD_REQUEST)

            user_profile.follow(profile)
            subject = "Some is following you."
            message = f"hi there, {profile.user.first_name}!!, the user {user_profile.user.first_name} {user_profile.user.last_name} is now following you."
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [profile.user.email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=True)
            return Response(
                {
                    "status_code": status.HTTP_200_OK,
                    "message": f"You are now following {profile.user.first_name} {profile.user.last_name}",
                },
            )
        except Profile.DoesNotExist:
            raise NotFound("You can't follow a profile that doesn't exist.")


class UnfollowAPIView(APIView):
    def post(self, request, user_id, format=None):
        user_profile = request.user.profile
        # profile = Profile.objects.get(user__id=user_id)
        profile = get_object_or_404(Profile, user__id=user_id)

        if not user_profile.check_following(profile):
            formatted_response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": f"You can't unfollow {profile.user.first_name} {profile.user.last_name}, since you were not following them.",
            }
            return Response(
                formatted_response,
                status.HTTP_400_BAD_REQUEST,
            )

        user_profile.unfollow(profile)
        formatted_response = {
            "status_code": status.HTTP_200_OK,
            "message": f"You have unfollowed {profile.user.first_name} {profile.user.last_name}.",
        }
        return Response(formatted_response, status.HTTP_200_OK)
