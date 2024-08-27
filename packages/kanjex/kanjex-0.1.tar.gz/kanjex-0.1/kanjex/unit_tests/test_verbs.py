from kanjex.data.verbs.get import get_verbs

def test_conjugate():
    verbs = get_verbs()

    for verb in verbs:
        print(verb.dictionary_form)