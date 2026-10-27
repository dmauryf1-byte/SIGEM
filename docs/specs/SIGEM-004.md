# SIGEM-004 — Usuarios y autenticación (JWT + RBAC)

- **Estado:** borrador, pendiente de aprobación del humano
- **Rama:** `feat/SIGEM-004-auth-jwt-rbac` (sobre `main`, con SIGEM-003 mergeada)
- **Depende de:** SIGEM-003 · **Bloquea a:** SIGEM-005 en adelante
- **Módulo crítico (auth):** `/codex:review` + `/codex:adversarial-review` + `/claude-security` (scan changes, esfuerzo high)

## Objetivo

Que solo entren a SIGEM usuarios registrados, con su rol. El login de SIGEM-003 pasa a ser real: usuario y contraseña se validan en el backend, la sesión vive en cookies `HttpOnly`, cada endpoint sabe quién llama y con qué rol, y el sidebar muestra el usuario real.

El éxito se demuestra así: con un administrador creado por consola, se entra por `http://localhost:8000/`, el dashboard muestra su nombre y "Cerrar sesión" invalida la sesión en el servidor; sin sesión, `dashboard.html` devuelve al login y `/api/v1/auth/me` da `401`.

### Fuera de alcance
- Pantalla "Usuarios" (crear, editar, desactivar o desbloquear desde la web): tarea nueva **SIGEM-017**, después de esta. Mientras tanto, los usuarios se crean y desbloquean por consola.
- Recuperación de contraseña por correo (fuera de v1, PLAN.md).
- Doble factor (2FA).

## Decisiones

| Decisión | Elegido | Descartado y por qué |
|---|---|---|
| Primer administrador | Comando de consola `uv run python -m app.scripts.users create --role Administrador` que pide la contraseña sin mostrarla | Usuario fijo en una migración o en `.env`: contraseña conocida o en texto plano (decisión del humano 2026-10-27) |
| Duración de la sesión | **Acceso 15 min** (JWT en cookie) + **renovación con tope absoluto de 1 día** desde el login: pasado ese día hay que volver a entrar aunque se esté usando | 7 días: una sesión abierta en un equipo compartido queda usable mucho tiempo (decisión del humano 2026-10-27) |
| Inactividad | Cada token de renovación dura **30 min** y se reemplaza al usarse: si nadie usa SIGEM entre 15 y 30 min, la sesión se cierra sola | Solo el tope de 1 día: un equipo desatendido seguiría abierto todo el día (propuesta de Claude; mismo motivo que pidió el humano) |
| Bloqueo por intentos | **5 fallos seguidos → cuenta bloqueada 15 min** (OWASP); se desbloquea sola, o antes con el comando `unlock` | Bloqueo permanente: cualquiera podría dejar sin acceso a un usuario a propósito escribiendo mal 5 veces (decisión del humano 2026-10-27) |
| Contraseñas | Argon2id (`argon2-cffi`); mínimo 12 caracteres, sin reglas de "mayúscula + símbolo" (guía OWASP / NIST 800-63B) | bcrypt: corta a 72 bytes; reglas de composición: llevan a contraseñas predecibles |
| Tokens | `PyJWT` (HS256) para el acceso; renovación = valor aleatorio opaco guardado **solo como hash** en `refresh_tokens`, rotado en cada uso; reutilizar uno ya usado revoca toda la sesión | JWT también para la renovación: no se puede revocar al cerrar sesión |
| Cookies | `sigem_access` (path `/api`) y `sigem_refresh` (path `/api/v1/auth`): `HttpOnly`, `SameSite=Strict`, `Secure` configurable (`COOKIE_SECURE`, `false` en local por http) | `localStorage`: prohibido (AGENTS.md §5.7) |
| CSRF | `SameSite=Strict` + el backend solo acepta JSON en los `POST` | Token CSRF aparte: innecesario con `SameSite=Strict` y mismo origen |
| Mensaje de error | Usuario inexistente y contraseña mala dan el mismo `401` "Usuario o contraseña incorrectos", con el mismo tiempo de respuesta (se verifica contra un hash señuelo) | Mensajes distintos: revelan qué usuarios existen |
| Roles | `Administrador` y `Vendedor` (enum en BD). `require_role("Administrador")` en el backend; el frontend solo oculta opciones | Permisos finos por acción: no hay requisito todavía |

## Contrato de API (`/api/v1/auth`)

| Método y ruta | Entrada | Respuesta |
|---|---|---|
| `POST /login` | `{ "username", "password" }` | `200` + `{ user }` y pone las dos cookies · `401 invalid_credentials` · `423 account_locked` ("Cuenta bloqueada temporalmente. Intenta de nuevo en 15 minutos o pide al administrador que la desbloquee.") · `422` validación |
| `POST /refresh` | cookie `sigem_refresh` | `200` + cookies nuevas · `401 session_expired` (borra cookies) |
| `POST /logout` | cookies | `204`, revoca la renovación en BD y borra cookies |
| `GET /me` | cookie `sigem_access` | `200` + `{ id, username, full_name, role }` · `401 not_authenticated` |

