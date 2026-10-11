"""Folk-Theorem: was Wiederholung tragen kann - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Fünftes Stück der Wiederholte-Spiele-Linie: Welche Paare mittlerer Auszahlungen trägt das unendlich wiederholte Gefangenendilemma als Gleichgewicht?
Die zulässige Menge, die stationär tragbare Menge (Trigger-Strategien) und die volle Gleichgewichtsmenge (Abreu, Pearce, Stacchetti), je Schatten der Zukunft.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import fkt_constants as C
import fkt_evaluation as E
from fkt_evaluation import Settings, fmt
from fkt_presets import (
    apply_preset,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    sync_query_params,
)
from fkt_visualization import build_alternation, build_areas, build_sets

st.set_page_config(page_title="Folk-Theorem: was Wiederholung tragen kann – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return E.analyse(settings)


@st.cache_data(show_spinner=False)
def _grid(delta):
    return E.trigger_grid(delta)


@st.cache_data(show_spinner=False)
def _areas():
    return E.area_curves()


@st.cache_data(show_spinner=False)
def _alternation():
    return E.alternation_curves()


st.title("🎼 Folk-Theorem: was Wiederholung tragen kann")
st.markdown(
    """
Zwei Spediteure spielen unendlich oft dasselbe Dilemma. Welche **mittleren Auszahlungen** (A, B) können als Gleichgewicht herauskommen? Das
**Folk-Theorem** sagt: bei genügend langer Beziehung fast **alle**, die beide besser stellen als das, was jeder sich durch ständiges Defektieren
sichern kann. Diese Demo zeichnet diese Mengen für jeden Schatten der Zukunft δ und rechnet für ein gewähltes Paar nach, ob und womit es trägt.

Der überraschende Teil: Die Menge ist **groß** (schon ab δ = 1/2 die ganze Region), und sie enthält **auch sehr ungleiche** Paare. Das Folk-Theorem erklärt
also nicht, was passiert, sondern was passieren *könnte*; welches Gleichgewicht gespielt wird, sagt es nicht.

