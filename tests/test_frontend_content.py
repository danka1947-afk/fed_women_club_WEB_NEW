from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = REPO_ROOT / "frontend"
FRONTEND_INDEX = FRONTEND_DIR / "index.html"
FRONTEND_MAIN = FRONTEND_DIR / "src" / "main.js"
FRONTEND_STYLES = FRONTEND_DIR / "src" / "styles.css"
ADMIN_ENDPOINTS = REPO_ROOT / "app" / "api" / "v1" / "endpoints" / "admin.py"
ADMIN_SCHEMAS = REPO_ROOT / "app" / "schemas" / "admin.py"

EXPECTED_TITLE = "Женский клуб — федеральный клуб привилегий для девушек"
FORBIDDEN_PUBLIC_COPY = (
    "skeleton",
    "ADMIN / PARTNER SHELL",
    "Панель администратора и кабинет партнёра сохраняют",
)
REQUIRED_PUBLIC_BLOCKS = (
    "Женский клуб",
    "Категории партнёров",
    "Выберите город",
)


def _frontend_index() -> str:
    return FRONTEND_INDEX.read_text(encoding="utf-8")


def _frontend_main() -> str:
    return FRONTEND_MAIN.read_text(encoding="utf-8")


def _frontend_styles() -> str:
    return FRONTEND_STYLES.read_text(encoding="utf-8")


def _admin_endpoints() -> str:
    return ADMIN_ENDPOINTS.read_text(encoding="utf-8")


def _admin_schemas() -> str:
    return ADMIN_SCHEMAS.read_text(encoding="utf-8")


def _frontend_public_sources() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in (FRONTEND_INDEX, FRONTEND_MAIN)
    )


def _css_block(styles: str, selector: str) -> str:
    match = re.search(rf"{re.escape(selector)}\s*{{(.*?)\n}}", styles, re.S)
    assert match is not None
    return match.group(1)


def _city_options() -> list[str]:
    source = _frontend_main()
    match = re.search(r"const cities = \[(.*?)\];", source, re.S)
    assert match is not None
    return re.findall(r"'([^']+)'", match.group(1))


def test_frontend_title_targets_girls() -> None:
    assert f"<title>{EXPECTED_TITLE}</title>" in _frontend_index()


def test_public_frontend_does_not_render_technical_shell_copy() -> None:
    source = _frontend_public_sources()

    for forbidden_copy in FORBIDDEN_PUBLIC_COPY:
        assert forbidden_copy not in source


def test_public_frontend_keeps_core_blocks() -> None:
    source = _frontend_main()

    for public_block in REQUIRED_PUBLIC_BLOCKS:
        assert public_block in source


def test_public_frontend_contains_css_only_sakura_layer() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for expected in (
        'class="sakura-layer" aria-hidden="true"',
        "sakura-petal",
        "sakura-petal--1",
    ):
        assert expected in source or expected in styles

    assert "Array.from({ length: 68 }" in source
    assert "sakura-petal--68" in styles
    for sakura_color in (
        "rgba(244, 167, 185",
        "rgba(247, 182, 200",
        "rgba(242, 191, 208",
        "rgba(233, 150, 173",
    ):
        assert sakura_color in styles

    assert "--petal-vein" in styles
    assert "filter: blur(0.25px);" in styles
    assert "@keyframes sakuraFall" in styles
    assert "translate3d(" in styles
    assert "animation-duration:" in styles
    assert "animation-delay:" in styles
    assert "--fall-duration:" in styles
    assert "--fall-delay:" in styles
    assert "prefers-reduced-motion: reduce" in styles
    assert "animation: none !important;" in styles
    assert "position: fixed;" in styles
    assert "pointer-events: none;" in styles
    assert "z-index: 0;" in styles
    assert ".app-shell" in styles
    assert "z-index: 1;" in styles

def test_public_landing_cards_use_frosted_translucent_backgrounds() -> None:
    styles = _frontend_styles()

    assert "body:not(.is-dashboard) .hero" in styles
    assert "body:not(.is-dashboard) .panel" in styles

    for selector in (
        "body:not(.is-dashboard) .hero",
        "body:not(.is-dashboard) .panel",
        ".hero-card",
        ".feature-card",
        ".city-select-card",
    ):
        block = _css_block(styles, selector)
        assert "background:" in block
        assert re.search(r"background:[^;]*(rgba|hsla)\(", block, re.S)
        assert "backdrop-filter: blur(10px) saturate(1.05);" in block
        assert "-webkit-backdrop-filter: blur(10px) saturate(1.05);" in block
        assert not re.search(r"(^|\s)opacity\s*:", block)


def test_frontend_adds_subtle_center_sakura_motion() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    assert "Array.from({ length: 20 }" in source
    assert "sakura-petal--center" in source
    assert "sakura-petal--center-${index + 1}" in source
    assert "sakura-petal--center-1" in styles
    assert "sakura-petal--center-20" in styles
    assert "--center-left: 35%" in styles
    assert "--center-left: 65%" in styles
    assert "--center-opacity: 0.22" in styles
    assert "--center-opacity: 0.38" in styles
    assert "will-change: transform;" in _css_block(styles, ".sakura-petal--center")

def test_brand_copy_targets_girls() -> None:
    source = _frontend_main()

    assert "Федеральный клуб привилегий для девушек" in source
    assert "Федеральный клуб привилегий для женщин" not in source


def test_public_brand_block_is_static_not_clickable() -> None:
    source = _frontend_main()

    assert '<div class="brand" aria-label="Женский клуб">' in source
    assert not re.search(r'<a[^>]*class="brand"', source)
    assert not re.search(r'<button[^>]*class="brand"', source)
    assert not re.search(r'class="brand"[^>]*(href|type)=', source)


def test_public_header_does_not_render_admin_panel_action() -> None:
    source = _frontend_main()
    topbar_match = re.search(r'<div class="topbar-actions".*?</div>', source, re.S)

    assert topbar_match is not None
    assert "Панель" not in topbar_match.group(0)


def test_city_selector_uses_static_choice_chips() -> None:
    source = _frontend_main()
    city_selector_block = source.split('<section class="panel" aria-labelledby="login-title" id="login">')[0]

    for forbidden_tag in ("<select", "<option", "<details", "<summary"):
        assert forbidden_tag not in city_selector_block

    assert 'class="city-choice-grid"' in source
    assert "city-choice${index === 0 ? ' is-active' : ''}" in source
    assert _city_options() == ["Новосибирск", "Череповец"]
    assert "Новосибирск" in source
    assert "Череповец" in source


