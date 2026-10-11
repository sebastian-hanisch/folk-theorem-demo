"""Permalink (Begrenzen), Presets und Zustand der Regler."""

from dataclasses import dataclass

import streamlit as st

import fkt_constants as C


@dataclass(frozen=True)
class SettingSpec:
    url_param: str
    caster: type
    default: object
    lo: float
    hi: float


SETTING_SPECS = {
    "delta_slider": SettingSpec("delta", float, C.DEFAULT_DELTA, C.DELTA_MIN, C.DELTA_MAX),
    "v1_slider": SettingSpec("v1", float, C.DEFAULT_V1, C.V_MIN, C.V_MAX),
    "v2_slider": SettingSpec("v2", float, C.DEFAULT_V2, C.V_MIN, C.V_MAX),
}
PRESET_KEYS = {"delta": "delta_slider", "v1": "v1_slider", "v2": "v2_slider"}


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec.default


def bounds(state_key):
    spec = SETTING_SPECS[state_key]
    return spec.lo, spec.hi


def clamp(spec: SettingSpec, value):
    return min(spec.hi, max(spec.lo, value))


def load_permalink_settings():
    """Einmal je Sitzung: Werte aus der Adresszeile übernehmen, auf die Reglergrenzen begrenzt."""
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec.url_param not in qp:
            continue
        raw = qp[spec.url_param]
        if isinstance(raw, list):
            raw = raw[0] if raw else ""
        try:
            value = spec.caster(raw)
        except (ValueError, TypeError):
            continue
        st.session_state[state_key] = clamp(spec, value)
    st.session_state["permalink_loaded"] = True


def sync_query_params(values):
    try:
        for state_key, value in values.items():
            st.query_params[SETTING_SPECS[state_key].url_param] = str(value)
    except Exception:
        pass


def apply_preset(name):
    for key, state_key in PRESET_KEYS.items():
        if key in C.PRESETS[name]:
            st.session_state[state_key] = C.PRESETS[name][key]