Usuario desactivado (`is_active = false`): no puede entrar, y su renovación deja de funcionar.

## Estructura

```
backend/app/
  core/security.py              # hash/verify Argon2, crear/leer JWT, generar token opaco + hash
  core/config.py                # + jwt_secret (SecretStr, obligatorio), cookie_secure
  modules/users/                # models.py (User), repository.py, service.py (crear, buscar, bloqueo, unlock)
  modules/auth/                 # router.py, schemas.py, service.py (login/refresh/logout),
                                # repository.py + models.py (RefreshToken), dependencies.py (get_current_user, require_role)
  scripts/users.py              # CLI: create, unlock
alembic/versions/0001_users_y_refresh_tokens.py   # revisada a mano
frontend/js/shared/api.js       # fetch con cookies; ante 401 intenta /refresh una vez y si falla va al login
frontend/js/shared/auth.js      # currentUser(), logout()
frontend/js/login.js            # envía el login y muestra 401/423 en un alert-error
frontend/js/dashboard.js        # usuario real desde /auth/me
```

Tablas: `users` (`id`, `username` único, `full_name`, `password_hash`, `role`, `is_active`, `failed_login_attempts`, `locked_until`, `created_at`, `updated_at`) y `refresh_tokens` (`id`, `user_id` FK, `token_hash` único, `session_started_at`, `expires_at`, `revoked_at`, `created_at`).

## Estrategia de tests

| Nivel | Qué cubre |
|---|---|
| Unit (pytest) | Hash y verificación Argon2; JWT vencido o alterado se rechaza; política de contraseña (11 caracteres falla, 12 pasa) |
| Integración (pytest + MySQL `sigem_test`) | Login ok pone cookies `HttpOnly`/`SameSite=Strict`; usuario inexistente = contraseña mala (mismo código y mensaje); 5 fallos → `423`, y al pasar 15 min (reloj inyectado) vuelve a entrar; un éxito reinicia el contador; `unlock` desbloquea; usuario inactivo no entra; refresh rota el token y el viejo ya no sirve; reutilizar un refresh usado revoca la sesión; refresh tras 30 min sin uso → `401`; refresh tras 1 día desde el login → `401` aunque haya actividad; logout revoca; `/me` sin cookie → `401`; `require_role` da `403` al Vendedor |
| Unit (Vitest) | `api.js`: ante `401` llama a `/refresh` una sola vez y reintenta; si el refresh falla, redirige al login |
| E2E (Playwright) | Login real con un usuario creado por el CLI → dashboard con su nombre; credenciales malas muestran el error; "Cerrar sesión" → login, y volver a `dashboard.html` regresa al login |

## Límites

- **Siempre:** contraseñas y tokens nunca en logs, respuestas ni Git; `JWT_SECRET` solo en `.env` (y documentado en `.env.example` sin valor real).
- **Preguntar antes:** cualquier dependencia fuera de `argon2-cffi` y `pyjwt`.
- **Nunca:** token en `localStorage`; mensaje que diga si el usuario existe; `# type: ignore`.

## Criterios de aceptación

1. `uv run python -m app.scripts.users create` crea un usuario pidiendo la contraseña dos veces sin mostrarla; rechaza menos de 12 caracteres y usuarios repetidos.
2. Login real desde la web; el sidebar y la barra superior muestran el nombre y el rol del usuario.
3. Sesión: acceso de 15 min renovado solo; se cierra tras ~30 min sin uso y siempre a 1 día del login.
4. 5 fallos seguidos bloquean 15 min con el mensaje `423`; `uv run python -m app.scripts.users unlock <usuario>` desbloquea al momento.
5. "Cerrar sesión" invalida la sesión en el servidor (el refresh viejo da `401`).
6. Endpoints protegidos dan `401` sin sesión y `403` con rol insuficiente.
7. Migración Alembic revisada a mano; `alembic upgrade head` y `downgrade -1` funcionan.
8. Comandos de AGENTS.md §7 en verde (cobertura ≥ 80 % en los `service.py`); Codex review + adversarial y `/claude-security` atendidos. Salida en el PR.
9. AGENTS.md §8 y PLAN.md actualizados (incluye SIGEM-017 Usuarios).

## Preguntas abiertas

- **Inactividad de ~30 min:** propuesta de Claude para el riesgo que señaló el humano. ¿Se aprueba, o solo el tope de 1 día?

## Plan de subtareas (un commit cada una)

1. Dependencias + `core/security.py` con tests unitarios.
2. Modelos `User` y `RefreshToken` + migración 0001 + `conftest` que migra `sigem_test`.
3. `users` service/repository + CLI `create`/`unlock` con tests.
4. `auth` login con bloqueo y mensaje uniforme (TDD).
5. `auth` refresh/logout/me + `get_current_user`/`require_role` (TDD).
6. Frontend: `api.js`, `auth.js`, login real y dashboard con usuario real (Vitest).
7. E2E, documentación (`.env.example`, AGENTS.md §8, PLAN.md) y verificación completa.