def test_frontend_city_selector_options_are_limited_to_active_cities() -> None:
    assert _city_options() == ["Новосибирск", "Череповец"]


def test_removed_cities_are_not_in_frontend_city_selector() -> None:
    source = _frontend_main()
    cities = _city_options()

    for removed_city in ("Москва", "Санкт-Петербург", "Екатеринбург", "Казань"):
        assert removed_city not in cities
        assert removed_city not in source


def test_city_growth_note_is_present() -> None:
    assert (
        "Чем больше мы растём, тем больше городов подключаем. "
        "Скоро появятся новые города."
    ) in _frontend_main()


def test_frontend_contains_real_login_form_and_dashboard_strings() -> None:
    source = _frontend_main()

    assert 'data-login-form' in source
    assert 'name="email"' in source
    assert 'name="password"' in source
    assert '/api/v1/auth/login' in source
    assert '/api/v1/admin/me' in source
    assert 'Панель администратора' in source
    assert 'Неверный логин или пароль' in source
    assert 'localStorage.setItem(authTokenKey, data.access_token)' in source


def test_frontend_contains_dashboard_shell_classes() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for expected in (
        "dashboard-shell",
        "dashboard-layout",
        "dashboard-sidebar",
        "dashboard-main",
        "dashboard-topbar",
        "Быстрые действия",
    ):
        assert expected in source or expected in styles

    assert "--dashboard-width: min(1680px, calc(100vw - 48px));" in styles
    assert "grid-template-columns: 260px minmax(0, 1fr);" in styles
    assert ".dashboard-main" in styles
    assert "min-width: 0;" in styles


def test_frontend_removes_broken_lotus_background() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for removed_lotus_marker in (
        "reference-lotus-layer",
        "lotus-layer",
        "lotus-decor",
        "--user-lotus-reference-svg",
        "--lotus-reference-background",
        "--lotus-left-composition",
        "--lotus-right-composition",
        "--lotus-swirl-line",
        "--lotus-line-art",
        "--lotus-botanical-line-art",
        "--lotus-botanical-composition",
    ):
        assert removed_lotus_marker not in source
        assert removed_lotus_marker not in styles

    assert ".hero::before" not in styles
    assert "body:not(.is-dashboard)::before" not in styles
    assert "/assets/lotus-bg.png" not in source
    assert "/assets/lotus-bg.png" not in styles

    for expected in (
        "Женский клуб",
        "Федеральный клуб привилегий для девушек",
        "Новосибирск",
        "Череповец",
        "dashboard-shell",
        "dashboard-topbar",
        "dashboard-sidebar",
        "dashboard-main",
        "womenClubAdminAccessToken",
        "womenclub_partner_token",
        "womenclub_client_token",
    ):
        assert expected in source or expected in styles


def test_frontend_keeps_required_public_role_nav_and_token_copy() -> None:
    source = _frontend_main()

    for expected in (
        "Женский клуб",
        "Федеральный клуб привилегий для девушек",
        "Новосибирск",
        "Череповец",
        "Панель администратора",
        "Кабинет партнёра",
        "Личный кабинет",
        "Главная",
        "Пользователи",
        "Города",
        "Категории",
        "Партнёры",
        "Предложения",
        "QR / лиды",
        "Подтверждения",
        "womenClubAdminAccessToken",
        "womenclub_partner_token",
        "womenclub_client_token",
    ):
        assert expected in source





def test_frontend_contains_compact_admin_table_markers() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for expected in (
        "admin-table-action",
        "admin-table--compact",
        "admin-table-cell--actions",
        "text-overflow: ellipsis",
        "overflow-wrap",
        "table-layout",
    ):
        assert expected in source or expected in styles

    for tab_text in (
        "Пользователи",
        "Города",
        "Категории",
        "Партнёры",
        "Предложения",
        "QR / лиды",
        "Подтверждения",
    ):
        assert tab_text in source


def test_frontend_contains_admin_search_filter_markers() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for expected in (
        "admin-search",
        "admin-search-input",
        "admin-toolbar",
        "admin-search-reset",
    ):
        assert expected in source or expected in styles

    for placeholder in (
        "Поиск по пользователям",
        "Поиск по городам",
        "Поиск по категориям",
        "Поиск по партнёрам",
        "Поиск по предложениям",
        "Поиск по QR",
        "Поиск по лидам",
        "Поиск по подтверждениям",
    ):
        assert placeholder in source

    for helper_marker in (
        "normalizeSearchText",
        "filterAdminRows",
        "data-admin-search",
        "data-admin-search-reset",
        "Ничего не найдено.",
    ):
        assert helper_marker in source


def test_frontend_contains_reusable_status_badges() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for expected in (
        "renderStatusBadge",
        "status-badge",
        "status-badge--success",
        "status-badge--muted",
        "status-badge--warning",
        "status-badge--danger",
    ):
        assert expected in source or expected in styles

    for expected_label in (
        "Активен",
        "Неактивен",
        "Активна",
        "Неактивна",
        "Проверен",
        "Не проверен",
        "Подтверждено",
        "Истекло",
        "Отменено",
    ):
        assert expected_label in source

    for preserved_marker in (
        "Пользователи",
        "Города",
        "Категории",
        "Партнёры",
        "Предложения",
        "QR / лиды",
        "Подтверждения",
        "Личный кабинет",
        "Кабинет партнёра",
        "womenClubAdminAccessToken",
        "womenclub_partner_token",
        "womenclub_client_token",
        "dashboard-shell",
        "dashboard-topbar",
        "dashboard-sidebar",
        "dashboard-main",
        "Женский клуб",
        "Федеральный клуб привилегий для девушек",
        "Новосибирск",
        "Череповец",
    ):
        assert preserved_marker in source or preserved_marker in styles

    for removed_lotus_marker in (
        "reference-lotus-layer",
        "lotus-layer",
        "lotus-decor",
        "--user-lotus-reference-svg",
        "--lotus-reference-background",
        "/assets/lotus-bg.png",
    ):
        assert removed_lotus_marker not in source
        assert removed_lotus_marker not in styles


