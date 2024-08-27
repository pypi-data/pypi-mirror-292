import pytest
from kanjex.conjugator import IRREGULAR, conjugate, assert_verb_type

irregular_plain_cases = pytest.mark.parametrize("verb, make_negative, make_past_tense, expected", [
    ("する", False, False, "する"),
    ("する", True, False, "しない"),
    ("する", False, True, "した"),
    ("する", True, True, "しなかった"),
    ("来る", False, False, "来る"),
    ("来る", True, False, "来ない"),
    ("来る", False, True, "来た"),
    ("来る", True, True, "来なかった"),
])

@irregular_plain_cases
def test_plain(verb, make_negative, make_past_tense, expected):
    assert_verb_type(verb, IRREGULAR)
    conjugated = conjugate(verb, "plain", make_negative, make_past_tense)
    assert conjugated == expected, f"[{verb}] Expected {expected}, got {conjugated}."

irregular_polite_cases = pytest.mark.parametrize("verb, make_negative, make_past_tense, expected", [
    ("する", False, False, "します"),
    ("する", True, False, "しません"),
    ("する", False, True, "しました"),
    ("する", True, True, "しませんでした"),
    ("来る", False, False, "来ます"),
    ("来る", True, False, "来ません"),
    ("来る", False, True, "来ました"),
    ("来る", True, True, "来ませんでした"),
])

@irregular_polite_cases
def test_polite(verb, make_negative, make_past_tense, expected):
    assert_verb_type(verb, IRREGULAR)
    conjugated = conjugate(verb, "polite", make_negative, make_past_tense)
    assert conjugated == expected, f"[{verb}] Expected {expected}, got {conjugated}."

irregular_te_cases = pytest.mark.parametrize("verb, make_negative, expected, make_past_tense", [
    ("する", False, False, "して"),
    ("する", True, False, "しなくて"),
    ("する", False, True, "していた"),  # This would typically be used in continuous forms
    ("する", True, True, "しなくていた"),  # Negative past continuous (less common)
    ("来る", False, False, "来て"),
    ("来る", True, False, "来なくて"),
    ("来る", False, True, "来ていた"),  # Continuous past
    ("来る", True, True, "来なくていた"),  # Negative continuous past
])

@irregular_te_cases
def test_te(verb, make_negative, make_past_tense, expected):
    assert_verb_type(verb, IRREGULAR)
    conjugated = conjugate(verb, "te", make_negative, make_past_tense)
    assert conjugated == expected, f"[{verb}] Expected {expected}, got {conjugated}."


# Define the test cases for the irregular Desire form
irregular_desire_cases = pytest.mark.parametrize("verb, make_negative, make_past_tense, expected", [
    ("する", False, False, "したい"),  # Desire form for "する"
    ("する", True, False, "したくない"),  # Negative Desire form for "する"
    ("する", False, True, "したかった"),  # Past Desire form for "する"
    ("する", True, True, "したくなかった"),  # Negative Past Desire form for "する"
    ("来る", False, False, "来たい"),  # Desire form for "来る"
    ("来る", True, False, "来たくない"),  # Negative Desire form for "来る"
    ("来る", False, True, "来たかった"),  # Past Desire form for "来る"
    ("来る", True, True, "来たくなかった"),  # Negative Past Desire form for "来る"
])

@irregular_desire_cases
def test_desire(verb, make_negative, make_past_tense, expected):
    assert_verb_type(verb, IRREGULAR)
    conjugated = conjugate(verb, "desire", make_negative, make_past_tense)
    assert conjugated == expected, f"[{verb}] Expected {expected}, got {conjugated}."