Weiter unten: **❓ Kernfrage**, drei Experimente (**🔬**), **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**. Vorgänger sind
[tit-for-tat-demo](https://sebastianhanisch-tit-for-tat-demo.streamlit.app/) (ab wann trägt Kooperation) und
[replikator-demo](https://sebastianhanisch-replikator-demo.streamlit.app/) (welche Strategie hält sich in einer Population).
"""
)

with st.expander("So wird ein Auszahlungspaar tragbar", expanded=True):
    st.markdown(
        """
1. **Zielpaar wählen** (A, B): es muss zulässig sein (Mischung der vier Stufenauszahlungen 3/3, 0/5, 5/0, 1/1) und beide mindestens **1** bekommen, denn
   ständiges Defektieren sichert jedem 1.
2. **Pfad bauen:** Die Spieler losen jede Runde mit einer Zufallsvorrichtung, die beide sehen, ein Aktionsprofil aus; die Gewichte ergeben im Mittel das
   Zielpaar.
3. **Strafe androhen:** Wer abweicht, löst dauerhafte gegenseitige Defektion aus (Auszahlung 1 für beide). Das ist die schärfste mögliche Strafe.
4. **Prüfen:** In jedem Profil muss der Wert der Weiterspielens, abgezinst, mindestens so groß sein wie der Gewinn aus dem Abweichen plus der Strafwert.
        """
    )

with st.expander("Die zwei Konstruktionen: wer macht was?", expanded=True):
    alt_now = E.alternation(st.session_state.get("delta_slider", C.DEFAULT_DELTA))
    st.markdown(
        "Zwei Arten, ein Paar zu tragen. Die **Trigger-Strategie** ist stationär: in jeder Runde dieselbe Mischung, bei Abweichen für immer Strafe. Das **Abwechseln** "
        "ist nicht stationär: A wird ausgebeutet, dann B, dann wieder A. Dass das Gleichgewicht ist, liegt allein an der Strafe."
    )
    st.markdown(
        "| Konstruktion | Verhalten | Trägt das Paar | Ab welchem δ |\n|---|---|---|---|\n"
        "| **Trigger** | Jede Runde ein Profil aus der Mischung; bei Abweichen für immer gegenseitige Defektion. | z. B. (3 / 3) durch dauerhafte Kooperation | 1/2 |\n"
        "| **Abwechseln** | A kooperiert, B defektiert; in der nächsten Runde umgekehrt. Bei Abweichen für immer gegenseitige Defektion. | "
        "ungleiche Paare je nach Phase, gemischt auch (2,5 / 2,5); Paare mit Summe höchstens 5 | 1/4 |"
    )
    st.caption(
        f"Beim aktuellen δ (Regler) ist der Wert im Abwechseln für den gerade Ausgebeuteten {fmt(alt_now['exploited'])}, für den Ausbeutenden {fmt(alt_now['exploiter'])}; "
        f"Abweichen brächte {fmt(alt_now['deviation'])}: {'Abwechseln trägt' if alt_now['holds'] else 'Abwechseln trägt nicht'}."
    )

st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
cols = st.columns(len(C.PRESETS))
for col, name in zip(cols, C.PRESETS):
    with col:
        st.button(name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}")

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    st.markdown("**Beziehung**")
    delta = st.slider("Schatten der Zukunft δ", *bounds("delta_slider"), step=C.DELTA_STEP, key="delta_slider",
                      help="Wahrscheinlichkeit, dass die Beziehung eine Runde weiterläuft. Erwartete Dauer: 1 / (1 − δ) Runden.")
    st.markdown("**Zielpaar der mittleren Auszahlungen**")
    v1 = st.slider("Mittlere Auszahlung A", *bounds("v1_slider"), step=C.V_STEP, key="v1_slider", help="Was A im Mittel je Runde bekommt.")
    v2 = st.slider("Mittlere Auszahlung B", *bounds("v2_slider"), step=C.V_STEP, key="v2_slider", help="Was B im Mittel je Runde bekommt.")

sync_query_params({"delta_slider": round(float(delta), 2), "v1_slider": round(float(v1), 1), "v2_slider": round(float(v2), 1)})

settings = Settings(round(float(delta), 2), round(float(v1), 1), round(float(v2), 1))
an = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🗺️ Welche Paare trägt die Wiederholung?")
m1, m2, m3 = st.columns(3)
m1.metric("Fläche aller Gleichgewichte", fmt(an.area_aps), delta=f"von {fmt(an.area_feasible)} zulässig und rational", delta_color="off")
m2.metric("Fläche stationär tragbar (Trigger)", fmt(an.area_trigger), delta=f"{fmt(an.area_trigger / an.area_feasible * 100, 0)} % der zulässigen Region", delta_color="off")
m3.metric("Erwartete Beziehungsdauer", f"{fmt(1 / (1 - settings.delta), 1)} Runden", delta="1 / (1 − δ)", delta_color="off")
st.plotly_chart(build_sets(settings.delta, an.aps_polygon, _grid(settings.delta), (settings.v1, settings.v2)), width="stretch", key="sets_chart")
st.caption("Hellgrau: alle zulässigen Paare (Hülle von 3/3, 0/5, 5/0, 1/1). Dunkelgrau: dazu beide mindestens 1. Blau: alle Gleichgewichte bei diesem δ. Grün: davon "
           "die mit einer einfachen Trigger-Strategie tragbaren. Rotes Kreuz: Ihr Zielpaar.")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Trägt die Wiederholung dieses Paar?")
level, sentence = E.verdict(an, settings)
{"success": st.success, "warning": st.warning, "info": st.info, "error": st.error}[level](sentence)
st.markdown("---")

# --- Experiment 1 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Ab welchem δ wird das gewählte Paar tragbar?")
st.caption("Kleinstes δ, ab dem das Zielpaar als Gleichgewicht trägt, einmal mit einer einfachen Trigger-Strategie und einmal mit beliebigen Strategien.")
rows = ["| Konstruktion | Schwelle |", "|---|---|"]
rows.append(f"| Stationäre Trigger-Strategie | {'δ ≥ ' + fmt(an.threshold_trigger, 3) if an.threshold_trigger is not None else 'nie'} |")
rows.append(f"| Beliebige Strategien (alle Gleichgewichte) | {'δ ≥ ' + fmt(an.threshold_aps, 3) if an.threshold_aps is not None else 'nie'} |")
st.markdown("\n".join(rows))
if an.threshold_trigger is not None and an.threshold_aps is not None and an.threshold_trigger > an.threshold_aps + 1e-6:
    st.info(f"Die einfache Trigger-Strategie braucht δ ≥ {fmt(an.threshold_trigger, 2)}, mit anderen Strategien reicht schon δ ≥ {fmt(an.threshold_aps, 2)}: "
            "ein Teil der tragbaren Paare lässt sich nur nicht-stationär erzeugen.")
st.markdown("---")

# --- Experiment 2 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Wie wächst die tragbare Menge mit dem Schatten der Zukunft?")
st.caption("Fläche der tragbaren Menge über δ: alle Gleichgewichte (blau) gegen stationär tragbare (grün), dazu die ganze zulässige und individuell rationale Region (gepunktet).")
curves = _areas()
st.plotly_chart(build_areas(curves), width="stretch", key="area_chart")
st.info(
    "Die Menge aller Gleichgewichte hat drei Phasen: **unter δ = 1/4 nur (1 / 1)**, **von 1/4 bis 1/2 genau ein Dreieck** (nur Paare, deren Summe höchstens 5 ist, "
    "also ohne gegenseitige Kooperation), **ab δ = 1/2 die ganze zulässige, individuell rationale Region**. Die einfache Trigger-Strategie erreicht dieselbe Region "
    "erst allmählich gegen δ = 1."
)
st.markdown("---")

# --- Experiment 3 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Warum trägt Abwechseln schon ab δ = 1/4?")
st.caption("Im Wechsel wird A ausgebeutet und danach B. Der Ausgebeutete hält mit, solange sein Wert im Wechsel mindestens 1 ist, was er durch Abweichen bekäme.")
st.plotly_chart(build_alternation(_alternation()), width="stretch", key="alt_chart")
st.info("Der Wert des Ausgebeuteten ist (S + δ·T)/(1 + δ) = 5δ/(1 + δ) und erreicht 1 genau bei δ = 1/4. Das ist die Schwelle, ab der der Wechsel trägt, und damit die "
        "untere Grenze des Dreiecks in Experiment 2.")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Öffentliche Zufallsvorrichtung** | Ohne sie sind nur Paare tragbar, die sich als Zeitmittel eines festen Pfades ergeben; die Region wird zackig, ihre Grundform bleibt. | - |
| **Strafe: ewige gegenseitige Defektion** | Sie ist die schärfste mögliche, aber wenig glaubwürdig: beide würden lieber neu verhandeln. Neuverhandlungsfeste Gleichgewichte sind eine kleinere Menge und hier nicht gerechnet. | - |
| **Beide beobachten alles fehlerfrei** | Bei Fehlern oder privater Beobachtung ändert sich die Menge; Strafen werden zu teuer. | `rauschen-kooperation-demo` zeigt, was ein Fehler anrichtet |
| **Genau zwei Spieler, feste Auszahlungen 5/3/1/0** | Die Auszahlungen sind gewählt, nicht gemessen; die Schwellen 1/4 und 1/2 hängen an ihnen. | - |
| **Folk-Theorem ≠ Vorhersage** | Es sagt, was Gleichgewicht sein *kann*, nicht, was gespielt wird. Fast alles in der Region ist gleichberechtigt. | `replikator-demo` fragt, welche sich in Populationen halten |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Zulässige Menge.** Die Hülle der Stufenauszahlungen $u(C,C) = (3,3)$, $u(C,D) = (0,5)$, $u(D,C) = (5,0)$, $u(D,D) = (1,1)$. **Individuell rational:**
$v_i \ge \underline v_i = P = 1$, der Minimaxwert (bei beidseitiger Defektion).

**Anreiz je Profil.** Mit normierten Werten (Gewicht $1 - \delta$ auf die laufende Runde) weicht Spieler $i$ im Profil $a$ nicht ab, wenn
$(1-\delta)\,g_i(a) \le \delta\,(w_i - P)$, mit dem Gewinn $g_i(a)$ aus dem Abweichen und der Fortsetzung $w$. Also $w_i \ge P + \tfrac{1-\delta}{\delta}\,g_i(a)$. Bei
$(C,C)$ ist $g = T - R = 2$.

**Stationär tragbar (Trigger).** Das Paar $v$ ist tragbar, wenn es in der Hülle der Profile $a$ liegt, für die $v_i \ge P + \tfrac{1-\delta}{\delta} g_i(a)$ für beide
Spieler gilt. Für $v = (3,3)$ ergibt das $\delta \ge \tfrac{T-R}{T-P} = \tfrac12$.

**Alle Gleichgewichte (APS).** Abreu, Pearce und Stacchetti: Die Menge $W$ aller Gleichgewichtsauszahlungen ist die größte Menge mit $W \subseteq B(W)$, wobei
$B(W)$ die Hülle aller $(1-\delta)\,u(a) + \delta\,w$ mit $w \in W$ und $w_i \ge P + \tfrac{1-\delta}{\delta} g_i(a)$ ist. Die Iteration $W \leftarrow B(W)$ von der
zulässigen, individuell rationalen Menge aus fällt gegen $W$. Weil die Strafe $(P,P)$ sowohl Minimax als auch Gleichgewicht des Stufenspiels ist, ist sie die
schärfstmögliche und $W$ die volle Menge der Gleichgewichtsauszahlungen mit öffentlicher Zufallsvorrichtung.

**Abwechseln.** Wert für den Ausgebeuteten $(S + \delta T)/(1+\delta)$, für den Ausbeutenden $(T + \delta S)/(1+\delta)$. Anreiz: $(S + \delta T)/(1+\delta) \ge P$, also
$\delta \ge \tfrac{P-S}{T-P} = \tfrac14$.

**Literatur.** Friedman (1971), *A non-cooperative equilibrium for supergames*, Review of Economic Studies 38, 1–12 (Trigger-Strategie mit ewiger Strafe; später
berichtigt); Fudenberg und Maskin (1986), *The folk theorem in repeated games with discounting or with incomplete information*, Econometrica 54, 533–554
(jedes individuell rationale Paar ist für geduldige Spieler teilspielperfekt tragbar, bei zwei Spielern ohne weitere Bedingung); Abreu, Pearce und Stacchetti
(1990), *Toward a theory of discounted repeated games with imperfect monitoring*, Econometrica 58, 1041–1063 (Selbsterzeugung, Monotonie der Wertemenge im
Diskontfaktor, Iterationsverfahren). Nur Zusammenfassungen gelesen, nicht die Volltexte. Die Schwellen 1/4 und 1/2 für 5/3/1/0 und die Aussage „ab δ = 1/2 die
ganze Region“ sind hier gerechnet (LP-Orakel in den Tests), nicht aus der Literatur übernommen.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
