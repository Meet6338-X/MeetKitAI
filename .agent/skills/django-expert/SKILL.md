---
name: django-expert
description: Robust Python web development with Django. ORM mastery, DRF patterns, security, and project structure.
---

# Django Expert

> **Goal**: Leverage the "batteries-included" framework to build secure, scalable, and maintainable web applications.

## 1. Project Layout (Two-Scoops Style)

```
config/             # Settings (base.py, local.py, production.py)
    ├── settings/
    ├── urls.py
    └── wsgi.py
apps/               # App directory (keep root clean)
    ├── users/
    ├── catalog/
    └── orders/
requirements/
    ├── base.txt
    └── production.txt
manage.py
```

## 2. ORM Mastery (The Powerhouse)

- **Select Related / Prefetch Related**:  PREVENT N+1 queries.
    - `select_related`: For ForeignKey (SQL JOIN).
    - `prefetch_related`: For ManyToMany (Separate lookup + Python join).
- **Q Objects**: For complex OR queries. `Book.objects.filter(Q(title__startswith='A') | Q(title__startswith='B'))`.
- **F Objects**: For database-level field references. `Product.objects.update(price=F('price') * 1.2)`.
- **Managers**: Encapsulate custom query logic. `User.objects.active_users()`.

## 3. Django Rest Framework (DRF)

- **Serializers**: The single source of truth for API validation.
- **ViewSets**: Use `ModelViewSet` for standard CRUD, `GenericAPIView` for specific logic.
- **Permissions**: Custom permission classes (`IsOwnerOrReadOnly`).
- **Filtering**: Use `django-filter` for robust query params.

## 4. Security Checklist (Production)

- `DEBUG = False`
- `ALLOWED_HOSTS` set correctly.
- `SECRET_KEY` loaded from Environment Variable.
- `SECURE_SSL_REDIRECT = True`
- `CSRF_COOKIE_SECURE = True`
- `SESSION_COOKIE_SECURE = True`

## 5. Performance & Caching

- **Redis**: Use as the cache backend.
- **View Caching**: `@cache_page(60 * 15)` for static public views.
- **Low-level Caching**: `cache.get('key')` / `cache.set('key', value)`.
- **Celery**: Offload ALL sends emails, image resizing, and heavy reports to background workers.

## 6. Deployment

- **Gunicorn**: The WSGI server.
- **Nginx**: Reverse proxy to serve static files and buffer requests.
- **WhiteNoise**: Simple static file serving for effortless PaaS deployment (optional but recommended for smaller apps).