# Define the test cases for the irregular Conditional form
irregular_conditional_cases = pytest.mark.parametrize("verb, make_negative, make_past_tense, expected", [
    ("する", False, False, "すれば"),  # Conditional form for "する"
    ("する", True, False, "しなければ"),  # Negative Conditional form for "する"
    ("する", False, True, "すればよかった"),  # Past Conditional form for "する"
    ("する", True, True, "しなければよかった"),  # Negative Past Conditional form for "する"
    ("来る", False, False, "来れば"),  # Conditional form for "来る"
    ("来る", True, False, "来なければ"),  # Negative Conditional form for "来る"
    ("来る", False, True, "来ればよかった"),  # Past Conditional form for "来る"
    ("来る", True, True, "来なければよかった"),  # Negative Past Conditional form for "来る"
])

@irregular_conditional_cases
def test_conditional(verb, make_negative, make_past_tense, expected):
    assert_verb_type(verb, IRREGULAR)
    conjugated = conjugate(verb, "conditional", make_negative, make_past_tense)
    assert conjugated == expected, f"[{verb}] Expected {expected}, got {conjugated}."


# Define the test cases for the irregular Potential form
irregular_potential_cases = pytest.mark.parametrize("verb, make_negative, make_past_tense, expected", [
    ("する", False, False, "できる"),  # Potential form for "する"
    ("する", True, False, "できない"),  # Negative Potential form for "する"
    ("する", False, True, "できた"),  # Past Potential form for "する"
    ("する", True, True, "できなかった"),  # Negative Past Potential form for "する"
    ("来る", False, False, "来られる"),  # Potential form for "来る"
    ("来る", True, False, "来られない"),  # Negative Potential form for "来る"
    ("来る", False, True, "来られた"),  # Past Potential form for "来る"
    ("来る", True, True, "来られなかった"),  # Negative Past Potential form for "来る"
])

@irregular_potential_cases
def test_potential(verb, make_negative, make_past_tense, expected):
    assert_verb_type(verb, IRREGULAR)
    conjugated = conjugate(verb, "potential", make_negative, make_past_tense)
    assert conjugated == expected, f"[{verb}] Expected {expected}, got {conjugated}."


# Define the test cases for the irregular Imperative form
irregular_imperative_cases = pytest.mark.parametrize("verb, make_negative, make_past_tense, expected", [
    ("する", False, False, "しろ"),  # Imperative form for "する"
    ("する", True, False, "するな"),  # Negative Imperative form for "する"
    ("来る", False, False, "来い"),  # Imperative form for "来る"
    ("来る", True, False, "来るな"),  # Negative Imperative form for "来る"
])

@irregular_imperative_cases
def test_imperative(verb, make_negative, make_past_tense, expected):
    assert_verb_type(verb, IRREGULAR)
    conjugated = conjugate(verb, "imperative", make_negative, make_past_tense)
    assert conjugated == expected, f"[{verb}] Expected {expected}, got {conjugated}."

# Define the test cases for the irregular Volitional form
irregular_volitional_cases = pytest.mark.parametrize("verb, make_negative, make_past_tense, expected", [
    ("する", False, False, "しよう"),  # Volitional form for "する"
    ("する", True, False, "するまい"),  # Negative Volitional form for "する"
    ("来る", False, False, "来よう"),  # Volitional form for "来る"
    ("来る", True, False, "来るまい"),  # Negative Volitional form for "来る"
])

@irregular_volitional_cases
def test_volitional(verb, make_negative, make_past_tense, expected):
    assert_verb_type(verb, IRREGULAR)
    conjugated = conjugate(verb, "volitional", make_negative, make_past_tense)
    assert conjugated == expected, f"[{verb}] Expected {expected}, got {conjugated}."

# Define the test cases for the irregular Passive form
irregular_passive_cases = pytest.mark.parametrize("verb, make_negative, make_past_tense, expected", [
    ("する", False, False, "される"),  # Passive form for "する"
    ("する", True, False, "されない"),  # Negative Passive form for "する"
    ("する", False, True, "された"),  # Past Passive form for "する"
    ("する", True, True, "されなかった"),  # Negative Past Passive form for "する"
    ("来る", False, False, "来られる"),  # Passive form for "来る"
    ("来る", True, False, "来られない"),  # Negative Passive form for "来る"
    ("来る", False, True, "来られた"),  # Past Passive form for "来る"
    ("来る", True, True, "来られなかった"),  # Negative Past Passive form for "来る"
])

