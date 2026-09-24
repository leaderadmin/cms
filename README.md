# Django + AngularJS + Angular + Redis Starter

The workspace contains four independent application repositories:

```text
backend/      # Django API repository
frontend/     # legacy AngularJS frontend repository
cron_service/ # standalone Python cron repository
backoffice/   # modern Angular Backoffice repository
```

## Run

```bash
docker compose up --build
```

Open:

- Frontend: http://localhost:8080
- Backoffice Angular: http://localhost:4200
- API health: http://localhost:8000/api/health/
- API stats: http://localhost:8000/api/stats/
- Swagger UI: http://localhost:8000/api/docs/
- OpenAPI schema: http://localhost:8000/api/schema/
- ReDoc: http://localhost:8000/api/redoc/

### GitHub Pages preview

The `main` branch deploys the Backoffice shell to GitHub Pages through
`.github/workflows/deploy-backoffice-pages.yml`:

```text
https://leaderadmin.github.io/cms/
```

GitHub Pages only serves the Angular static bundle. Django API, PostgreSQL,
Redis, authentication, and CRUD operations still require the Docker Compose
environment or a separate backend deployment.

The API uses PostgreSQL in Docker. PostgreSQL data is stored in the
`postgres_data` Docker volume and is available at `postgres:5432` from the API
container. Running Django directly without `DB_ENGINE=postgresql` keeps using
the local SQLite file at `backend/db.sqlite3`.

### Authentication

The API uses JWT authentication. Registering a user assigns the `user` role by
default. The `stats` endpoint requires an access token.

```text
POST /api/auth/register/       # create a user and receive access/refresh tokens
POST /api/auth/login/          # receive access/refresh tokens
POST /api/auth/token/refresh/  # renew an access token
POST /api/auth/logout/         # revoke the current session
GET  /api/auth/me/             # current user, roles and permissions
GET  /api/auth/sessions/       # list current user's sessions
POST /api/auth/sessions/<id>/revoke/ # revoke one session
GET  /api/auth/roles/           # list dynamic roles
POST /api/auth/roles/           # create role and assign declared permissions
POST /api/auth/users/<id>/roles/ # assign one or more roles to a user
GET  /api/auth/users/             # list users (optional ?q= search)
POST /api/auth/users/             # create a user
PATCH /api/auth/users/<id>/       # update email, password or active status

### Activity logs

The API stores activity logs in the PostgreSQL `api_activitylog` table. Every
`/api/` request is recorded after completion, except Swagger/schema routes. A
log contains a structured event envelope: `timestamp`, `level`, `service`,
`module`, `environment`, `host`, `message`, request/trace/session IDs,
`action`, `entity_type`, `entity_id`, error details, changed fields, tags and
the authenticated user. The EspoCRM-style HTTP aliases (`http_method`,
`http_path`, `http_status`, `user_id`, `user_name`) are returned alongside the
legacy fields (`method`, `path`, `status_code`, `username`) for compatibility.
Request bodies are not stored, so passwords and tokens are not written to the
audit table.

Administrators can query the logs with:

```text
GET /api/audit/logs/?limit=50
GET /api/audit/logs/?path=/api/auth/&status_code=401
GET /api/audit/logs/?action=dashboard.stats.read&level=INFO
```

Route-based actions are generated automatically. Domain views can provide
more specific metadata with `set_activity_context(request, action=..., module=...,
entity_type=..., entity_id=..., tags=..., changed_fields=...)`, allowing events
such as `gift_warehouse.allocation_template_requested` to be classified without
storing request bodies.

The endpoint requires the `audit.logs.read` route permission, which is assigned
to the demo `admin` role by `seed_auth_demo`.
```

Send the access token on protected requests:

```text
Authorization: Bearer <access-token>
```

JWT/session settings are configurable through environment variables on the API
container:

