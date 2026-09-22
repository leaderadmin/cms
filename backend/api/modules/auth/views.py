from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.conf import settings
from django.http import FileResponse
from mimetypes import guess_type
from django.core.mail import EmailMessage, get_connection
from smtplib import SMTPException
from django.utils import timezone
from datetime import timedelta
import hashlib
import secrets
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenViewBase
from drf_spectacular.utils import OpenApiExample, extend_schema

from ...models import AuthSession, EmailConfiguration, Menu, MenuItem, PasswordResetToken, Role, RoutePermission, UserProfile
from .permissions import (
    AUTH_ME,
    AUTH_MENU_CREATE,
    AUTH_MENU_DELETE,
    AUTH_MENU_READ,
    AUTH_MENU_UPDATE,
    AUTH_PERMISSIONS_READ,
    AUTH_ROLES_CREATE,
    AUTH_ROLES_DELETE,
    AUTH_ROLES_READ,
    AUTH_ROLES_UPDATE,
    AUTH_SESSIONS_READ,
    AUTH_SESSIONS_REVOKE,
    AUTH_USERS_ASSIGN_ROLE,
    AUTH_USERS_CREATE,
    AUTH_USERS_READ,
    AUTH_USERS_UPDATE,
    HasRoutePermission,
)
from .serializers import (
    AuthSessionSerializer,
    ChangePasswordSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    LoginSerializer,
    MenuItemSerializer,
    MenuSerializer,
    RegisterSerializer,
    RoleSerializer,
    RoutePermissionSerializer,
    TokenResponseSerializer,
    UserRoleSerializer,
    UserSerializer,
    UserProfileSerializer,
    UserAdminSerializer,
)


def send_configured_email(subject, body, recipient):
    config = EmailConfiguration.objects.first()
    if not config or not config.enabled or not config.host or not config.from_email:
        raise SMTPException("Email configuration is incomplete or disabled")
    connection = get_connection(
        host=config.host,
        port=config.port,
        username=config.username,
        password=config.password,
        use_tls=config.encryption == "tls",
        use_ssl=config.encryption == "ssl",
        fail_silently=False,
    )
    EmailMessage(
        subject,
        body,
        config.from_email,
        [recipient],
        connection=connection,
        headers={"Reply-To": config.reply_to} if config.reply_to else None,
    ).send()
from .sessions import create_session, revoke_session, token_expiry
from .token_serializers import SessionTokenRefreshSerializer
from ..audit.context import set_activity_context


def token_response(user, request):
    session, refresh = create_session(user, request)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "session_id": str(session.session_id),
        "refresh_expires_at": token_expiry(refresh).isoformat(),
        "user": UserSerializer(user).data,
    }


