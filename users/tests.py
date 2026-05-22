import bcrypt

from django.db import connection
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITransactionTestCase

from .models import Profile, User


@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
)
class RegisterUserViewTests(APITransactionTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(Profile)
            schema_editor.create_model(User)

    @classmethod
    def tearDownClass(cls):
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(User)
            schema_editor.delete_model(Profile)
        super().tearDownClass()

    def setUp(self):
        User.objects.all().delete()
        Profile.objects.all().delete()
        self.profile = Profile.objects.create(
            profilename="Administrador",
            status=True,
            created_by=1,
        )

    def test_post_register_creates_user_when_userid_is_not_sent(self):
        response = self.client.post(
            reverse("user-register"),
            {
                "username": "admin",
                "fullname": "Usuario Admin",
                "profile_id": self.profile.profileid,
                "password": "secret",
                "created_by": 2,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "User created successfully")
        self.assertEqual(response.data["data"]["userName"], "admin")

        user = User.objects.get(username="admin")
        self.assertTrue(
            bcrypt.checkpw("secret".encode("utf-8"), user.password_hash.encode("utf-8"))
        )

    def test_post_register_updates_user_when_userid_is_sent(self):
        user = User.objects.create(
            username="admin",
            password_hash=bcrypt.hashpw(
                "secret".encode("utf-8"),
                bcrypt.gensalt(),
            ).decode("utf-8"),
            fullname="Usuario Admin",
            profile=self.profile,
            status=True,
            created_by=1,
        )

        response = self.client.post(
            reverse("user-register"),
            {
                "userID": user.userid,
                "userName": "admin2",
                "fullName": "Usuario Actualizado",
                "status": False,
                "updated_by": 9,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "User updated successfully")

        user.refresh_from_db()
        self.assertEqual(user.username, "admin2")
        self.assertEqual(user.fullname, "Usuario Actualizado")
        self.assertFalse(user.status)
        self.assertEqual(user.updated_by, 9)
