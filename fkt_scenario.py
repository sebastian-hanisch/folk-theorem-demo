"""Szenario: das Gefangenendilemma 5/3/1/0 als Stufenspiel. Vier Aktionsprofile, ihre Auszahlungen und was ein Abweichen je Profil bringt."""

import fkt_constants as C


def stage_payoff(own: int, other: int) -> float:
    """Auszahlung einer Runde für die eigene Aktion gegen die des anderen (0 = C, 1 = D)."""
    if own == C.COOPERATE:
        return C.R if other == C.COOPERATE else C.S
    return C.T if other == C.COOPERATE else C.P


def profile_payoff(profile: tuple[int, int]) -> tuple[float, float]:
    """Auszahlungspaar (A, B) eines Aktionsprofils."""
    a, b = profile
    return stage_payoff(a, b), stage_payoff(b, a)


def deviation_gain(profile: tuple[int, int], player: int) -> float:
    """Was `player` (0 = A, 1 = B) in dieser Runde durch einseitiges Abweichen gewinnt (mindestens 0)."""
    own, other = (profile[0], profile[1]) if player == 0 else (profile[1], profile[0])
    best = max(stage_payoff(C.COOPERATE, other), stage_payoff(C.DEFECT, other))
    return best - stage_payoff(own, other)


STAGE_POINTS = tuple(profile_payoff(p) for p in C.PROFILES)    # (3,3), (0,5), (5,0), (1,1)
