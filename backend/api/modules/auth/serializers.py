from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.urls import reverse
from rest_framework import serializers

from ...models import AuthSession, Menu, MenuItem, Role, RoutePermission, UserProfile


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        role, _ = Role.objects.get_or_create(name="user")
        role.permissions.set(
            RoutePermission.objects.filter(
                code__in=("auth.me.read", "dashboard.stats.read", "auth.sessions.read")
            )
        )
        role.users.add(user)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["current_password"]):
            raise serializers.ValidationError({"current_password": "Current password is incorrect."})
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        if attrs["current_password"] == attrs["new_password"]:
            raise serializers.ValidationError({"new_password": "New password must be different."})
        validate_password(attrs["new_password"], user)
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(min_length=32, max_length=128)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        validate_password(attrs["new_password"])
        return attrs


class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    session_id = serializers.UUIDField()
    refresh_expires_at = serializers.DateTimeField()
    user = serializers.DictField()


class UserRoleSerializer(serializers.Serializer):
    roles = serializers.ListField(child=serializers.CharField(), min_length=0)


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "email", "is_staff", "roles", "permissions", "avatar_url")

    def get_avatar_url(self, user):
        profile = getattr(user, "profile", None)
        return reverse("auth-profile-avatar", kwargs={"user_id": user.id}) if profile and profile.avatar else ""

    def get_roles(self, user):
        return list(user.dynamic_roles.values_list("name", flat=True))

    def get_permissions(self, user):
        return sorted(
            user.dynamic_roles.values_list("permissions__code", flat=True).distinct()
        )


class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", required=False)
    username = serializers.CharField(source="user.username", read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ("username", "email", "avatar_url", "display_name", "job_title", "phone", "location", "bio", "timezone", "date_format", "email_notifications", "security_alerts", "compact_mode")

    def get_avatar_url(self, profile):
        return reverse("auth-profile-avatar", kwargs={"user_id": profile.user_id}) if profile.avatar else ""

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        if "email" in user_data:
            instance.user.email = user_data["email"]
            instance.user.save(update_fields=("email",))
        return super().update(instance, validated_data)


class UserAdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    email = serializers.EmailField(required=True, allow_blank=False)
    roles = serializers.SerializerMethodField()
    display_name = serializers.CharField(required=False, allow_blank=True, default="")
    job_title = serializers.CharField(required=False, allow_blank=True, default="")
    phone = serializers.CharField(required=False, allow_blank=True, max_length=40, default="")
    location = serializers.CharField(required=False, allow_blank=True, default="")
    bio = serializers.CharField(required=False, allow_blank=True, max_length=1000, default="")

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "is_active",
            "is_staff",
            "roles",
            "date_joined",
            "last_login",
            "display_name",
            "job_title",
            "phone",
            "location",
            "bio",
        )
        read_only_fields = ("id", "is_staff", "date_joined", "last_login")

    def get_roles(self, user):
        return list(user.dynamic_roles.values_list("name", flat=True))

    def to_representation(self, instance):
        data = super().to_representation(instance)
        profile = getattr(instance, "profile", None)
        if profile is not None:
            data.update({
                "display_name": profile.display_name,
                "job_title": profile.job_title,
                "phone": profile.phone,
                "location": profile.location,
                "bio": profile.bio,
            })
        return data

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        if not password:
            raise serializers.ValidationError({"password": "This field is required."})
        profile_data = {field: validated_data.pop(field, "") for field in ("display_name", "job_title", "phone", "location", "bio")}
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        profile_data = {field: validated_data.pop(field, None) for field in ("display_name", "job_title", "phone", "location", "bio")}
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save(update_fields=("password",))
        profile, _ = UserProfile.objects.get_or_create(user=user)
        changed_profile_fields = []
        for field, value in profile_data.items():
            if value is not None:
                setattr(profile, field, value)
                changed_profile_fields.append(field)
        if changed_profile_fields:
            profile.save(update_fields=changed_profile_fields + ["updated_at"])
        return user


class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.SlugRelatedField(
        many=True,
        slug_field="code",
        queryset=RoutePermission.objects.all(),
    )

    class Meta:
        model = Role
        fields = ("id", "name", "permissions")


class RoutePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutePermission
        fields = ("id", "code", "module", "route")


class MenuItemSerializer(serializers.ModelSerializer):
    menu_id = serializers.PrimaryKeyRelatedField(
        source="menu",
        queryset=Menu.objects.all(),
    )
    parent_id = serializers.PrimaryKeyRelatedField(
        source="parent",
        queryset=MenuItem.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = MenuItem
        fields = (
            "id",
            "menu_id",
            "label",
            "href",
            "view",
            "icon",
            "required_permission",
            "parent_id",
            "sort_order",
            "is_active",
        )
        read_only_fields = ("id",)

    def validate(self, attrs):
        parent = attrs.get("parent", getattr(self.instance, "parent", None))
        menu = attrs.get("menu", getattr(self.instance, "menu", None))
        required_permission = str(attrs.get("required_permission", getattr(self.instance, "required_permission", ""))).strip()
        if required_permission and not RoutePermission.objects.filter(code=required_permission).exists():
            raise serializers.ValidationError({"required_permission": "Permission does not exist."})
        if parent and parent.menu_id != menu.id:
            raise serializers.ValidationError({"parent_id": "A menu item must have a parent in the same menu."})
        if self.instance and (parent == self.instance or self.instance in self._descendants(parent)):
            raise serializers.ValidationError({"parent_id": "A menu item cannot be nested under itself or its descendants."})
        return attrs

    def _descendants(self, item):
        if item is None:
            return MenuItem.objects.none()
        descendants = MenuItem.objects.filter(parent=item)
        for child in list(descendants):
            descendants = descendants | self._descendants(child)
        return descendants


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ("id", "name", "slug", "is_active")
        read_only_fields = ("id",)

class AuthSessionSerializer(serializers.ModelSerializer):
    active = serializers.ReadOnlyField(source="is_active")

    class Meta:
        model = AuthSession
        fields = (
            "session_id",
            "created_at",
            "last_seen_at",
            "expires_at",
            "revoked_at",
            "user_agent",
            "ip_address",
            "active",
        )