@irregular_passive_cases
def test_passive(verb, make_negative, make_past_tense, expected):
    assert_verb_type(verb, IRREGULAR)
    conjugated = conjugate(verb, "passive", make_negative, make_past_tense)
    assert conjugated == expected, f"[{verb}] Expected {expected}, got {conjugated}."


# Define the test cases for the irregular Causative form
irregular_causative_cases = pytest.mark.parametrize("verb, make_negative, make_past_tense, expected", [
    ("する", False, False, "させる"),  # Causative form for "する"
    ("する", True, False, "させない"),  # Negative Causative form for "する"
    ("する", False, True, "させた"),  # Past Causative form for "する"
    ("する", True, True, "させなかった"),  # Negative Past Causative form for "する"
    ("来る", False, False, "来させる"),  # Causative form for "来る"
    ("来る", True, False, "来させない"),  # Negative Causative form for "来る"
    ("来る", False, True, "来させた"),  # Past Causative form for "来る"
    ("来る", True, True, "来させなかった"),  # Negative Past Causative form for "来る"
])

@irregular_causative_cases
def test_causative(verb, make_negative, make_past_tense, expected):
    assert_verb_type(verb, IRREGULAR)
    conjugated = conjugate(verb, "causative", make_negative, make_past_tense)
    assert conjugated == expected, f"[{verb}] Expected {expected}, got {conjugated}."


# Define the test cases for the irregular Progressive form
irregular_progressive_cases = pytest.mark.parametrize("verb, make_negative, make_past_tense, expected", [
    ("する", False, False, "している"),  # Progressive form for "する"
    ("する", True, False, "していない"),  # Negative Progressive form for "する"
    ("する", False, True, "していた"),  # Past Progressive form for "する"
    ("する", True, True, "していなかった"),  # Negative Past Progressive form for "する"
    ("来る", False, False, "来ている"),  # Progressive form for "来る"
    ("来る", True, False, "来ていない"),  # Negative Progressive form for "来る"
    ("来る", False, True, "来ていた"),  # Past Progressive form for "来る"
    ("来る", True, True, "来ていなかった"),  # Negative Past Progressive form for "来る"
])

@irregular_progressive_cases
def test_progressive(verb, make_negative, make_past_tense, expected):
    assert_verb_type(verb, IRREGULAR)
    conjugated = conjugate(verb, "progressive", make_negative, make_past_tense)
    assert conjugated == expected, f"[{verb}] Expected {expected}, got {conjugated}."

# Define the test cases for the irregular Perfective form
irregular_perfective_cases = pytest.mark.parametrize("verb, make_negative, make_past_tense, expected", [
    ("する", False, False, "した"),  # Perfective form for "する"
    ("する", True, False, "しない"),  # Negative Perfective form for "する" (uncommon)
    ("する", False, True, "していた"),  # Past Perfective form for "する"
    ("する", True, True, "していなかった"),  # Negative Past Perfective form for "する"
    ("来る", False, False, "来た"),  # Perfective form for "来る"
    ("来る", True, False, "来ない"),  # Negative Perfective form for "来る" (uncommon)
    ("来る", False, True, "来ていた"),  # Past Perfective form for "来る"
    ("来る", True, True, "来ていなかった"),  # Negative Past Perfective form for "来る"
])

@irregular_perfective_cases
def test_perfective(verb, make_negative, make_past_tense, expected):
    assert_verb_type(verb, IRREGULAR)
    conjugated = conjugate(verb, "perfective", make_negative, make_past_tense)
    assert conjugated == expected, f"[{verb}] Expected {expected}, got {conjugated}."