def test_frontend_contains_human_readable_admin_labels() -> None:
    source = _frontend_main()

    for expected in (
        "Название города",
        "Порядок сортировки",
        "Владелец / аккаунт партнёра",
        "Название партнёра",
        "Ссылка на соцсеть / сайт",
        "Название предложения",
        "Цена со скидкой",
        "Скидка, %",
        "Целевая ссылка",
        "Подтверждено",
        "Email",
        "Телефон",
        "Роль",
        "Активен",
        "Действие",
        "Клиент",
        "Администратор",
    ):
        assert expected in source


def test_frontend_does_not_render_technical_admin_labels() -> None:
    source = _frontend_main()
    rendered_table_headers = "\n".join(re.findall(r"renderTable\(\[(.*?)\]", source, re.S))

    for forbidden_label in (
        "city_id",
        "owner_user_id",
        "category_slug",
        "sort_order",
        "is_active",
    ):
        assert f">{forbidden_label}<" not in source
        assert f">{forbidden_label}" not in source
        assert f"'{forbidden_label}'" not in rendered_table_headers
        assert f'"{forbidden_label}"' not in rendered_table_headers


def test_frontend_contains_admin_cabinet_tabs() -> None:
    source = _frontend_main()

    for tab_text in (
        "Панель администратора",
        "Главная",
        "Обзор",
        "Пользователи",
        "Города",
        "Категории",
        "Партнёры",
        "Предложения",
        "QR / лиды",
        "Подтверждения",
    ):
        assert tab_text in source


def test_frontend_contains_admin_cabinet_endpoint_strings() -> None:
    source = _frontend_main()

    for endpoint in (
        "/api/v1/admin/users",
        "/api/v1/admin/cities",
        "/api/v1/admin/categories",
        "/api/v1/admin/partners",
        "/api/v1/admin/leads/partners",
        "/api/v1/admin/verifications",
    ):
        assert endpoint in source


def test_admin_categories_support_create_edit_and_safe_toggle_ui() -> None:
    endpoints = _admin_endpoints()
    schemas = _admin_schemas()
    source = _frontend_main()

    assert '@router.get("/categories", response_model=list[CategoryRead])' in endpoints
    assert '@router.post("/categories", response_model=CategoryRead)' in endpoints
    assert '@router.patch("/categories/{category_id}", response_model=CategoryRead)' in endpoints
    assert '@router.delete("/categories/{category_id}"' not in endpoints
    assert 'class CategoryCreate' in schemas
    assert 'class CategoryUpdate' in schemas

    for marker in (
        "Новая категория",
        "Редактировать категорию",
        "Редактировать",
        "Деактивировать",
        "Активировать",
        "Название",
        "Slug",
        "Активна",
        "Порядок сортировки",
        "Отмена",
        "postJson('/api/v1/admin/categories'",
        "patchJson(`/api/v1/admin/categories/${categoryId}`",
        "data-admin-category-edit",
        "data-admin-category-active-toggle",
    ):
        assert marker in source


def test_frontend_category_admin_keeps_public_dashboard_and_removed_image_markers() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for marker in (
        "Женский клуб",
        "Федеральный клуб привилегий для девушек",
        "Новосибирск",
        "Череповец",
        "dashboard-shell",
        "dashboard-topbar",
        "dashboard-sidebar",
        "dashboard-main",
        "womenClubAdminAccessToken",
        "womenclub_partner_token",
        "womenclub_client_token",
    ):
        assert marker in source

    for removed_marker in (
        "reference-lotus-layer",
        "lotus-layer",
        "lotus-decor",
        "--user-lotus-reference-svg",
        "--lotus-reference-background",
        "/assets/lotus-bg.png",
    ):
        assert removed_marker not in source
        assert removed_marker not in styles


def test_frontend_contains_admin_user_role_options() -> None:
    source = _frontend_main()

    for role in ("client", "partner", "admin"):
        assert role in source


def test_frontend_contains_admin_users_management_ui_strings() -> None:
    source = _frontend_main()

    for expected in (
        "data-admin-form=\"user\"",
        "data-user-active-toggle",
        "Создать пользователя",
        "owner_user_id",
        "Без владельца",
        "owner_email",
    ):
        assert expected in source


def test_public_landing_copy_and_city_chips_remain_intact() -> None:
    source = _frontend_main()

    for public_copy in (
        "Женский клуб",
        "Федеральный клуб привилегий для девушек",
        "Новосибирск",
        "Череповец",
    ):
        assert public_copy in source


def test_frontend_contains_admin_city_edit_and_safe_deactivate_ui() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for expected in (
        "Редактировать город",
        "Редактировать",
        "Деактивировать",
        "Убрать город из активных?",
        "data-admin-city-edit",
        "data-admin-city-active-toggle",
        "Название",
        "Slug",
        "Активен",
        "Порядок сортировки",
        "Отмена",
        "POST",
        "PATCH",
        "/api/v1/admin/cities",
        "patchJson(`/api/v1/admin/cities/${cityId}`",
        "is_active: city.is_active ? false : true",
        "await loadCities();",
    ):
        assert expected in source or expected in styles


def test_frontend_city_management_keeps_required_landing_dashboard_and_negative_markers() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for expected in (
        "Женский клуб",
        "Федеральный клуб привилегий для девушек",
        "Новосибирск",
        "Череповец",
        "dashboard-shell",
        "dashboard-topbar",
        "dashboard-sidebar",
        "dashboard-main",
        "womenClubAdminAccessToken",
        "womenclub_partner_token",
        "womenclub_client_token",
    ):
        assert expected in source or expected in styles

    for removed_marker in (
        "reference-lotus-layer",
        "lotus-layer",
        "lotus-decor",
        "--user-lotus-reference-svg",
        "--lotus-reference-background",
        "/assets/lotus-bg.png",
    ):
        assert removed_marker not in source
        assert removed_marker not in styles


def test_frontend_contains_admin_partner_edit_ui() -> None:
    source = _frontend_main()

    for expected in (
        "Редактировать партнёра",
        "Редактировать",
        "/api/v1/admin/partners/",
        "Город",
        "Категория",
        "Владелец",
        "Без владельца",
        "Название",
        "Описание",
        "Адрес",
        "Телефон",
        "Сайт",
        "Соцсеть",
        "Активен",
        "Проверен",
    ):
        assert expected in source


