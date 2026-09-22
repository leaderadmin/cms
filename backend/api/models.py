from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class RoutePermission(models.Model):
    code = models.CharField(max_length=120, unique=True)
    module = models.CharField(max_length=80)
    route = models.CharField(max_length=160)

    class Meta:
        ordering = ("module", "code")

    def __str__(self):
        return self.code


class Role(models.Model):
    name = models.CharField(max_length=80, unique=True)
    permissions = models.ManyToManyField(RoutePermission, blank=True, related_name="roles")
    users = models.ManyToManyField(User, blank=True, related_name="dynamic_roles")

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Menu(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name", "id")

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="items")
    label = models.CharField(max_length=120)
    href = models.CharField(max_length=255, blank=True)
    view = models.CharField(max_length=80, blank=True)
    icon = models.CharField(max_length=80, default="bi-circle")
    required_permission = models.CharField(max_length=120, blank=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("parent_id", "sort_order", "id")

    def __str__(self):
        return self.label


class SystemSettings(models.Model):
    system_name = models.CharField(max_length=160, default="Startup Backoffice")
    api_domain = models.URLField(max_length=500, blank=True)
    backoffice_domain = models.URLField(max_length=500, blank=True)
    logo_url = models.URLField(max_length=500, blank=True)
    logo_file = models.FileField(upload_to="system/branding", blank=True)
    favicon_url = models.URLField(max_length=500, blank=True)
    description = models.CharField(max_length=255, blank=True)
    website_url = models.URLField(max_length=500, blank=True)
    support_email = models.EmailField(blank=True)
    version = models.CharField(max_length=40, default="1.0.0")
    footer_text = models.CharField(max_length=255, default="operations console")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.system_name


class AuthSession(models.Model):
    session_id = models.UUIDField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auth_sessions")
    refresh_jti = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    @property
    def is_active(self):
        return self.revoked_at is None and self.expires_at > timezone.now()


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_reset_tokens")
    token_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)


class MediaFolder(models.Model):
    name = models.CharField(max_length=120)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="media_folders")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)
        constraints = [models.UniqueConstraint(fields=("parent", "name"), name="unique_media_folder_name")]

    def __str__(self):
        return self.name


class MediaFile(models.Model):
    file = models.FileField(upload_to="media/%Y/%m")
    original_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=160, blank=True)
    size = models.PositiveBigIntegerField(default=0)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="media_files")
    folder = models.ForeignKey(MediaFolder, on_delete=models.SET_NULL, null=True, blank=True, related_name="files")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("-created_at",)), models.Index(fields=("original_name",))]

    def __str__(self):
        return self.original_name


class ArticleCategory(models.Model):
    legacy_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    category_type = models.CharField(max_length=64, default="article")
    status = models.SmallIntegerField(default=1)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="children")
    ordering = models.IntegerField(default=0)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("ordering", "name")

    def __str__(self):
        return self.name


class ArticleCategoryTranslation(models.Model):
    category = models.ForeignKey(ArticleCategory, on_delete=models.CASCADE, related_name="translations")
    legacy_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    language_code = models.CharField(max_length=10)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    url_key = models.CharField(max_length=255, blank=True)
    status = models.SmallIntegerField(default=1)
    meta_keyword = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("category", "language_code"), name="unique_article_category_language")
        ]


class Tag(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Article(models.Model):
    STATUS_DELETED = -1
    STATUS_APPROVED = 1
    STATUS_PENDING = 2
    STATUS_CHOICES = (
        (STATUS_DELETED, "Deleted"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_PENDING, "Pending"),
    )

    legacy_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    article_type = models.CharField(max_length=64, default="article")
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_PENDING)
    view_count = models.PositiveIntegerField(default=0)
    ordering = models.IntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="articles")
    legacy_author_id = models.CharField(max_length=20, blank=True)
    show_home = models.BooleanField(default=False)
    is_feature = models.BooleanField(default=False)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    public_date = models.DateTimeField(null=True, blank=True)
    image = models.ForeignKey(MediaFile, on_delete=models.SET_NULL, null=True, blank=True, related_name="articles")
    legacy_image_id = models.CharField(max_length=20, blank=True)
    categories = models.ManyToManyField(ArticleCategory, blank=True, related_name="articles")
    managed_tags = models.ManyToManyField(Tag, blank=True, related_name="articles")
    tags = models.JSONField(default=list, blank=True)
    cta_label = models.CharField(max_length=80, blank=True)
    cta_url = models.URLField(max_length=500, blank=True)
    cta_phone = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-public_date", "-created_at", "-id")
        indexes = [
            models.Index(fields=("status", "-public_date")),
            models.Index(fields=("article_type", "status")),
        ]

    def __str__(self):
        return self.name


class ArticleTranslation(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="translations")
    legacy_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    language_code = models.CharField(max_length=10)
    title = models.CharField(max_length=255)
    raw_title = models.CharField(max_length=255, blank=True)
    sub_title = models.CharField(max_length=255, blank=True)
    raw_sub_title = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    raw_content = models.TextField(blank=True)
    short_description = models.TextField(blank=True)
    status = models.SmallIntegerField(choices=Article.STATUS_CHOICES, default=Article.STATUS_PENDING)
    public_date = models.DateTimeField(null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="article_translations")
    legacy_author_id = models.CharField(max_length=20, blank=True)
    feature_image = models.ForeignKey(MediaFile, on_delete=models.SET_NULL, null=True, blank=True, related_name="article_translation_images")
    legacy_feature_image_id = models.CharField(max_length=20, blank=True)
    is_featured = models.BooleanField(default=False)
    url_key = models.CharField(max_length=255)
    seo_title = models.CharField(max_length=255, blank=True)
    seo_name = models.CharField(max_length=255, blank=True)
    seo_content = models.TextField(blank=True)
    meta_keyword = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("article", "language_code"), name="unique_article_language")
        ]
        indexes = [
            models.Index(fields=("language_code", "status")),
            models.Index(fields=("url_key", "language_code")),
        ]


