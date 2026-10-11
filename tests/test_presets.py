"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, Permalink-Begrenzen."""

import fkt_constants as C
import fkt_evaluation as ev
import fkt_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds():
    for name, preset in C.PRESETS.items():
        assert C.DELTA_MIN <= preset["delta"] <= C.DELTA_MAX, name
        assert C.V_MIN <= preset["v1"] <= C.V_MAX and C.V_MIN <= preset["v2"] <= C.V_MAX, name


def test_default_preset_equals_the_default_settings():
    first = next(iter(C.PRESETS.values()))
    assert ev.Settings(first["delta"], first["v1"], first["v2"]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_clamp_limits_numbers():
    spec = P.SETTING_SPECS["delta_slider"]
    assert P.clamp(spec, 2.0) == C.DELTA_MAX and P.clamp(spec, 0.0) == C.DELTA_MIN