def test_frontend_contains_admin_offer_edit_ui() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for expected in (
        "Редактировать предложение",
        "Редактировать",
        "/api/v1/admin/offers/",
        "PATCH",
        "Название",
        "Описание",
        "Скидка / выгода",
        "Условия",
        "Активно",
        "Отмена",
        "POST",
        "/api/v1/admin/partners/",
        "/offers",
        "Женский клуб",
        "Федеральный клуб привилегий для девушек",
        "Новосибирск",
        "Череповец",
        "dashboard-shell",
        "dashboard-topbar",
        "dashboard-sidebar",
        "dashboard-main",
        "womenClubAdminAccessToken",
        "womenclub_partner_token",
        "womenclub_client_token",
    ):
        assert expected in source or expected in styles

    for removed_lotus_marker in (
        "reference-lotus-layer",
        "lotus-layer",
        "lotus-decor",
        "--user-lotus-reference-svg",
        "--lotus-reference-background",
        "/assets/lotus-bg.png",
    ):
        assert removed_lotus_marker not in source
        assert removed_lotus_marker not in styles


def test_frontend_contains_admin_qr_edit_ui() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for expected in (
        "Редактировать QR-ссылку",
        "Редактировать",
        "/api/v1/admin/qr-links/",
        "PATCH",
        "Slug",
        "Целевая ссылка",
        "Deep-link payload",
        "Активна",
        "Отмена",
        "POST",
        "/api/v1/admin/partners/",
        "/qr-links",
        "Женский клуб",
        "Федеральный клуб привилегий для девушек",
        "Новосибирск",
        "Череповец",
        "dashboard-shell",
        "dashboard-topbar",
        "dashboard-sidebar",
        "dashboard-main",
        "womenClubAdminAccessToken",
        "womenclub_partner_token",
        "womenclub_client_token",
    ):
        assert expected in source or expected in styles

    for removed_lotus_marker in (
        "reference-lotus-layer",
        "lotus-layer",
        "lotus-decor",
        "--user-lotus-reference-svg",
        "--lotus-reference-background",
        "/assets/lotus-bg.png",
    ):
        assert removed_lotus_marker not in source
        assert removed_lotus_marker not in styles


def test_frontend_keeps_landing_and_dashboard_markers_with_partner_edit() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for expected in (
        "Женский клуб",
        "Федеральный клуб привилегий для девушек",
        "Новосибирск",
        "Череповец",
        "dashboard-shell",
        "dashboard-topbar",
        "dashboard-sidebar",
        "dashboard-main",
        "womenClubAdminAccessToken",
        "womenclub_partner_token",
        "womenclub_client_token",
    ):
        assert expected in source or expected in styles


def test_frontend_login_modes_remain_available() -> None:
    source = _frontend_main()

    for expected in (
        "Администратор",
        "Партнёр",
        "Клиент",
    ):
        assert expected in source


def test_frontend_contains_partner_cabinet_foundation() -> None:
    source = _frontend_main()

    for expected in (
        "Кабинет партнёра",
        "Партнёр",
        "Профиль",
        "Предложения",
        "QR / лиды",
        "Подтверждения",
    ):
        assert expected in source


def test_frontend_contains_partner_endpoint_strings_and_separate_token() -> None:
    source = _frontend_main()

    for endpoint in (
        "/api/v1/auth/user-login",
        "/api/v1/auth/user-me",
        "/api/v1/partners/me",
        "/api/v1/partners/me/offers",
        "/api/v1/partners/me/qr-links",
        "/api/v1/partners/me/leads",
        "/api/v1/partners/me/verifications",
    ):
        assert endpoint in source

    assert "/api/v1/auth/login" in source
    assert "womenclub_partner_token" in source


def test_partner_cabinet_uses_human_readable_copy_statuses_and_empty_states() -> None:
    source = _frontend_main()

    for expected in (
        "Пока нет предложений.",
        "Добавьте первое предложение",
        "Пока нет QR-ссылок.",
        "Создайте QR-ссылку",
        "Пока нет лидов.",
        "Когда клиенты перейдут по QR-ссылке",
        "Пока нет подтверждений.",
        "Когда клиент покажет код привилегии",
        "Активен",
        "Неактивен",
        "Проверен",
        "Не проверен",
        "Активно",
        "Неактивно",
        "Активна",
        "Неактивна",
        "Подтверждено",
        "Истекло",
        "Отменено",
        "Название",
        "Краткая выгода",
        "Описание",
        "Условия",
        "Базовая цена",
        "Код ссылки",
        "Целевая ссылка",
        "Подтвердить привилегию",
    ):
        assert expected in source

    for marker in (
        "womenclub_partner_token",
        "womenclub_client_token",
        "womenClubAdminAccessToken",
        "dashboard-shell",
        "dashboard-topbar",
        "dashboard-sidebar",
        "dashboard-main",
        "Женский клуб",
        "Федеральный клуб привилегий для девушек",
        "Новосибирск",
        "Череповец",
    ):
        assert marker in source

    assert "renderStatusBadge(formatStatus(item.status))" in source
    assert "renderActiveStatusBadge(offer.is_active)" in source
    assert "renderActiveStatusFeminineBadge(link.is_active)" in source

def test_frontend_contains_client_cabinet_foundation() -> None:
    source = _frontend_main()

    for expected in (
        "Личный кабинет",
        "Клиент",
        "Профиль",
        "Каталог",
        "Моя подписка",
        "История",
    ):
        assert expected in source


def test_frontend_contains_client_endpoint_strings_and_separate_token() -> None:
    source = _frontend_main()

    for endpoint in (
        "/api/v1/auth/user-login",
        "/api/v1/auth/user-me",
        "/api/v1/clients/me",
        "/api/v1/clients/me/subscription",
        "/api/v1/clients/catalog/partners",
        "/api/v1/clients/partners/",
        "/api/v1/clients/me/verifications",
    ):
        assert endpoint in source

    assert "womenclub_client_token" in source
    assert "womenClubAdminAccessToken" in source
    assert "womenclub_partner_token" in source


def test_frontend_contains_client_vk_link_code_ui() -> None:
    source = _frontend_main()

    for expected in (
        "Привязка VK",
        "Создать код для VK",
        "/api/v1/clients/me/vk-link-codes",
        "Привязать",
    ):
        assert expected in source

    assert "womenclub_client_token" in source
    assert "womenClubAdminAccessToken" in source
    assert "womenclub_partner_token" in source

    for public_copy in (
        "Женский клуб",
        "Федеральный клуб привилегий для девушек",
        "Новосибирск",
        "Череповец",
    ):
        assert public_copy in source


