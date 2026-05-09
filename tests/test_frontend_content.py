from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = REPO_ROOT / "frontend"
FRONTEND_INDEX = FRONTEND_DIR / "index.html"
FRONTEND_MAIN = FRONTEND_DIR / "src" / "main.js"
FRONTEND_STYLES = FRONTEND_DIR / "src" / "styles.css"

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


def _frontend_public_sources() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in (FRONTEND_INDEX, FRONTEND_MAIN)
    )


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


def test_frontend_contains_lotus_line_art_background() -> None:
    source = _frontend_main()
    styles = _frontend_styles()

    assert "--lotus-line-art" in styles
    assert "--lotus-botanical-line-art" in styles or "botanical-lotus" in styles
    assert "viewBox='0%200%20500%20520'" in styles
    assert "stroke-linecap='round'" in styles
    assert "stroke-linejoin='round'" in styles
    assert "lotus-layer" in source
    assert "lotus-decor" in source
    assert "lotus-layer--public" in source
    assert "lotus-layer--dashboard" in source
    assert "dashboard-shell" in source

    for expected_class in (
        "lotus-decor--bottom-left",
        "lotus-decor--bottom-right",
        "lotus-decor--top-soft",
    ):
        assert expected_class in source
        assert expected_class in styles

    for expected in (
        "Женский клуб",
        "Федеральный клуб привилегий для девушек",
        "Новосибирск",
        "Череповец",
        "womenClubAdminAccessToken",
        "womenclub_partner_token",
        "womenclub_client_token",
    ):
        assert expected in source


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
