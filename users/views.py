# views.py
import bcrypt
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from utils.responses import standard_response
from .models import User, Profile
from .serializers import UserSerializer


class UserListView(APIView):
    def get(self, request):
        profile = request.query_params.get("profile")
        users = User.objects.select_related("profile")

        if profile and profile.strip():
            if not profile.strip().isdigit():
                return standard_response(
                    success=False,
                    message="El parámetro 'profile' debe ser numérico",
                    data=None,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            users = users.filter(profile_id=profile.strip())

        serializer = UserSerializer(users.order_by("userid"), many=True)
        return standard_response(
            success=True,
            message="Usuarios obtenidos correctamente",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

class RegisterUserView(APIView):
    def post(self, request):
        data = request.data
        password = data.get("password")
        if not password:
            return Response({"error": "Password is required"}, status=400)

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            user = User.objects.create(
                username=data["username"],
                password_hash=hashed.decode('utf-8'),
                fullname=data["fullname"],
                profile_id=data["profile_id"],
                #customer_id=data.get("customer_id"),
                status=True,
                created_by=1,
                created_at=timezone.now()
            )
            #return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
            return standard_response(
            success=True,
            message="User created successfully",
            status_code=status.HTTP_200_OK
        )
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class LoginUserView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        try:
            user = User.objects.select_related('profile').get(username=username)
        except User.DoesNotExist:
            #return Response({"error": "Invalid username or password"}, status=400)
            return standard_response(
                success=False,
                message="Invalid username or password",
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            user_data ={
                "fullname": user.fullname,
                "profileID": user.profile.profileid,
                "profileName": user.profile.profilename,
                #"id" : user.customer.id,
                #"type" : user.customer.type
            }
            return standard_response(
                success=True,
                message="Login successful",
                data=user_data,
                status_code=status.HTTP_200_OK
            )
        else:
            #return Response({"error": "Invalid username or password"}, status=400)
            return standard_response(
                success=False,
                message="Invalid username or password",
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST
            )