def test_client_cabinet_uses_human_readable_profile_catalog_history_and_subscription_copy() -> None:
    source = _frontend_main()

    for forbidden in (
        "ID города не угадывается",
        "Город (ID)",
        "например, beauty",
        "Например, beauty",
        "ID из админки",
    ):
        assert forbidden not in source

    for expected in (
        "Выберите город",
        "Выберите город, чтобы видеть предложения рядом с вами.",
        "Все категории",
        "Категория",
        "По выбранному городу",
        "Все города",
        "Название, описание, адрес",
        "Пока нет подтверждений.",
        "Активная подписка пока не найдена",
        "Когда подписка будет оформлена",
        "Активно",
        "Подтверждено",
        "Истекло",
        "Отменено",
    ):
        assert expected in source

    assert "selected_city_id: selectedCityId ? Number(selectedCityId) : null" in source
    assert "renderStatusBadge(formatStatus(item.status))" in source
    assert "formatClientCategory(partner.category_slug)" in source


def test_frontend_contains_vk_password_setup_flow_markers() -> None:
    source = _frontend_main()

    assert "setup_token" in source
    assert "getPasswordSetupParams" in source
    assert "Задайте пароль" in source
    assert "Новый пароль" in source
    assert "Повторите пароль" in source
    assert "Пароль установлен. Теперь войдите" in source
    assert "/api/v1/auth/password-setup/complete" in source
    assert "Ссылка недействительна или истекла" in source


def test_frontend_preserves_public_and_cabinet_contract_markers_after_password_setup() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for expected in (
        "Федеральный клуб привилегий для девушек",
        "data-login-form",
        'data-login-mode="admin"',
        'data-login-mode="partner"',
        'data-login-mode="client"',
        "/api/v1/auth/login",
        "/api/v1/auth/user-login",
        "Панель администратора",
        "partner-dashboard",
        "client-dashboard",
    ):
        assert expected in source

    for removed_marker in (
        "reference-lotus-layer",
        "lotus-layer",
        "lotus-decor",
        "--user-lotus-reference-svg",
        "--lotus-reference-background",
    ):
        assert removed_marker not in source
        assert removed_marker not in styles


def test_public_landing_contains_smm_hero_menu_directions_and_partner_modal() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for expected in (
        "hero-card",
        "для себя",
        "Красота, забота и вдохновение",
        "Скидки, подарки и специальные предложения у партнёров клуба.",
        "formatPartnerBenefit",
        "Специальное предложение",
        "landing-menu",
        "landing-menu-toggle",
        "landing-menu-panel",
        "О клубе",
        "Привилегии",
        "Партнёры",
        "Направления",
        "Как вступить",
        "Города",
        "landing-about",
        "landing-benefits",
        "landing-partners",
        "landing-directions",
        "landing-join",
        "landing-cities",
        "landing-direction-button",
        "direction-card",
        "data-landing-category-slug",
        "selectedLandingDirection",
        "landingPartnerModalState",
        "/api/v1/public/landing/partners",
        "landing-partner-modal",
        "landing-partner-panel",
        "landing-partner-card",
        "landing-partner-cover",
        "landing-partner-cover--placeholder",
        "landing-carousel-button",
        "Партнёры этого направления скоро появятся.",
        "Закрыть",
    ):
        assert expected in source or expected in styles

    for expected_style in (
        ".hero-card",
        ".pill",
        ".landing-menu-panel",
        ".landing-direction-button",
        ".landing-partner-modal",
        ".landing-partner-card",
        ".landing-carousel-button",
    ):
        assert expected_style in styles

    topbar_block = _css_block(styles, ".topbar")
    landing_menu_block = _css_block(styles, ".landing-menu")
    landing_menu_panel_block = _css_block(styles, ".landing-menu-panel")
    hero_card_block = _css_block(styles, ".hero-card")

    assert "z-index: 20;" in topbar_block
    assert "z-index: 30;" in landing_menu_block
    assert "Keep landing dropdown above hero/glass cards." in landing_menu_panel_block
    assert "position: absolute;" in landing_menu_panel_block
    assert "z-index: 40;" in landing_menu_panel_block
    assert "pointer-events: auto;" in landing_menu_panel_block
    assert "right: 0;" in landing_menu_panel_block
    assert "z-index:" not in hero_card_block

    assert "Красота, забота и привилегии рядом с вами" not in source
    assert "hero-visual" not in source
    assert "hero-visual-image" not in styles
    assert "1E+1" not in source
    assert "-1E+1%" not in source


def test_public_landing_uses_safe_public_partner_fetches_and_images() -> None:
    source = _frontend_main()
    styles = _frontend_styles()
    public_landing_match = re.search(r"const renderPublicApp = \(\) => \{(.*?)const authTokenKey", source, re.S)
    assert public_landing_match is not None
    public_landing_source = public_landing_match.group(1)

    assert "/api/v1/public/landing/partners" in source
    assert "/api/v1/admin/partners" not in public_landing_source
    assert "/api/v1/clients/catalog/partners" not in public_landing_source
    assert "Красота, забота и привилегии рядом с вами" not in source
    assert "hero-visual" not in source
    assert "hero-visual-image" not in styles
    assert 'url("/assets/hero-woman.jpg")' not in styles
    assert "startsWith('/assets/')" in source
    assert "startsWith('/uploads/')" in source


def test_frontend_contains_partner_logo_cover_upload_markers() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for expected in (
        "Загрузить логотип",
        "Загрузить обложку",
        "Фотографии профиля",
        "Изображения партнёра",
        "/api/v1/admin/partners/${partnerId}/images?kind=${kind}",
        "/api/v1/partners/me/images?kind=${kind}",
        "partner-image-uploader",
        "partner-image-preview",
        "/uploads/",
    ):
        assert expected in source or expected in styles


def test_frontend_contains_partner_marketplace_profile_preview() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for expected in (
        "renderPartnerMarketplaceCard",
        "partner-marketplace-card",
        "partner-marketplace-cover",
        "partner-marketplace-logo",
        "partner-marketplace-body",
        "partner-marketplace-meta",
        "partner-marketplace-offer",
        "partner-profile-layout",
        "partner-profile-preview",
        "partner-profile-settings",
        "partner-profile-hints",
        "Профиль партнёра",
        "Настройте, как ваша карточка будет выглядеть",
        "Так карточку увидит клиент",
        "Название, город и категорию редактирует администратор",
        "График работы",
        "Витрина партнёра",
        "Заполненность профиля",
        "Загрузить логотип",
        "Загрузить обложку",
        "/api/v1/partners/me/images",
        "/api/v1/admin/partners/",
        "/images?kind=",
        "working_hours",
        "logo_url",
        "cover_url",
        "sort_order",
    ):
        assert expected in source or expected in styles

    assert "startsWith('/uploads/')" in source
    assert "startsWith('/assets/')" in source

