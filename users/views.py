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
        user_identifier = data.get("userid") or data.get("user_id") or data.get("userID")

        if user_identifier:
            return self._update_user(data, user_identifier)

        return self._create_user(data)

    def _create_user(self, data):
        username = data.get("username") or data.get("userName")
        fullname = data.get("fullname") or data.get("fullName")
        profile_id = data.get("profile_id") or data.get("profileID")
        password = data.get("password")
        missing_fields = []
        if not username:
            missing_fields.append("username")
        if not fullname:
            missing_fields.append("fullname")
        if not profile_id:
            missing_fields.append("profile_id")
        if not password:
            missing_fields.append("password")

        if missing_fields:
            return standard_response(
                success=False,
                message="Faltan campos obligatorios",
                data={"fields": missing_fields},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            user = User.objects.create(
                username=username,
                password_hash=hashed.decode('utf-8'),
                fullname=fullname,
                profile_id=profile_id,
                #customer_id=data.get("customer_id"),
                status=data.get("status", True),
                created_by=data.get("created_by") or data.get("createdby") or 1,
                created_at=timezone.now()
            )
            return standard_response(
                success=True,
                message="User created successfully",
                data=UserSerializer(user).data,
                status_code=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def _update_user(self, data, user_identifier):
        try:
            user = User.objects.get(userid=user_identifier)
        except User.DoesNotExist:
            return standard_response(
                success=False,
                message="Usuario no encontrado",
                data=None,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        update_fields = ["updated_at"]
        username = data.get("username") or data.get("userName")
        fullname = data.get("fullname") or data.get("fullName")
        profile_id = data.get("profile_id") or data.get("profileID")

        if username:
            user.username = username
            update_fields.append("username")

        if fullname:
            user.fullname = fullname
            update_fields.append("fullname")

        if profile_id:
            user.profile_id = profile_id
            update_fields.append("profile")

        if "status" in data:
            user.status = data["status"]
            update_fields.append("status")

        if data.get("password"):
            hashed = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt())
            user.password_hash = hashed.decode("utf-8")
            update_fields.append("password_hash")

        updated_by = data.get("updated_by")
        if updated_by is None:
            updated_by = data.get("updatedby")
        if updated_by is not None:
            user.updated_by = updated_by
            update_fields.append("updated_by")

        user.updated_at = timezone.now()

        try:
            user.save(update_fields=update_fields)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

        return standard_response(
            success=True,
            message="User updated successfully",
            data=UserSerializer(user).data,
            status_code=status.HTTP_200_OK,
        )


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


class UpdatePasswordView(APIView):
    def post(self, request):
        user_identifier = (
            request.data.get("userid")
            or request.data.get("user_id")
            or request.data.get("username")
        )
        new_password = request.data.get("new_password") or request.data.get("password")
        updated_by = request.data.get("updated_by")

        if not user_identifier:
            return standard_response(
                success=False,
                message="Debe enviar userid o username",
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if not new_password:
            return standard_response(
                success=False,
                message="Debe enviar la nueva contraseña",
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        filters = {"userid": user_identifier} if str(user_identifier).isdigit() else {"username": user_identifier}

        try:
            user = User.objects.get(**filters)
        except User.DoesNotExist:
            return standard_response(
                success=False,
                message="Usuario no encontrado",
                data=None,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
        user.password_hash = hashed.decode("utf-8")
        user.updated_at = timezone.now()

        if updated_by is not None:
            user.updated_by = updated_by

        user.save(update_fields=["password_hash", "updated_at", "updated_by"])

        return standard_response(
            success=True,
            message="Contraseña actualizada correctamente",
            data=None,
            status_code=status.HTTP_200_OK,
        )
