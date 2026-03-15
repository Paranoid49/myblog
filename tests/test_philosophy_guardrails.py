from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import DEFAULT_SQLITE_URL, settings
from app.core.error_codes import (
    INVALID_CREDENTIALS,
    SETUP_ALREADY_INITIALIZED,
    SETUP_DATABASE_BOOTSTRAP_FAILED,
    SETUP_MIGRATION_FAILED,
    SETUP_PASSWORD_MISMATCH,
)
from app.main import app
from app.models.site_settings import SiteSettings
from app.routes.api_v1_auth import router as auth_router
from app.routes.api_v1_media import IMAGE_EXTENSION_BY_TYPE, IMAGE_MAX_BYTES, IMAGE_RULES
from app.routes.api_v1_posts import router as posts_router
from app.routes.api_v1_setup import router as setup_router
from app.routes.api_v1_taxonomy import router as taxonomy_router
from app.schemas.api_response import error_response, ok_response
from app.services.setup_service import clear_initialized_cache


def test_default_database_stays_sqlite_baseline() -> None:
    assert DEFAULT_SQLITE_URL.startswith("sqlite:///")
    assert settings.__class__.model_fields["database_url"].default == DEFAULT_SQLITE_URL


def test_login_endpoint_keeps_form_contract(client: TestClient, initialized_site, admin_user) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "secret123"},
    )

    assert response.status_code == 422


def test_login_endpoint_still_accepts_form_submission(client: TestClient, initialized_site, admin_user) -> None:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "secret123"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["message"] == "ok"
    assert set(payload.keys()) == {"code", "message", "data"}


def test_invalid_login_uses_unified_api_response_shape(client: TestClient, initialized_site, admin_user) -> None:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "wrong"},
    )

    assert response.status_code == 401
    payload = response.json()
    assert payload == {"code": INVALID_CREDENTIALS, "message": "invalid_credentials", "data": None}


def test_ok_response_keeps_unified_shape() -> None:
    response = ok_response({"value": 1}, status_code=201)

    assert response.status_code == 201
    assert response.body == b'{"code":0,"message":"ok","data":{"value":1}}'


def test_error_response_keeps_unified_shape() -> None:
    response = error_response("failed", 400, 9999)

    assert response.status_code == 400
    assert response.body == b'{"code":9999,"message":"failed","data":null}'


def test_media_rules_keep_single_authority() -> None:
    assert IMAGE_RULES["max_bytes"] == IMAGE_MAX_BYTES
    assert IMAGE_RULES["extension_by_type"] is IMAGE_EXTENSION_BY_TYPE
    assert IMAGE_EXTENSION_BY_TYPE["image/gif"] == ".gif"


def test_auth_route_keeps_form_fields_declared() -> None:
    login_route = next(route for route in auth_router.routes if route.path == "/api/v1/auth/login")
    body_params = {param.name for param in login_route.dependant.body_params}

    assert body_params == {"username", "password"}


def test_setup_route_keeps_unified_response_shape(client) -> None:
    response = client.get('/api/v1/setup/status')

    assert response.status_code == 200
    payload = response.json()
    assert set(payload.keys()) == {'code', 'message', 'data'}
    assert payload['code'] == 0
    assert payload['message'] == 'ok'


def test_setup_route_uses_registered_error_code_constants(client) -> None:
    mismatch = client.post(
        '/api/v1/setup',
        json={
            'blog_title': '我的博客',
            'username': 'admin',
            'password': 'secret123',
            'confirm_password': 'wrong',
        },
    )

    assert mismatch.status_code == 400
    assert mismatch.json()['code'] == SETUP_PASSWORD_MISMATCH


def test_setup_router_keeps_expected_paths_registered() -> None:
    setup_paths = {route.path for route in setup_router.routes}

    assert '/api/v1/setup/status' in setup_paths
    assert '/api/v1/setup' in setup_paths


def test_setup_error_codes_keep_single_authority() -> None:
    assert SETUP_PASSWORD_MISMATCH == 2001
    assert SETUP_DATABASE_BOOTSTRAP_FAILED == 2002
    assert SETUP_MIGRATION_FAILED == 2003
    assert SETUP_ALREADY_INITIALIZED == 2004


def test_site_settings_keeps_minimal_boundary_fields() -> None:
    assert SiteSettings.__tablename__ == 'site_settings'
    field_names = set(SiteSettings.__table__.columns.keys())
    assert field_names == {
        'id',
        'blog_title',
        'author_name',
        'author_bio',
        'author_email',
        'author_avatar',
        'author_link',
        'created_at',
        'updated_at',
    }


def test_main_app_keeps_auth_router_registered() -> None:
    paths = {route.path for route in app.routes}
    assert "/api/v1/auth/login" in paths
    assert "/api/v1/auth/logout" in paths


def test_posts_router_keeps_admin_and_public_boundaries_registered() -> None:
    post_paths = {route.path for route in posts_router.routes}
    assert '/api/v1/posts' in post_paths
    assert '/api/v1/posts/{slug}' in post_paths
    assert '/api/v1/admin/posts' in post_paths
    assert '/api/v1/admin/posts/import-markdown' in post_paths
    assert '/api/v1/admin/posts/{post_id}/publish' in post_paths
    assert '/api/v1/admin/posts/{post_id}/unpublish' in post_paths


def test_taxonomy_router_keeps_public_query_and_admin_create_boundaries() -> None:
    taxonomy_paths = {route.path for route in taxonomy_router.routes}
    assert '/api/v1/categories/{slug}' in taxonomy_paths
    assert '/api/v1/tags/{slug}' in taxonomy_paths
    assert '/api/v1/taxonomy' in taxonomy_paths
    assert '/api/v1/admin/categories' in taxonomy_paths
    assert '/api/v1/admin/tags' in taxonomy_paths


def test_core_regression_suite_keeps_high_value_commands_documented() -> None:
    content = Path('docs/engineering/core-regression-suite.md').read_text(encoding='utf-8')
    assert 'tests/test_philosophy_guardrails.py' in content
    assert 'tests/test_api_v1_auth.py' in content
    assert 'tests/test_api_v1_posts.py' in content
    assert 'tests/test_admin_posts.py' in content
    assert 'tests/test_hook_bus.py' in content
    assert 'tests/test_extension_loader.py' in content
    assert 'tests/test_database_provider.py' in content


def test_docs_readme_keeps_single_source_document_governance() -> None:
    content = Path('docs/README.md').read_text(encoding='utf-8')
    assert '新增文档前，先判断现有文档是否可以补充' in content
    assert '只保存历史材料' in content


def test_long_term_guardrails_keep_hotspot_monitoring_targets_documented() -> None:
    content = Path('docs/engineering/engineering-guardrails.md').read_text(encoding='utf-8')
    assert 'app/routes/api_v1_posts.py' in content
    assert 'frontend/src/admin/hooks/useAdminPostsState.js' in content
    assert '触发收口' in content