class Page(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = (
        (STATUS_DRAFT, "Draft"),
        (STATUS_PUBLISHED, "Published"),
        (STATUS_ARCHIVED, "Archived"),
    )

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    template_key = models.CharField(max_length=120, default="standard-page")
    template = models.ForeignKey("PageTemplate", on_delete=models.SET_NULL, null=True, blank=True, related_name="pages")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    components = models.JSONField(default=list, blank=True)
    published_version = models.ForeignKey("PageVersion", on_delete=models.SET_NULL, null=True, blank=True, related_name="published_pages")
    draft_version = models.ForeignKey("PageVersion", on_delete=models.SET_NULL, null=True, blank=True, related_name="draft_pages")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="pages")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at", "-id")

    def __str__(self):
        return self.name


class PageTemplate(models.Model):
    name = models.CharField(max_length=255)
    key = models.SlugField(max_length=120, unique=True)
    regions = models.JSONField(default=list, blank=True)
    tokens = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=Page.STATUS_CHOICES, default=Page.STATUS_PUBLISHED)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name", "id")

    def __str__(self):
        return self.name


class PageComponent(models.Model):
    name = models.CharField(max_length=255)
    block_name = models.SlugField(max_length=120, unique=True)
    html = models.TextField(blank=True)
    css = models.TextField(blank=True)
    js = models.TextField(blank=True)
    content = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Page.STATUS_CHOICES, default=Page.STATUS_PUBLISHED)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name", "id")

    def __str__(self):
        return self.name


class PageComponentDefinition(models.Model):
    name = models.CharField(max_length=255)
    component_key = models.SlugField(max_length=120, unique=True)
    prehtml = models.TextField(blank=True)
    html = models.TextField(blank=True)
    css = models.TextField(blank=True)
    js = models.TextField(blank=True)
    content = models.TextField(blank=True)
    backhtml = models.TextField(blank=True)
    blocks = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, choices=Page.STATUS_CHOICES, default=Page.STATUS_PUBLISHED)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name", "id")

    def __str__(self):
        return self.name


class PageVersion(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="versions")
    regions = models.JSONField(default=dict, blank=True)
    version_number = models.PositiveIntegerField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="page_versions")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-version_number", "-id")
        constraints = [models.UniqueConstraint(fields=("page", "version_number"), name="unique_page_version_number")]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.FileField(upload_to="users/avatars", blank=True)
    display_name = models.CharField(max_length=160, blank=True)
    job_title = models.CharField(max_length=160, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    location = models.CharField(max_length=160, blank=True)
    bio = models.TextField(blank=True, max_length=1000)
    language = models.CharField(max_length=10, default="en")
    timezone = models.CharField(max_length=80, default="UTC")
    date_format = models.CharField(max_length=40, default="MMM d, yyyy")
    email_notifications = models.BooleanField(default=True)
    security_alerts = models.BooleanField(default=True)
    compact_mode = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)


class ActivityLog(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    level = models.CharField(max_length=16, default="INFO")
    service = models.CharField(max_length=100, default="startup-api")
    module = models.CharField(max_length=80, blank=True)
    environment = models.CharField(max_length=40, default="development")
    host = models.CharField(max_length=255, blank=True)
    message = models.CharField(max_length=255, blank=True)
    trace_id = models.CharField(max_length=128, null=True, blank=True)
    request_id = models.CharField(max_length=128, null=True, blank=True)
    session_id = models.CharField(max_length=128, null=True, blank=True)
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="activity_logs",
    )
    action = models.CharField(max_length=160, blank=True)
    entity_type = models.CharField(max_length=160, blank=True)
    entity_id = models.CharField(max_length=160, null=True, blank=True)
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=255)
    status_code = models.PositiveSmallIntegerField(null=True, blank=True)
    error_code = models.CharField(max_length=120, null=True, blank=True)
    error_type = models.CharField(max_length=120, null=True, blank=True)
    stack_trace = models.TextField(null=True, blank=True)
    changed_fields = models.JSONField(default=list, blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)
    portal_id = models.CharField(max_length=160, null=True, blank=True)
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("-created_at",)),
            models.Index(fields=("user", "-created_at")),
            models.Index(fields=("path", "-created_at")),
        ]


class EmailConfiguration(models.Model):
    provider = models.CharField(max_length=40, default="smtp")
    host = models.CharField(max_length=255, blank=True)
    port = models.PositiveIntegerField(default=587)
    username = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=512, blank=True)
    encryption = models.CharField(max_length=16, default="tls")
    from_name = models.CharField(max_length=160, blank=True)
    from_email = models.EmailField(blank=True)
    reply_to = models.EmailField(blank=True)
    enabled = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Email configuration"


class EmailTemplate(models.Model):
    key = models.SlugField(max_length=120, unique=True)
    name = models.CharField(max_length=160)
    subject = models.CharField(max_length=255)
    html_body = models.TextField(blank=True)
    text_body = models.TextField(blank=True)
    variables = models.JSONField(default=list, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)

