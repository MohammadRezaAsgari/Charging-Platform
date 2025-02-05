from django.urls import resolve, reverse
from rest_framework.test import APITestCase

from users.api.v1.views import (
    LoginPasswordAPIView,
    UserProfileAPIView,
)
from users.factories import UserFactory
from utils.api.error_objects import ErrorObject


class TestLoginPasswordAPIView(APITestCase):
    def setUp(self):
        self.url = reverse("users:v1:login_password")
        self.username = "roham"
        self.password = "12345"
        self.user_obj = UserFactory(username=self.username, password=self.password)

    def test_login_bad_request(self):
        invalid_data = {"password": self.password}
        response = self.client.post(self.url, invalid_data)
        json_response = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json_response.get("success"), False)
        self.assertEqual(
            json_response.get("error").get("code"), ErrorObject.BAD_REQUEST["code"]
        )
        self.assertEqual(
            json_response.get("error").get("msg"), ErrorObject.BAD_REQUEST["msg"]
        )

    def test_login_not_found(self):
        data = {
            "username": "wrong_username",
            "password": self.password,
        }
        response = self.client.post(self.url, data)
        json_response = response.json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json_response.get("success"), False)
        self.assertEqual(
            json_response.get("error").get("code"), ErrorObject.USER_NOT_FOUND["code"]
        )
        self.assertEqual(
            json_response.get("error").get("msg"), ErrorObject.USER_NOT_FOUND["msg"]
        )

    def test_login_not_activated(self):
        self.user_obj.is_active = False
        self.user_obj.save()
        data = {
            "username": self.user_obj.username,
            "password": self.password,
        }
        response = self.client.post(self.url, data)
        json_response = response.json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json_response.get("success"), False)
        self.assertEqual(
            json_response.get("error").get("code"), ErrorObject.USER_NOT_FOUND["code"]
        )
        self.assertEqual(
            json_response.get("error").get("msg"), ErrorObject.USER_NOT_FOUND["msg"]
        )

    def test_login_successful(self):
        data = {
            "username": self.user_obj.username,
            "password": self.password,
        }
        response = self.client.post(self.url, data)
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_response.get("success"), True)
        self.assertIn("access", json_response.get("data"))
        self.assertIn("refresh", json_response.get("data"))
        self.assertIn("access_token_expires_at", json_response.get("data"))

    def test_resolve_url(self):
        resolver = resolve("/api/v1/auth/login-password/")
        self.assertEqual(resolver.view_name, "users:v1:login_password")
        self.assertEqual(resolver.func.view_class, LoginPasswordAPIView)
        self.assertEqual(resolver.namespace, "users:v1")
        self.assertEqual(resolver.url_name, "login_password")


class TestUserProfileAPIView(APITestCase):
    def setUp(self):
        self.url = reverse("users:v1:user_profile")
        self.username = "roham"
        self.password = "12345"
        self.user_obj = UserFactory(username=self.username, password=self.password)

    def test_user_get_profile_success(self):
        self.client.force_authenticate(user=self.user_obj)
        response = self.client.get(self.url)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json.get("success"), True)
        self.assertEqual(
            response_json.get("data")["first_name"], self.user_obj.first_name
        )
        self.assertEqual(
            response_json.get("data")["last_name"], self.user_obj.last_name
        )

    def test_user_update_profile_success(self):
        self.client.force_authenticate(user=self.user_obj)
        data = {
            "first_name": "updated first name",
            "last_name": "updated last name",
        }
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 204)

    def test_resolve_url(self):
        resolver = resolve(f"/api/v1/auth/me/")
        self.assertEqual(resolver.view_name, "users:v1:user_profile")
        self.assertEqual(resolver.func.view_class, UserProfileAPIView)
        self.assertEqual(resolver.namespace, "users:v1")
        self.assertEqual(resolver.url_name, "user_profile")
