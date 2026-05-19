from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User
from .serializers import UserSerializer, RegisterSerializer, ChangePasswordSerializer
from activity_logs.services import create_log

class MobileTokenSerializer(TokenObtainPairSerializer):
    username_field = "mobile"

class MobileTokenView(TokenObtainPairView):
    serializer_class = MobileTokenSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = User.objects.filter(mobile=request.data.get("mobile")).first()
        if user:
            create_log(user, "LOGIN", "ACCOUNT", user.id, user.mobile)
        return response

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        create_log(user, "REGISTER", "ACCOUNT", user.id, user.mobile)

class ProfileView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        create_log(request.user, "UPDATE_PROFILE", "ACCOUNT", request.user.id, request.user.mobile)
        return Response(serializer.data)

class ChangePasswordView(APIView):
    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not request.user.check_password(serializer.validated_data["old_password"]):
            return Response({"detail":"Old password invalid"}, status=400)

        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()

        create_log(request.user, "CHANGE_PASSWORD", "ACCOUNT", request.user.id, request.user.mobile)
        return Response({"detail":"Password updated"})
