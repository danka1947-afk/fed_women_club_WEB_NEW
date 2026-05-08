from pathlib import Path
import re

FRONTEND_MAIN = Path(__file__).resolve().parents[1] / "frontend" / "src" / "main.js"


def _frontend_main() -> str:
    return FRONTEND_MAIN.read_text(encoding="utf-8")


def _city_options() -> list[str]:
    source = _frontend_main()
    match = re.search(r"const cities = \[(.*?)\];", source, re.S)
    assert match is not None
    return re.findall(r"'([^']+)'", match.group(1))


def test_brand_copy_targets_girls() -> None:
    source = _frontend_main()

    assert "Федеральный клуб привилегий для девушек" in source
    assert "Федеральный клуб привилегий для женщин" not in source


def test_frontend_city_selector_options_are_limited_to_active_cities() -> None:
    assert _city_options() == ["Новосибирск", "Череповец"]


def test_removed_cities_are_not_in_frontend_city_selector() -> None:
    cities = _city_options()

    assert "Москва" not in cities
    assert "Санкт-Петербург" not in cities
    assert "Екатеринбург" not in cities
    assert "Казань" not in cities


def test_city_growth_note_is_present() -> None:
    assert (
        "Чем больше мы растём, тем больше городов подключаем. "
        "Скоро появятся новые города."
    ) in _frontend_main()