def test_frontend_contains_offer_marketplace_cards() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for expected in (
        "renderOfferMarketplaceCard",
        "offer-marketplace-card",
        "offer-marketplace-image",
        "offer-marketplace-benefit",
        "offer-marketplace-preview",
        "offer-card-grid",
        "offer-card-placeholder",
        "Предложения и привилегии",
        "Оформите услуги так, чтобы участницы сразу понимали выгоду",
        "Так предложение увидит клиент",
        "Добавьте первое предложение",
        "URL изображения",
        "Базовая цена",
        "Скидка, %",
        "Получить привилегию",
        "Карточка привилегии партнёра",
        "Фото услуги",
        "Специальное предложение",
        "/uploads/offer.webp",
        "/assets/offer.webp",
    ):
        assert expected in source or expected in styles

    assert "startsWith('/uploads/')" in source
    assert "startsWith('/assets/')" in source
    assert "image_url: getOptionalText(formData, 'image_url')" in source
    assert "partner-marketplace-card" in source or "partner-marketplace-card" in styles
    assert "Загрузить логотип" in source
    assert "Загрузить обложку" in source
    assert "/api/v1/public/landing/partners" in source
    assert "landing-partner-card" in source or "landing-partner-card" in styles
    assert "data-landing-partner-modal" in source
    assert "setup_token" in source
    assert "womenClubAdminAccessToken" in source
    assert "womenclub_partner_token" in source
    assert "womenclub_client_token" in source

    for removed_marker in (
        "reference-lotus-layer",
        "lotus-layer",
        "lotus-decor",
        "--user-lotus-reference-svg",
        "--lotus-reference-background",
        "/assets/lotus-bg.png",
    ):
        assert removed_marker not in source
        assert removed_marker not in styles


def test_frontend_contains_safe_offer_image_upload_markers() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for expected in (
        "Фото предложения",
        "Загрузить фото предложения",
        "Сначала сохраните предложение, затем загрузите фото.",
        "/api/v1/admin/offers/",
        "/image",
        "/api/v1/partners/me/offers/",
        "offer-image-uploader",
        "offer-image-preview",
        "offer-image-upload-actions",
        "offer-image-status",
        "admin-offers-layout",
        "admin-offers-toolbar",
        "admin-offers-preview-panel",
        "admin-offers-table-panel",
        "admin-offers-form-panel",
        "admin-table-actions",
        "admin-action-button",
        "admin-table-action",
        "/uploads/",
        "renderOfferMarketplaceCard",
        "offer-marketplace-card",
        "offer-marketplace-image",
        "Загрузить логотип",
        "Загрузить обложку",
        "partner-image-uploader",
        "partner-image-preview",
        "/api/v1/public/landing/partners",
        "data-landing-partner-modal",
        "landing-directions",
        "setup_token",
        "womenClubAdminAccessToken",
        "womenclub_partner_token",
        "womenclub_client_token",
        "dashboard-shell",
        "dashboard-topbar",
        "dashboard-sidebar",
        "dashboard-main",
    ):
        assert expected in source or expected in styles

    assert "startsWith('/uploads/')" in source
    assert "startsWith('/assets/')" in source

    for removed_marker in (
        "reference-lotus-layer",
        "lotus-layer",
        "lotus-decor",
        "--user-lotus-reference-svg",
        "--lotus-reference-background",
        "/assets/lotus-bg.png",
    ):
        assert removed_marker not in source
        assert removed_marker not in styles


def test_frontend_contains_partner_gallery_photo_mvp_markers() -> None:
    source = FRONTEND_MAIN.read_text(encoding="utf-8")
    styles = FRONTEND_STYLES.read_text(encoding="utf-8")

    required_source_markers = [
        "Галерея партнёра",
        "Загрузить фото в галерею",
        "Добавьте живые фото",
        "Новые фото появятся в витрине после проверки и активации администратором.",
        "Фото загружено и отправлено на проверку.",
        "На проверке",
        "Ожидает активации администратором.",
        "Скрыть фото",
        "partner-gallery",
        "partner-gallery-grid",
        "/api/v1/admin/partners/",
        "/photos",
        "/api/v1/partners/me/photos",
        "landing-partner-gallery",
        "/api/v1/partners/me/images?kind=${kind}",
        "/api/v1/admin/partners/${partnerId}/images?kind=${kind}",
        "/api/v1/partners/me/offers/${offerId}/image",
        "/api/v1/admin/offers/${offerId}/image",
        "partner-marketplace-card",
        "offer-marketplace-card",
        "setup_token",
        "/api/v1/public/landing/partners",
        "startsWith('/uploads/')",
    ]
    for marker in required_source_markers:
        assert marker in source

    for marker in [
        ".partner-gallery",
        ".partner-gallery-grid",
        ".partner-gallery-item",
        ".partner-gallery-image",
        ".partner-gallery-actions",
        ".partner-gallery-upload",
        ".partner-gallery-empty",
        ".partner-gallery-status",
    ]:
        assert marker in styles

    forbidden_reference_markers = ["lotus", "Лотос", "remote image fetch"]
    for marker in forbidden_reference_markers:
        assert marker not in source


def test_frontend_contains_partner_content_moderation_markers() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for expected in (
        "Новое предложение появится у клиентов после проверки и активации администратором.",
        "Предложение отправлено на проверку. После активации администратором оно появится у клиентов.",
        "Новые фото появятся в витрине после проверки и активации администратором.",
        "Фото загружено и отправлено на проверку.",
        "Ожидает активации администратором.",
        "На проверке",
        "partner-gallery-status",
        "renderPartnerReviewStatusBadge",
        "Неактивные материалы не видны клиентам.",
        "partner-marketplace-card",
        "offer-marketplace-card",
        "/api/v1/partners/me/photos",
        "/api/v1/partners/me/offers",
        "/api/v1/partners/me/activity",
        "/api/v1/partners/me/analytics",
        "setup_token",
        "dashboard-shell",
        "womenclub_partner_token",
        "womenclub_client_token",
        "/api/v1/public/landing/partners",
    ):
        assert expected in source or expected in styles

    for removed_marker in (
        "reference-lotus-layer",
        "lotus-layer",
        "lotus-decor",
        "--user-lotus-reference-svg",
        "--lotus-reference-background",
        "/assets/lotus-bg.png",
    ):
        assert removed_marker not in source
        assert removed_marker not in styles