```text
JWT_ACCESS_TOKEN_LIFETIME_SECONDS=900       # 15 minutes
JWT_REFRESH_TOKEN_LIFETIME_SECONDS=604800   # 7 days
AUTH_MAX_SESSIONS=5                         # active sessions per user
DJANGO_CACHE_URL=redis://redis:6379/1       # throttle/cache Redis database
API_RATE_LIMIT_ANON=100/hour                # default unauthenticated limit
API_RATE_LIMIT_USER=1000/hour               # default authenticated limit
API_RATE_LIMIT_LOGIN=5/minute               # login attempts per client IP
API_RATE_LIMIT_REGISTER=10/hour             # registration attempts per IP
API_RATE_LIMIT_PASSWORD_RESET=5/hour        # reset requests per IP
API_RATE_LIMIT_PASSWORD_CONFIRM=10/hour     # reset confirmations per IP
API_RATE_LIMIT_MEDIA_UPLOAD=30/hour        # media upload requests per user
MEDIA_MAX_UPLOAD_BYTES=26214400             # 25 MiB per file
MEDIA_ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,webp,pdf,txt,csv,doc,docx,xls,xlsx,ppt,pptx,zip
```

The Backoffice login form includes `Keep me signed in on this device`. When
selected, the JWT response is persisted in `localStorage`; otherwise it stays
in `sessionStorage` and is cleared when the browser session ends. The API rate
limits use Redis-backed DRF throttling and return HTTP 429 when exceeded.

Refresh tokens use rotation and blacklist. Each refresh request returns a new
refresh token and invalidates the previous one. Logging out revokes the session
and immediately invalidates its access token through the session check.

The Backoffice Media library supports authenticated upload, listing, download,
and deletion through `/api/media/`. File metadata is stored in Django and file
content is stored under `MEDIA_ROOT` (the `media_data` Docker volume in Compose).
Uploaded files are not served anonymously; downloads require the `media.read`
permission. Grant `media.upload` and `media.delete` for the corresponding actions.

Create or reset the local demo database data with:

```bash
docker compose exec api python manage.py migrate
docker compose exec api python manage.py seed_auth_demo
```

Demo credentials:

```text
demo-admin   / DemoAdmin123!
demo-user    / DemoUser123!
demo-support / DemoSupport123!
```

Create the first administrative user inside the API container with
`docker compose exec api python manage.py createsuperuser`. Roles are dynamic
database records. Route permissions are declared centrally at the top of each
feature module, for example `api/modules/dashboard/permissions.py`, and cannot
be invented through the role API.

Create a role with route permissions:

```json
POST /api/auth/roles/
{
	"name": "report-reader",
	"permissions": ["dashboard.stats.read"]
}
```

The separate `cron` container runs the standalone Python job from `cron_service/` every five minutes and stores its last execution in Redis. The API does not own or execute the cron source code. Run it manually with:

```bash
docker compose exec cron python run_cron_job.py
```

The cron service is organized independently from the API:

```text
cron_service/
├── services.py                 # scheduled-job logic
├── redis_repository.py         # cron persistence boundary
├── run_cron_job.py             # Python entrypoint
├── Dockerfile
└── cron.txt                   # five-minute schedule
```

Stop services with `docker compose down`. Add `-v` only when you also want to delete Redis and PostgreSQL data.

## Module structure

The backend follows a Django MVC-style module boundary:

```text
backend/api/modules/dashboard/
├── redis_repository.py  # Redis persistence boundary
├── services.py          # application/business logic
├── serializers.py       # response shaping
├── views.py             # HTTP controllers
└── urls.py              # module routes

backend/api/modules/auth/
├── permissions.py       # auth permission registry and route checker
├── serializers.py       # user and registration payloads
├── views.py             # register, login, profile and role assignment
└── urls.py              # authentication routes

backend/api/modules/dashboard/
└── permissions.py       # dashboard route permission declarations

backend/api/modules/audit/
├── permissions.py       # audit log route permission
├── serializers.py        # audit log response shaping
├── views.py              # audit log query endpoint
└── urls.py               # audit routes

backend/api/middleware.py # records completed API activity in PostgreSQL
```

The frontend follows the same feature-module idea:

```text
frontend/modules/dashboard/
├── dashboard.module.js
├── dashboard.service.js      # API client
├── dashboard.controller.js   # view controller
└── dashboard.template.html   # view template
```

The Backoffice Angular app is built and served by the `backoffice` Compose service on port `4200`. It has its own `package.json`, Dockerfile, Nginx configuration and `.git` repository boundary.

Ứng dụng Angular hiện đại được tách thành project/repository riêng:

```text
backoffice/
├── src/app/app.ts            # Backoffice component
├── src/app/app.html          # Backoffice view
├── src/app/app.css
└── Dockerfile
```

The dashboard is Redis-backed and has no relational domain entities, so its persistence layer is represented by `redis_repository.py` rather than Django models.
