# Folk-Theorem: was Wiederholung tragen kann – Streamlit-Demo

<!-- Nach dem Deploy direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-folk-theorem-demo.streamlit.app/)** -->

Fünftes Stück der **Wiederholte-Spiele-Linie** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“.
Vorgänger sind [tit-for-tat-demo](https://sebastianhanisch-tit-for-tat-demo.streamlit.app/) (ab wann trägt Kooperation) und
[replikator-demo](https://sebastianhanisch-replikator-demo.streamlit.app/) (welche Strategie hält sich). Hier die allgemeine Frage: **Welche Paare mittlerer
Auszahlungen kann die Wiederholung überhaupt als Gleichgewicht tragen?** Die Kante ist ein `kontrast`: dieselbe Frage nach dem Tragen, aber nicht für eine bestimmte
Strategie, sondern für die ganze Menge der Gleichgewichte.

Vehikel: der Rückladungstausch mit den Auszahlungen 5/3/1/0 (gewählt, nicht gemessen), zwei Spediteure, unendlich oft wiederholt, Fortsetzungswahrscheinlichkeit δ.

## Warum dieses Problem

Das Folk-Theorem (Friedman 1971, Fudenberg/Maskin 1986) sagt: bei genügend langer Beziehung ist fast jedes Auszahlungspaar tragbar, das beide besser stellt als ihr
Minimum. Interessant ist, **wie groß die Menge bei gegebenem δ ist, ab wann sie alles umfasst, und was Strafdrohungen und Wechsel dafür leisten müssen**. Und: dass
„tragbar“ keine Vorhersage ist.

## Modell

Vier Aktionsprofile mit den Auszahlungen (3/3), (0/5), (5/0), (1/1). Zulässig ist die Hülle dieser Punkte, individuell rational sind Paare mit beiden mindestens 1
(ständiges Defektieren sichert jedem 1). Anreiz je Profil: nur mitspielen, wenn die abgezinste Fortsetzung den Gewinn aus dem Abweichen plus den Strafwert 1 übertrifft,
also `w_i ≥ P + (1−δ)/δ · Gewinn_i`. Mit öffentlicher Zufallsvorrichtung (beide sehen denselben Münzwurf). Zwei Mengen:
**stationär tragbar** (jede Runde dieselbe Mischung, bei Abweichen ewige Defektion) und **alle Gleichgewichte** (Abreu/Pearce/Stacchetti: größte selbsterzeugende Menge).

## Methodik

- **Trigger-Menge:** `allowed_profiles`, `trigger_weights`: die Mischung nur über die Profile, die mit dem Zielpaar als Fortsetzung anreizverträglich sind.
- **Alle Gleichgewichte:** `aps_set`: Iteration `W ← B(W)` mit konvexen Polygonen (Hülle, Halbebenen-Beschnitt), startend von der zulässigen, individuell rationalen Menge.
- **Schwellen:** `threshold_delta`: Bisektion; beide Mengen wachsen mit δ.
- **Flächen:** exakt für die APS-Polygone, Raster mit Schritt 0,025 für die Trigger-Menge (vektorisiert).

## Befunde (gemessen, keine Behauptungen)

Auszahlungen 5/3/1/0. Fläche der zulässigen, individuell rationalen Region: 20/3 = 6,667.

| Frage | Befund | Test |
|---|---|---|
| Wie sieht die Menge aller Gleichgewichte aus? | **Drei Phasen:** unter δ = 1/4 nur (1 / 1); von 1/4 bis 1/2 genau das Dreieck (1,1), (4,1), (1,4) mit Fläche 4,5 (nur Paare mit Summe höchstens 5); ab δ = 1/2 die **ganze** zulässige, individuell rationale Region. | `test_three_phases_of_the_full_equilibrium_set` |
| Woher kommen die Schwellen 1/4 und 1/2? | 1/2 = (T−R)/(T−P): gegenseitige Kooperation trägt. 1/4 = (P−S)/(T−P): im **Wechsel** (A wird ausgebeutet, dann B) erreicht der Ausgebeutete (S+δT)/(1+δ), und das ist mindestens 1 genau ab δ = 1/4. | `test_thresholds_one_quarter_and_one_half`, `test_alternating_values_by_hand` |
| Wie viel davon trägt eine einfache Trigger-Strategie? | Fläche (Raster): 0,17 bei δ = 0,45; 0,54 bei 0,5; 2,10 bei 0,6 (32 % der Region); 4,97 bei 0,8 (75 %); 6,24 bei 0,95 (94 %). Sie erreicht die volle Region erst gegen δ = 1. | `test_trigger_areas` |
| Wie unterscheiden sich die Schwellen einzelner Paare? | (3 / 3): Trigger 0,50, alle 0,50. (2,5 / 2,5): Trigger 0,40, alle 0,25. (4 / 1,5): Trigger 0,80, alle 0,50. (1 / 4): Trigger nie, alle 0,25. | `test_threshold_table_for_four_pairs` |
| Trägt (3 / 3) knapp unter 1/2? | Nein, auch nicht mit beliebigen Strategien: bei δ = 0,45 liegt (3 / 3) weder in der Trigger- noch in der vollen Menge. | `test_preset_stories`, `test_the_trigger_region_never_exceeds_the_full_set_and_never_contains_pairs_above_the_sum_bound_below_one_half` |

### Befunde gegenüber dem Plan

Der Plan sah vor, nur die **Trigger-Teilmenge** zu zeigen und die volle Gleichgewichtsmenge als Grenze zu benennen. Die Vormessung zeigte, dass die volle Menge **qualitativ
anders** ist: Schon ab δ = 1/4 trägt ein Dreieck, ab δ = 1/2 die ganze Region, während die Trigger-Menge erst gegen δ = 1 aufholt. Deshalb rechnet die Demo beide: die
einfache Konstruktion zum Erklären, die volle Menge (APS) zum Beantworten der Frage. Die Aussage „ab δ = 1/2 die ganze Region“ ist hier gerechnet und per Linearprogramm
geprüft, nicht aus der Literatur übernommen.

## Ehrliche Grenzen

- **Öffentliche Zufallsvorrichtung:** ohne sie bleibt die Grundform, aber die Region wird zackig.
- **Strafe ist ewige Defektion:** schärfstmöglich, aber nicht neuverhandlungsfest; die kleinere Menge neuverhandlungsfester Gleichgewichte ist nicht gerechnet.
- **Perfekte Beobachtung, zwei Spieler, feste Auszahlungen:** Fehler ändern die Mengen (siehe rauschen-kooperation-demo), die Schwellen hängen an 5/3/1/0.
- **Folk-Theorem ≠ Vorhersage:** es sagt, was Gleichgewicht sein kann, nicht, was gespielt wird.
- **Literatur nur über Zusammenfassungen gelesen.**

## Verifikation

- **Kern:** je Einheit eine Handrechnung (Abweichungsgewinne, Strafschwellen, erlaubte Profile, Mischungsgewichte, Polygonoperationen inklusive entarteter Fälle, die drei Phasen, Schwellen in geschlossener Form).
- **Orakel** (`tests/test_oracle_folk_theorem.py`), alle mit `scipy.optimize.linprog` und einer eigenen Auszahlungstabelle, ohne die Polygonoperationen des Kerns: (1) die
  Trigger-Zugehörigkeit als LP auf einem Raster und für 150 Zufallspunkte (vektorisiert gegen LP); (2) die APS-Menge als **Fixpunkt**: Ecken und innere Punkte liegen in B(W)
  (jeder Punkt ist ein Gleichgewicht), Punkte knapp außerhalb jeder Kante nicht (nichts Zusätzliches); (3) das Abwechseln über das lineare System der Zwei-Zustands-Strategie und die
  Schwelle 1/4; (4) Monotonie: die Mengen wachsen mit δ, und jeder Trigger-Punkt liegt in der vollen Menge.
- **Claims:** jede Zahl dieses READMEs in `tests/test_claims.py`.
- **Oberfläche:** AppTest (jeder Button, jeder Regler am Minimum und Maximum, Permalink begrenzt, beide Konstruktionen erklärt) und Footer-Test.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `requirements-dev.txt` | Laufzeit plus pytest und scipy (nur für das Orakel) |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `fkt_algorithm.py` | Kern: Strafschwellen, Trigger-Menge, Polygone, APS-Iteration, Schwellen |
| `fkt_constants.py` | Regler-Grenzen, feste Annahmen, Farben, Presets |
| `fkt_evaluation.py` | Analyse, Flächenkurven, Abwechseln, Verdikt |
| `fkt_presets.py` | Permalink (Begrenzen), Presets |
| `fkt_scenario.py` | Das Stufenspiel, Profile, Abweichungsgewinne |
| `fkt_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tests/` | Handrechnung, Orakel, Claims, Presets, AppTest-Smoke-Test, Footer |

## Bewusst nicht umgesetzt

- **Mehr als zwei Spieler, andere Stufenspiele, private Beobachtung:** eigene Modelle (für private Beobachtung ist die Menge deutlich schwerer zu berechnen).
- **Neuverhandlungsfeste Gleichgewichte:** eigener Gleichgewichtsbegriff.
- **Konkrete Strategieautomaten für jeden Punkt der APS-Menge:** die Demo zeigt, dass ein Punkt tragbar ist und mit welcher Konstruktion im stationären Fall, nicht den vollen Baum.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
