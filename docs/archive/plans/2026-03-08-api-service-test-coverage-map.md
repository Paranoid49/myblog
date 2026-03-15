# API/Service 测试覆盖映射（执行完成）

> 日期：2026-03-08
> 目标：确保每个 HTTP 接口与每个 service 公开函数至少有主路径+关键失败/边界路径测试

## Route Endpoint Mapping

| Endpoint | Method | 主路径测试 | 失败/边界测试 | 状态 |
|---|---|---|---|---|
| `/health` | GET | `test_health_route_exists` | `test_health_route_rejects_post_method` | 完成 |
| `/` | GET | `test_home_displays_database_blog_title_when_initialized` | `test_home_redirects_to_setup_when_uninitialized` / `test_home_redirects_to_setup_when_target_database_does_not_exist` | 完成 |
| `/posts/{slug}` | GET | `test_post_detail_uses_slug_route` | `test_post_detail_returns_404_for_missing_slug` | 完成 |
| `/categories/{slug}` | GET | `test_category_page_lists_posts` | `test_category_page_returns_404_for_missing_slug` | 完成 |
| `/tags/{slug}` | GET | `test_tag_page_lists_posts` | `test_tag_page_returns_404_for_missing_slug` | 完成 |
| `/setup` | GET | `test_setup_page_is_available_when_uninitialized` / `test_setup_page_is_available_when_target_database_does_not_exist` | `test_setup_page_redirects_home_when_initialized` | 完成 |
| `/setup` | POST | `test_setup_submission_initializes_site_and_redirects_to_admin_posts` | `test_setup_submission_rejects_password_mismatch` / `test_setup_submission_shows_generic_error_when_bootstrap_fails` | 完成 |
| `/admin/login` | GET | `test_admin_login_page_renders` | `test_admin_login_redirects_to_setup_when_uninitialized` | 完成 |
| `/admin/login` | POST | `test_admin_login_sets_session` | `test_admin_login_rejects_invalid_password` | 完成 |
| `/admin/logout` | GET | `test_admin_logout_clears_session` | `test_admin_logout_clears_session`（登出后访问受保护页重定向） | 完成 |
| `/admin/posts` | GET | `test_admin_post_list_renders_after_login` | `test_admin_posts_redirects_to_setup_when_uninitialized` / `test_admin_post_list_requires_login` | 完成 |
| `/admin/posts/new` | GET | `test_admin_new_post_page_renders` | `test_admin_new_post_page_requires_login` | 完成 |
| `/admin/posts/new` | POST | `test_admin_can_create_post` | `test_admin_create_post_requires_login` | 完成 |
| `/admin/posts/{post_id}/edit` | GET | `test_edit_post_page_renders_existing_data` | `test_edit_post_page_returns_404_for_missing_post` | 完成 |
| `/admin/posts/{post_id}/edit` | POST | `test_admin_can_edit_post` | `test_admin_edit_post_returns_404_for_missing_post` | 完成 |

## Service Function Mapping

| Module | Function | 主路径测试 | 失败/边界测试 | 状态 |
|---|---|---|---|---|
| `auth_service.py` | `authenticate_user` | `test_authenticate_user_returns_user_for_valid_credentials` | `test_authenticate_user_returns_none_for_wrong_password` / `test_authenticate_user_returns_none_for_inactive_user` / `test_authenticate_user_returns_none_for_missing_user` | 完成 |
| `auth_service.py` | `build_admin_user` | `test_build_admin_user_hashes_password` | `test_build_admin_user_hashes_password`（断言非明文 + 可验证） | 完成 |
| `database_bootstrap_service.py` | `build_maintenance_database_url` | `test_build_maintenance_database_url_replaces_target_database_name` | `test_build_maintenance_database_url_rejects_non_postgresql_url` / `test_build_maintenance_database_url_preserves_real_password_for_engine_connection` | 完成 |
| `database_bootstrap_service.py` | `ensure_database_exists` | `test_ensure_database_exists_skips_create_when_database_already_exists` / `test_ensure_database_exists_creates_database_when_missing` | `test_ensure_database_exists_wraps_create_failures` | 完成 |
| `migration_service.py` | `upgrade_database` | `test_upgrade_database_calls_alembic_upgrade` | `test_upgrade_database_uses_project_root_alembic_ini_when_cwd_changes` / `test_upgrade_database_uses_absolute_script_location_when_cwd_changes` | 完成 |
| `post_service.py` | `slugify` | `test_slugify_converts_title_to_url_slug` | `test_slugify_falls_back_to_post_when_slug_is_empty` | 完成 |
| `post_service.py` | `ensure_unique_slug` | `test_ensure_unique_slug_adds_suffix` | `test_ensure_unique_slug_handles_chinese_generated_slug` | 完成 |
| `post_service.py` | `build_post` | `test_build_post_generates_slug` | `test_build_post_applies_unique_slug_when_title_conflicts` | 完成 |
| `post_service.py` | `update_post` | `test_update_post_replaces_fields_and_tags` | `test_update_post_replaces_fields_and_tags`（tags 替换边界） | 完成 |
| `post_service.py` | `list_published_posts` | `test_list_published_posts_returns_newest_first` | `test_list_published_posts_returns_newest_first`（顺序边界） | 完成 |
| `post_service.py` | `get_post_by_slug` | `test_get_post_by_slug_returns_post_for_existing_slug` | `test_get_post_by_slug_returns_none_for_missing_slug` | 完成 |
| `taxonomy_service.py` | `get_category_by_slug` | `test_get_category_by_slug_returns_category_with_posts` | `test_get_category_by_slug_returns_none_for_missing_slug` | 完成 |
| `taxonomy_service.py` | `get_tag_by_slug` | `test_get_tag_by_slug_returns_tag_with_posts` | `test_get_tag_by_slug_returns_none_for_missing_slug` | 完成 |
| `setup_service.py` | `is_initialized` | `test_is_initialized_returns_true_with_site_settings_and_admin` | `test_is_initialized_returns_false_when_database_has_no_setup_data` / `test_is_initialized_returns_false_with_only_admin` / `test_is_initialized_returns_false_with_only_site_settings` | 完成 |
| `setup_service.py` | `get_site_settings` | `test_get_site_settings_returns_site_settings_after_initialization` | `test_get_site_settings_returns_none_when_uninitialized` | 完成 |
| `setup_service.py` | `initialize_site` | `test_initialize_site_creates_site_settings_and_admin` | `test_initialize_site_rejects_repeat_install` | 完成 |
| `database_state_service.py` | `database_exists` | `test_database_exists_returns_true_for_non_postgresql_url` / `test_database_exists_returns_true_when_target_database_exists` | `test_database_exists_returns_false_when_target_database_missing` / `test_database_exists_returns_false_when_connection_raises` | 完成 |

## 回归验证

- `python -m pytest -q tests/test_admin_posts.py tests/test_admin_auth.py tests/test_setup_service.py tests/test_post_service.py tests/test_database_state_service.py tests/test_taxonomy_service.py`
- 结果：`66 passed`

## 下一步

1. 运行主流程验证套件（public/admin/setup/post/service/config/health）。
2. 运行全量回归并保存结果快照。