def test_frontend_contains_client_marketplace_partner_catalog_markers() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for expected in (
        "client-marketplace-grid",
        "client-partner-card",
        "client-partner-cover",
        "client-partner-logo",
        "client-partner-gallery",
        "client-partner-detail",
        "client-partner-offers",
        "client-partner-empty",
        "Партнёры пока не найдены",
        "Попробуйте выбрать другой город или категорию",
        "Предложения скоро появятся",
        "Смотреть предложения",
        "Получить привилегию",
        "Проверенный партнёр",
        "renderOfferMarketplaceCard",
        "offer-marketplace-card",
        "getActivePartnerGalleryPhotos(partner.photos)",
        "isSafePublicAssetUrl(partner.cover_url)",
        "isSafePublicAssetUrl(partner.logo_url)",
        "openClientPartnerMarketplace",
        "/api/v1/clients/partners/${partnerId}",
        "/api/v1/clients/partners/${partnerId}/offers",
        "partner-gallery",
        "partner-gallery-grid",
        "Загрузить фото в галерею",
        "setup_token",
        "womenClubAdminAccessToken",
        "womenclub_partner_token",
        "womenclub_client_token",
        "dashboard-shell",
        "dashboard-topbar",
        "dashboard-sidebar",
        "dashboard-main",
        "/api/v1/public/landing/partners",
        "data-landing-partner-modal",
    ):
        assert expected in source or expected in styles

    assert "startsWith('/uploads/')" in source
    assert "startsWith('/assets/')" in source

    for removed_marker in (
        "reference-lotus-layer",
        "lotus-layer",
        "lotus-decor",
        "--user-lotus-reference-svg",
        "--lotus-reference-background",
        "/assets/lotus-bg.png",
    ):
        assert removed_marker not in source
        assert removed_marker not in styles


def test_frontend_contains_privilege_marketplace_flow_markers() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for expected in (
        "Привилегия активирована",
        "Покажите этот код партнёру перед оплатой/получением услуги.",
        "Мои привилегии",
        "Для получения привилегии нужна активная подписка.",
        "Предложение сейчас недоступно.",
        "Подтвердить привилегию",
        "data-privilege-success-panel",
        "data-client-privilege-card",
        "data-partner-confirmation-card",
        "privilege-success-panel",
        "client-privilege-card",
        "partner-confirmation-card",
        "/api/v1/clients/partners/${partnerId}/verify",
        "/api/v1/clients/me/verifications",
        "/api/v1/partners/me/verifications/${verificationId}/confirm",
        "renderOfferMarketplaceCard",
        "offer-marketplace-card",
        "partner-gallery",
        "setup_token",
        "/api/v1/public/landing/partners",
        "womenclub_client_token",
        "womenclub_partner_token",
    ):
        assert expected in source or expected in styles

    for expected_status in ("Активно", "Подтверждено", "Истекло", "Отменено"):
        assert expected_status in source

    assert "startsWith('/uploads/')" in source
    assert "startsWith('/assets/')" in source

    for removed_lotus_marker in (
        "reference-lotus-layer",
        "lotus-layer",
        "lotus-decor",
        "--user-lotus-reference-svg",
        "--lotus-reference-background",
        "/assets/lotus-bg.png",
    ):
        assert removed_lotus_marker not in source
        assert removed_lotus_marker not in styles


def test_frontend_contains_partner_analytics_ui_markers() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for expected in (
        "Аналитика",
        "Аналитика партнёра",
        "Переходы по QR",
        "Получено привилегий",
        "Подтверждено",
        "Активные привилегии",
        "Истекшие привилегии",
        "Конверсия в привилегию",
        "Процент подтверждения",
        "Данных пока нет",
        "Аналитика помогает понять",
        "/api/v1/partners/me/analytics",
        "/api/v1/admin/partners/",
        "/analytics",
        "renderAnalyticsCards",
        "partnerAnalyticsById",
        "selectedPartnerAnalytics",
        "analyticsLoading",
        "analyticsError",
    ):
        assert expected in source

    for expected_style in (
        "analytics-grid",
        "analytics-card",
        "analytics-value",
        "analytics-label",
        "analytics-hint",
        "analytics-empty",
    ):
        assert expected_style in source or expected_style in styles

    for preserved_marker in (
        "partner-marketplace-card",
        "offer-marketplace-card",
        "partner-gallery",
        "partner-gallery-grid",
        "data-privilege-success-panel",
        "data-client-privilege-card",
        "data-partner-confirmation-card",
        "setup_token",
        "/api/v1/public/landing/partners",
        "womenclub_partner_token",
        "womenclub_client_token",
        "dashboard-shell",
        "dashboard-topbar",
        "dashboard-sidebar",
        "dashboard-main",
        "startsWith('/uploads/')",
    ):
        assert preserved_marker in source or preserved_marker in styles

    for removed_lotus_marker in (
        "reference-lotus-layer",
        "lotus-layer",
        "lotus-decor",
        "--user-lotus-reference-svg",
        "--lotus-reference-background",
        "/assets/lotus-bg.png",
    ):
        assert removed_lotus_marker not in source
        assert removed_lotus_marker not in styles


