import pytest

from kanjex.conjugator import GODAN, conjugate, assert_verb_type, ConjugationForms




godan_plain_cases = pytest.mark.parametrize("verb, make_negative, make_past_tense, expected", [
    ("会う", False, False, "会う"),
    ("会う", True, False, "会わない"),
    ("会う", False, True, "会った"),
    ("会う", True, True, "会わなかった"),

    ("書く", False, False, "書く"),
    ("書く", True, False, "書かない"),
    ("書く", False, True, "書いた"),
    ("書く", True, True, "書かなかった"),

    ("話す", False, False, "話す"),
    ("話す", True, False, "話さない"),
    ("話す", False, True, "話した"),
    ("話す", True, True, "話さなかった"),

    ("泳ぐ", False, False, "泳ぐ"),
    ("泳ぐ", True, False, "泳がない"),
    ("泳ぐ", False, True, "泳いだ"),
    ("泳ぐ", True, True, "泳がなかった"),

    ("読む", False, False, "読む"),
    ("読む", True, False, "読まない"),
    ("読む", False, True, "読んだ"),
    ("読む", True, True, "読まなかった"),

    ("死ぬ", False, False, "死ぬ"),
    ("死ぬ", True, False, "死なない"),
    ("死ぬ", False, True, "死んだ"),
    ("死ぬ", True, True, "死ななかった"),

    ("買う", False, False, "買う"),
    ("買う", True, False, "買わない"),
    ("買う", False, True, "買った"),
    ("買う", True, True, "買わなかった"),

    ("切る", False, False, "切る"),
    ("切る", True, False, "切らない"),
    ("切る", False, True, "切った"),
    ("切る", True, True, "切らなかった"),

    ("踊る", False, False, "踊る"),
    ("踊る", True, False, "踊らない"),
    ("踊る", False, True, "踊った"),
    ("踊る", True, True, "踊らなかった"),

    ("急ぐ", False, False, "急ぐ"),
    ("急ぐ", True, False, "急がない"),
    ("急ぐ", False, True, "急いだ"),
    ("急ぐ", True, True, "急がなかった"),

    ("飲む", False, False, "飲む"),
    ("飲む", True, False, "飲まない"),
    ("飲む", False, True, "飲んだ"),
    ("飲む", True, True, "飲まなかった"),

    ("行く", False, False, "行く"),
    ("行く", True, False, "行かない"),
    ("行く", False, True, "行った"),
    ("行く", True, True, "行かなかった"),

    ("待つ", False, False, "待つ"),
    ("待つ", True, False, "待たない"),
    ("待つ", False, True, "待った"),
    ("待つ", True, True, "待たなかった"),

    ("歩く", False, False, "歩く"),
    ("歩く", True, False, "歩かない"),
    ("歩く", False, True, "歩いた"),
    ("歩く", True, True, "歩かなかった"),

    ("走る", False, False, "走る"),
    ("走る", True, False, "走らない"),
    ("走る", False, True, "走った"),
    ("走る", True, True, "走らなかった"),

    ("作る", False, False, "作る"),
    ("作る", True, False, "作らない"),
    ("作る", False, True, "作った"),
    ("作る", True, True, "作らなかった"),

    ("泳ぐ", False, False, "泳ぐ"),
    ("泳ぐ", True, False, "泳がない"),
    ("泳ぐ", False, True, "泳いだ"),
    ("泳ぐ", True, True, "泳がなかった"),

    ("帰る", False, False, "帰る"),
    ("帰る", True, False, "帰らない"),
    ("帰る", False, True, "帰った"),
    ("帰る", True, True, "帰らなかった"),
])


@godan_plain_cases
def test_godan_plain(verb, make_negative, make_past_tense, expected):
    assert_verb_type(verb, GODAN)
    conjugated = conjugate(verb, "plain", make_negative, make_past_tense)
    assert conjugated == expected, f"[{verb}] Expected {expected}, got {conjugated}."


godan_polite_cases = pytest.mark.parametrize("verb, make_negative, make_past_tense, expected", [
    ("書く", False, False, "書きます"),
    ("書く", True, False, "書きません"),
    ("書く", False, True, "書きました"),
    ("書く", True, True, "書きませんでした"),

    ("話す", False, False, "話します"),
    ("話す", True, False, "話しません"),
    ("話す", False, True, "話しました"),
    ("話す", True, True, "話しませんでした"),

    ("泳ぐ", False, False, "泳ぎます"),
    ("泳ぐ", True, False, "泳ぎません"),
    ("泳ぐ", False, True, "泳ぎました"),
    ("泳ぐ", True, True, "泳ぎませんでした"),

    ("読む", False, False, "読みます"),
    ("読む", True, False, "読みません"),
    ("読む", False, True, "読みました"),
    ("読む", True, True, "読みませんでした"),

    ("死ぬ", False, False, "死にます"),
    ("死ぬ", True, False, "死にません"),
    ("死ぬ", False, True, "死にました"),
    ("死ぬ", True, True, "死にませんでした"),

    ("買う", False, False, "買います"),
    ("買う", True, False, "買いません"),
    ("買う", False, True, "買いました"),
    ("買う", True, True, "買いませんでした"),

    ("切る", False, False, "切ります"),
    ("切る", True, False, "切りません"),
    ("切る", False, True, "切りました"),
    ("切る", True, True, "切りませんでした"),

    ("踊る", False, False, "踊ります"),
    ("踊る", True, False, "踊りません"),
    ("踊る", False, True, "踊りました"),
    ("踊る", True, True, "踊りませんでした"),

    ("急ぐ", False, False, "急ぎます"),
    ("急ぐ", True, False, "急ぎません"),
    ("急ぐ", False, True, "急ぎました"),
    ("急ぐ", True, True, "急ぎませんでした"),

    ("飲む", False, False, "飲みます"),
    ("飲む", True, False, "飲みません"),
    ("飲む", False, True, "飲みました"),
    ("飲む", True, True, "飲みませんでした"),

    ("待つ", False, False, "待ちます"),
    ("待つ", True, False, "待ちません"),
    ("待つ", False, True, "待ちました"),
    ("待つ", True, True, "待ちませんでした"),

    ("歩く", False, False, "歩きます"),
    ("歩く", True, False, "歩きません"),
    ("歩く", False, True, "歩きました"),
    ("歩く", True, True, "歩きませんでした"),

    ("走る", False, False, "走ります"),
    ("走る", True, False, "走りません"),
    ("走る", False, True, "走りました"),
    ("走る", True, True, "走りませんでした"),

    ("作る", False, False, "作ります"),
    ("作る", True, False, "作りません"),
    ("作る", False, True, "作りました"),
    ("作る", True, True, "作りませんでした"),

    ("泳ぐ", False, False, "泳ぎます"),
    ("泳ぐ", True, False, "泳ぎません"),
    ("泳ぐ", False, True, "泳ぎました"),
    ("泳ぐ", True, True, "泳ぎませんでした"),

    ("帰る", False, False, "帰ります"),
    ("帰る", True, False, "帰りません"),
    ("帰る", False, True, "帰りました"),
    ("帰る", True, True, "帰りませんでした"),
])



@godan_polite_cases
def test_godan_polite(verb, make_negative, make_past_tense, expected):
    assert_verb_type(verb, GODAN)
    conjugated = conjugate(verb, "polite", make_negative, make_past_tense)
    assert conjugated == expected, f"[{verb}] Expected {expected}, got {conjugated}."