@extend_schema(request=SessionTokenRefreshSerializer, responses=TokenResponseSerializer)
class SessionTokenRefreshView(TokenViewBase):
    serializer_class = SessionTokenRefreshSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_register"

    @extend_schema(
        request=RegisterSerializer,
        responses={201: TokenResponseSerializer},
        examples=[
            OpenApiExample(
                "Register",
                request_only=True,
                value={"username": "demo-user", "email": "demo@example.test", "password": "DemoUser123!"},
            ),
            OpenApiExample(
                "Register response",
                response_only=True,
                value={
                    "access": "<access-token>",
                    "refresh": "<refresh-token>",
                    "session_id": "00000000-0000-0000-0000-000000000000",
                    "refresh_expires_at": "2026-09-23T12:00:00Z",
                    "user": {"id": 1, "username": "demo-user", "roles": ["user"]},
                },
            ),
        ],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(token_response(user, request), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_login"

    @extend_schema(
        request=LoginSerializer,
        responses=TokenResponseSerializer,
        examples=[
            OpenApiExample(
                "Login",
                request_only=True,
                value={"username": "demo-user", "password": "DemoUser123!"},
            ),
            OpenApiExample(
                "Login response",
                response_only=True,
                value={
                    "access": "<access-token>",
                    "refresh": "<refresh-token>",
                    "session_id": "00000000-0000-0000-0000-000000000000",
                    "refresh_expires_at": "2026-09-23T12:00:00Z",
                    "user": {"id": 1, "username": "demo-user", "roles": ["user"]},
                },
            ),
        ],
    )
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"detail": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        set_activity_context(request, action="auth.login", entity_type="User", tags=["auth", "login"])
        return Response(token_response(user, request))


class MeView(APIView):
    permission_classes = [HasRoutePermission]
    required_permission = AUTH_ME

    @extend_schema(
        responses=UserSerializer,
        examples=[
            OpenApiExample(
                "Current user",
                response_only=True,
                value={
                    "id": 1,
                    "username": "demo-user",
                    "email": "demo-user@example.test",
                    "is_staff": False,
                    "roles": ["user"],
                    "permissions": ["auth.me.read", "dashboard.stats.read"],
                },
            )
        ],
    )
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class UserProfileView(APIView):
    permission_classes = [HasRoutePermission]
    required_permission = AUTH_ME

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        return Response(UserProfileSerializer(profile).data)

    def patch(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(UserProfileSerializer(serializer.save()).data)


class UserAvatarView(APIView):
    permission_classes = []

    def get(self, request, user_id=None):
        if user_id is None:
            return Response({"detail": "Avatar user is required."}, status=status.HTTP_404_NOT_FOUND)
        profile = UserProfile.objects.filter(user_id=user_id).first()
        if not profile or not profile.avatar:
            return Response({"detail": "No avatar has been uploaded."}, status=status.HTTP_404_NOT_FOUND)
        return FileResponse(profile.avatar.open("rb"), content_type=guess_type(profile.avatar.name)[0] or "application/octet-stream")

    def post(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        avatar = request.FILES.get("avatar")
        if not avatar:
            return Response({"detail": "An avatar file is required."}, status=status.HTTP_400_BAD_REQUEST)
        if avatar.content_type not in {"image/png", "image/jpeg", "image/gif", "image/webp"}:
            return Response({"detail": "Avatar must be a PNG, JPG, GIF, or WEBP image."}, status=status.HTTP_400_BAD_REQUEST)
        if avatar.size > 5 * 1024 * 1024:
            return Response({"detail": "Avatar must be smaller than 5 MB."}, status=status.HTTP_400_BAD_REQUEST)
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.avatar = avatar
        profile.save(update_fields=("avatar",))
        return Response(UserProfileSerializer(profile).data)

class ChangePasswordView(APIView):
    permission_classes = [HasRoutePermission]
    required_permission = AUTH_ME

    @extend_schema(request=ChangePasswordSerializer, responses={204: None})
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=("password",))
        current_session_id = request.auth.get("sid")
        for session in AuthSession.objects.filter(user=request.user, revoked_at__isnull=True).exclude(session_id=current_session_id):
            revoke_session(session)
        set_activity_context(request, action="auth.password.changed", entity_type="User", entity_id=request.user.id)
        email_sent = False
        if request.user.email:
            try:
                send_configured_email(
                    "Your Startup password was changed",
                    f"Hello {request.user.username},\n\nYour password was changed successfully. If you did not make this change, contact an administrator immediately.",
                    request.user.email,
                )
                email_sent = True
            except (OSError, SMTPException):
                pass
        return Response({
            "detail": "Password changed successfully.",
            "email_sent": email_sent,
            "email": request.user.email or None,
        })


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_password_reset"

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(
            username=serializer.validated_data["username"],
            email__iexact=serializer.validated_data["email"],
            is_active=True,
        ).first()
        if user is None or not user.email:
            return Response(
                {"detail": "Username or email is incorrect. Please verify both values."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw_token = secrets.token_urlsafe(48)
        PasswordResetToken.objects.filter(user=user, used_at__isnull=True).update(used_at=timezone.now())
        PasswordResetToken.objects.create(
            user=user,
            token_hash=hashlib.sha256(raw_token.encode()).hexdigest(),
            expires_at=timezone.now() + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_MINUTES),
        )
        reset_url = f"{settings.BACKOFFICE_URL}/?reset_token={raw_token}"
        try:
            send_configured_email(
                "Reset your Startup password",
                f"Hello {user.username},\n\nThis password reset is for account: {user.username} ({user.email}).\n\nUse this confirmation token to reset your password:\n\n{raw_token}\n\nYou can also open: {reset_url}\n\nThis token expires in {settings.PASSWORD_RESET_TOKEN_MINUTES} minutes.",
                user.email,
            )
        except (OSError, SMTPException):
            PasswordResetToken.objects.filter(token_hash=hashlib.sha256(raw_token.encode()).hexdigest()).delete()
            return Response({"detail": "The email service is currently unavailable. Please try again later."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({"detail": f"Reset token sent to {user.email}."})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_password_confirm"

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_hash = hashlib.sha256(serializer.validated_data["token"].encode()).hexdigest()
        reset = PasswordResetToken.objects.select_related("user").filter(
            token_hash=token_hash, used_at__isnull=True, expires_at__gt=timezone.now(), user__is_active=True,
        ).first()
        if reset is None:
            return Response({"detail": "The reset token is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)
        reset.user.set_password(serializer.validated_data["new_password"])
        reset.user.save(update_fields=("password",))
        reset.used_at = timezone.now()
        reset.save(update_fields=("used_at",))
        for session in AuthSession.objects.filter(user=reset.user, revoked_at__isnull=True):
            revoke_session(session)
        return Response({
            "detail": "Password reset successfully.",
            "username": reset.user.username,
            "email": reset.user.email,
        })


class RoleListCreateView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": AUTH_ROLES_READ, "POST": AUTH_ROLES_CREATE}

    @extend_schema(responses=RoleSerializer(many=True))
    def get(self, request):
        self.required_permission = AUTH_ROLES_READ
        return Response(RoleSerializer(Role.objects.all(), many=True).data)

    @extend_schema(request=RoleSerializer, responses={201: RoleSerializer})
    def post(self, request):
        self.required_permission = AUTH_ROLES_CREATE
        serializer = RoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            RoleSerializer(serializer.save()).data,
            status=status.HTTP_201_CREATED,
        )


class PermissionListView(APIView):
    permission_classes = [HasRoutePermission]
    required_permission = AUTH_PERMISSIONS_READ

    @extend_schema(responses=RoutePermissionSerializer(many=True))
    def get(self, request):
        return Response(RoutePermissionSerializer(RoutePermission.objects.all(), many=True).data)


class MenuListCreateView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": AUTH_MENU_READ, "POST": AUTH_MENU_CREATE}

    @extend_schema(responses=MenuItemSerializer(many=True))
    def get(self, request):
        self.required_permission = AUTH_MENU_READ
        items = MenuItem.objects.filter(is_active=True)
        menu_id = request.query_params.get("menu_id")
        if menu_id:
            items = items.filter(menu_id=menu_id)
        else:
            items = items.filter(menu__slug="main")
        return Response(MenuItemSerializer(items, many=True).data)

    @extend_schema(request=MenuItemSerializer, responses={201: MenuItemSerializer})
    def post(self, request):
        self.required_permission = AUTH_MENU_CREATE
        serializer = MenuItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(MenuItemSerializer(serializer.save()).data, status=status.HTTP_201_CREATED)


class MenuGroupListCreateView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": AUTH_MENU_READ, "POST": AUTH_MENU_CREATE}

    def get(self, request):
        self.required_permission = AUTH_MENU_READ
        return Response(MenuSerializer(Menu.objects.filter(is_active=True), many=True).data)

    def post(self, request):
        self.required_permission = AUTH_MENU_CREATE
        serializer = MenuSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(MenuSerializer(serializer.save()).data, status=status.HTTP_201_CREATED)


class MenuGroupDetailView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"PATCH": AUTH_MENU_UPDATE, "DELETE": AUTH_MENU_DELETE}

    def get_object(self, menu_id):
        try:
            return Menu.objects.get(pk=menu_id)
        except Menu.DoesNotExist:
            return None

    def patch(self, request, menu_id):
        self.required_permission = AUTH_MENU_UPDATE
        menu = self.get_object(menu_id)
        if menu is None:
            return Response({"detail": "Menu not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = MenuSerializer(menu, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(MenuSerializer(serializer.save()).data)

    def delete(self, request, menu_id):
        self.required_permission = AUTH_MENU_DELETE
        menu = self.get_object(menu_id)
        if menu is None:
            return Response({"detail": "Menu not found."}, status=status.HTTP_404_NOT_FOUND)
        menu.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MenuDetailView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"PATCH": AUTH_MENU_UPDATE, "DELETE": AUTH_MENU_DELETE}

    def get_object(self, menu_id):
        try:
            return MenuItem.objects.get(pk=menu_id)
        except MenuItem.DoesNotExist:
            return None

    def patch(self, request, menu_id):
        self.required_permission = AUTH_MENU_UPDATE
        item = self.get_object(menu_id)
        if item is None:
            return Response({"detail": "Menu item not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = MenuItemSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(MenuItemSerializer(serializer.save()).data)

    def delete(self, request, menu_id):
        self.required_permission = AUTH_MENU_DELETE
        item = self.get_object(menu_id)
        if item is None:
            return Response({"detail": "Menu item not found."}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoleDetailView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"PATCH": AUTH_ROLES_UPDATE, "DELETE": AUTH_ROLES_DELETE}

    def get_object(self, role_id):
        try:
            return Role.objects.get(pk=role_id)
        except Role.DoesNotExist:
            return None

    @extend_schema(request=RoleSerializer, responses=RoleSerializer)
    def patch(self, request, role_id):
        self.required_permission = AUTH_ROLES_UPDATE
        role = self.get_object(role_id)
        if role is None:
            return Response({"detail": "Role not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = RoleSerializer(role, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(RoleSerializer(serializer.save()).data)

    def delete(self, request, role_id):
        self.required_permission = AUTH_ROLES_DELETE
        role = self.get_object(role_id)
        if role is None:
            return Response({"detail": "Role not found."}, status=status.HTTP_404_NOT_FOUND)
        role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserAdminListCreateView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": AUTH_USERS_READ, "POST": AUTH_USERS_CREATE}

    @extend_schema(responses=UserAdminSerializer(many=True))
    def get(self, request):
        self.required_permission = AUTH_USERS_READ
        query = request.query_params.get("q", "").strip()
        users = User.objects.select_related("profile").prefetch_related("dynamic_roles").order_by("username")
        if query:
            users = users.filter(username__icontains=query) | users.filter(email__icontains=query)
        return Response(UserAdminSerializer(users, many=True).data)

    @extend_schema(request=UserAdminSerializer, responses={201: UserAdminSerializer})
    def post(self, request):
        self.required_permission = AUTH_USERS_CREATE
        serializer = UserAdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        set_activity_context(request, action="auth.user.created", entity_type="User", entity_id=user.id)
        return Response(UserAdminSerializer(user).data, status=status.HTTP_201_CREATED)


class UserAdminDetailView(APIView):
    permission_classes = [HasRoutePermission]
    required_permission = AUTH_USERS_UPDATE

    def patch(self, request, user_id):
        self.required_permission = AUTH_USERS_UPDATE
        try:
            user = User.objects.select_related("profile").get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserAdminSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_user = serializer.save()
        set_activity_context(
            request,
            action="auth.user.updated",
            entity_type="User",
            entity_id=user.id,
            changed_fields=list(request.data.keys()),
        )
        return Response(UserAdminSerializer(updated_user).data)


class UserRoleView(APIView):
    permission_classes = [HasRoutePermission]
    required_permission = AUTH_USERS_ASSIGN_ROLE

    @extend_schema(request=UserRoleSerializer, responses=UserAdminSerializer)
    def post(self, request, user_id):
        role_names = request.data.get("roles", [])
        if not isinstance(role_names, list) or any(not isinstance(role, str) for role in role_names):
            return Response(
                {"detail": "roles must be a list of role names."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        roles = list(Role.objects.filter(name__in=role_names))
        if len(roles) != len(set(role_names)):
            return Response(
                {"detail": "One or more roles do not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.dynamic_roles.set(roles)
        return Response(UserAdminSerializer(user).data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={204: None})
    def post(self, request):
        set_activity_context(request, action="auth.logout", entity_type="AuthSession", tags=["auth", "logout"])
        session_id = request.auth.get("sid")
        session = AuthSession.objects.filter(
            session_id=session_id,
            user=request.user,
        ).first()
        if session:
            revoke_session(session)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SessionListView(APIView):
    permission_classes = [HasRoutePermission]
    required_permission = AUTH_SESSIONS_READ

    @extend_schema(responses=AuthSessionSerializer(many=True))
    def get(self, request):
        sessions = AuthSession.objects.filter(user=request.user)
        return Response(AuthSessionSerializer(sessions, many=True).data)


class SessionRevokeView(APIView):
    permission_classes = [HasRoutePermission]
    required_permission = AUTH_SESSIONS_REVOKE

    @extend_schema(responses={204: None})
    def post(self, request, session_id):
        session = AuthSession.objects.filter(
            session_id=session_id,
            user=request.user,
        ).first()
        if session is None:
            return Response(
                {"detail": "Session not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        revoke_session(session)
        return Response(status=status.HTTP_204_NO_CONTENT)