def test_frontend_contains_derived_activity_feed_ui_markers() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for expected in (
        "Активность",
        "Событий пока нет.",
        "Загружаем события",
        "Не удалось загрузить события",
        "Здесь появятся ваши действия",
        "Лента помогает быстро видеть",
        "Все события",
        "QR-переходы",
        "/api/v1/clients/me/activity",
        "/api/v1/partners/me/activity",
        "/api/v1/admin/activity",
        "renderActivityFeed",
        "renderActivityItem",
        "formatActivityDate",
        "privilege_created",
        "privilege_confirmed",
        "privilege_expired",
        "qr_clicked",
        "partner_created",
        "offer_created",
        "qr_link_created",
    ):
        assert expected in source

    for expected_style in (
        "activity-feed",
        "activity-item",
        "activity-badge",
        "activity-badge--privilege",
        "activity-badge--confirmed",
        "activity-badge--expired",
        "activity-badge--qr",
        "activity-badge--partner",
        "activity-meta",
        "activity-empty",
        "activity-filter",
    ):
        assert expected_style in source or expected_style in styles

    for preserved_marker in (
        "partner-marketplace-card",
        "offer-marketplace-card",
        "partner-gallery",
        "partner-gallery-grid",
        "data-privilege-success-panel",
        "data-client-privilege-card",
        "data-partner-confirmation-card",
        "analytics-grid",
        "analytics-card",
        "analyticsLoading",
        "setup_token",
        "/api/v1/auth/password-setup/complete",
        "/api/v1/public/landing/partners",
        "/api/v1/clients/catalog/partners",
        "dashboard-shell",
        "dashboard-topbar",
        "dashboard-sidebar",
        "dashboard-main",
        "womenclub_partner_token",
        "womenclub_client_token",
        "womenClubAdminAccessToken",
        "startsWith('/uploads/')",
    ):
        assert preserved_marker in source or preserved_marker in styles

    for removed_lotus_marker in (
        "reference-lotus-layer",
        "lotus-layer",
        "lotus-decor",
        "--user-lotus-reference-svg",
        "--lotus-reference-background",
        "/assets/lotus-bg.png",
    ):
        assert removed_lotus_marker not in source
        assert removed_lotus_marker not in styles


def test_frontend_contains_admin_partner_detail_screen_markers() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for expected in (
        "Назад к списку партнёров",
        "Редактирование партнёра",
        "Основные данные",
        "Изображения партнёра",
        "Галерея партнёра",
        "Так партнёр будет выглядеть в клиентском каталоге",
    ):
        assert expected in source

    for expected_style in (
        "admin-partner-detail",
        "admin-partner-detail-header",
        "admin-partner-detail-grid",
        "admin-partner-detail-main",
        "admin-partner-detail-side",
        "admin-partner-detail-section",
        "admin-back-button",
    ):
        assert expected_style in source or expected_style in styles

    for preserved_marker in (
        "partner-marketplace-card",
        "publish-readiness",
        "partner-gallery",
        "partner-image-uploader",
        "content-review",
        "content-review-preview",
        "analytics-grid",
        "analytics-card",
        "offer-image-uploader",
        "setup_token",
        "/api/v1/public/landing/partners",
    ):
        assert preserved_marker in source or preserved_marker in styles


def test_frontend_contains_admin_publish_readiness_markers() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    for expected in (
        "Готовность к публикации",
        "Готов к публикации",
        "Нужно доработать",
        "Проверьте базовые элементы витрины",
        "Обложка добавлена",
        "Логотип добавлен",
        "Описание заполнено",
        "Адрес заполнен",
        "График работы заполнен",
        "Есть активное предложение",
        "Партнёр активен",
        "Партнёр проверен",
        "renderPublishReadiness",
        "getAdminLoadedOffersForPartner",
    ):
        assert expected in source

    for expected_style in (
        "publish-readiness",
        "publish-readiness-checklist",
        "publish-readiness-item--ok",
        "publish-readiness-item--warn",
    ):
        assert expected_style in source or expected_style in styles

    for preserved_marker in (
        "content-review",
        "content-review-card",
        "content-review-preview",
        "/api/v1/admin/content-review",
        "offer-image-uploader",
        "partner-image-uploader",
        "partner-gallery",
        "partner-gallery-grid",
        "offer-marketplace-card",
        "partner-marketplace-card",
        "analytics-grid",
        "analytics-card",
        "analyticsLoading",
        "/api/v1/admin/activity",
        "activity-feed",
        "data-privilege-success-panel",
        "data-client-privilege-card",
        "data-partner-confirmation-card",
        "setup_token",
        "/api/v1/auth/password-setup/complete",
        "/api/v1/public/landing/partners",
        "/api/v1/clients/catalog/partners",
        "womenclub_partner_token",
        "womenclub_client_token",
        "womenClubAdminAccessToken",
        "startsWith('/uploads/')",
    ):
        assert preserved_marker in source or preserved_marker in styles

    for removed_lotus_marker in (
        "reference-lotus-layer",
        "lotus-layer",
        "lotus-decor",
        "--user-lotus-reference-svg",
        "--lotus-reference-background",
        "/assets/lotus-bg.png",
    ):
        assert removed_lotus_marker not in source
        assert removed_lotus_marker not in styles


def test_frontend_contains_admin_content_review_queue_markers() -> None:
    source = _frontend_main()
    styles = _frontend_styles()
    admin_endpoints = _admin_endpoints()

    for expected in (
        "На проверке",
        "Материалов на проверке нет",
        "Здесь появляются новые предложения и фото",
        "Активировать",
        "Фото галереи",
        "content-review",
        "content-review-card",
        "content-review-preview",
        "/api/v1/admin/content-review",
        "/api/v1/admin/offers/${offerId}",
        "/api/v1/admin/offers/",
        "/api/v1/admin/partner-photos/${photoId}",
        "/api/v1/admin/partner-photos/",
    ):
        assert expected in source or expected in styles or expected in admin_endpoints

    for expected_style in (
        ".content-review",
        ".content-review-section",
        ".content-review-card",
        ".content-review-preview",
        ".content-review-actions",
        ".content-review-empty",
    ):
        assert expected_style in styles

    for preserved_marker in (
        "Новое предложение появится у клиентов после проверки и активации администратором.",
        "Предложение отправлено на проверку. После активации администратором оно появится у клиентов.",
        "Новые фото появятся в витрине после проверки и активации администратором.",
        "Фото загружено и отправлено на проверку.",
        "Ожидает активации администратором.",
        "/api/v1/partners/me/activity",
        "/api/v1/partners/me/analytics",
        "/api/v1/admin/activity",
        "offer-image-uploader",
        "partner-image-uploader",
        "partner-gallery",
        "partner-gallery-grid",
        "offer-marketplace-card",
        "partner-marketplace-card",
        "data-privilege-success-panel",
        "data-client-privilege-card",
        "setup_token",
        "/api/v1/auth/password-setup/complete",
        "/api/v1/public/landing/partners",
        "/api/v1/clients/catalog/partners",
        "womenclub_partner_token",
        "womenclub_client_token",
        "womenClubAdminAccessToken",
    ):
        assert preserved_marker in source or preserved_marker in styles

    for removed_lotus_marker in (
        "reference-lotus-layer",
        "lotus-layer",
        "lotus-decor",
        "--user-lotus-reference-svg",
        "--lotus-reference-background",
        "/assets/lotus-bg.png",
    ):
        assert removed_lotus_marker not in source
        assert removed_lotus_marker not in styles
