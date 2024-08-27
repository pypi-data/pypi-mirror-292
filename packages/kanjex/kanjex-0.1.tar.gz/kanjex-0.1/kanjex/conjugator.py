from kanjex.conjugation.forms import detect_verb_type, IRREGULAR, GODAN, ICHIDAN, ConjugationForms
from kanjex.conjugation.godan import GodanConjugator
from kanjex.conjugation.ichidan import IchidanConjugator
from kanjex.conjugation.irregular import IrregularConjugator

def assert_verb_type(verb: str, expected: str):
    detected = detect_verb_type(verb)
    assert detected == expected, f"[{verb}] Expected {expected}, detected {detected}."

# Main function that takes a verb, form, and tense options, and returns the conjugated verb and its type
def conjugate(verb: str, form: str = ConjugationForms.POLITE, negative: bool = False, past_tense: bool = False):
    """Given a dictionary-form verb, conjugate it to the specified form.
    """

    # Detect the verb type
    verb_type = detect_verb_type(verb)
    
    # Conjugate the verb based on its type
    if verb_type == IRREGULAR:
        return IrregularConjugator.conjugate(verb, form, negative, past_tense)
    elif verb_type == GODAN:
        return GodanConjugator.conjugate(verb, form, negative, past_tense)
    elif verb_type == ICHIDAN:
        return IchidanConjugator.conjugate(verb, form, negative, past_tense)
    else:
        raise ValueError("Unknown verb type")

# Example usage
if __name__ == "__main__":
    verb = "食べる"
    result = conjugate(verb, "plain", False, False)
    verb_type = detect_verb_type(verb)
    print(f"Conjugated Verb: {result}, Verb Type: {verb_type}")
