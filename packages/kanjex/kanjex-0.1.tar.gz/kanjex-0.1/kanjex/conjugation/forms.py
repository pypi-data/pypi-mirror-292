import pykakasi

kks = pykakasi.kakasi()

ICHIDAN = "ichidan"
GODAN = "godan"
IRREGULAR = "irregular"

class ConjugationForms:
    PLAIN = "plain"                 # Base form
    POLITE = "polite"               # Respectful or formal
    TE = "-te"                      # Connecting form
    DESIRE = "desire"               # Desire form
    CONDITIONAL = "conditional"     # Conditional "if" form
    POTENTIAL = "potential"         # Ability form
    IMPERATIVE = "imperative"       # Command form
    VOLITIONAL = "volitional"       # Intention or will form
    PASSIVE = "passive"             # Action received form
    CAUSATIVE = "causative"         # Making or allowing form
    PROGRESSIVE = "progressive"     # Ongoing action form
    PERFECTIVE = "perfective"       # Completed action form




class VerbTypeConjugator:
    @staticmethod
    def polite(verb: str, negative: bool, past_tense: bool) -> str:
        raise NotImplementedError

    @staticmethod
    def plain(verb: str, negative: bool, past_tense: bool) -> str:
        raise NotImplementedError
    
    @staticmethod
    def te(verb: str, negative: bool, past_tense: bool) -> str:
        raise NotImplementedError
    
    @staticmethod
    def desire(verb: str, negative: bool, past_tense: bool) -> str:
        raise NotImplementedError
    
    @staticmethod
    def conditional(verb: str, negative: bool, past_tense: bool) -> str:
        raise NotImplementedError
    
    @staticmethod
    def potential(verb: str, negative: bool, past_tense: bool) -> str:
        raise NotImplementedError
    
    @staticmethod
    def imperative(verb: str, negative: bool, past_tense: bool) -> str:
        raise NotImplementedError
    
    @staticmethod
    def volitional(verb: str, negative: bool, past_tense: bool) -> str:
        raise NotImplementedError
    
    @staticmethod
    def passive(verb: str, negative: bool, past_tense: bool) -> str:
        raise NotImplementedError
    
    @staticmethod
    def causative(verb: str, negative: bool, past_tense: bool) -> str:
        raise NotImplementedError
    
    @staticmethod
    def progressive(verb: str, negative: bool, past_tense: bool) -> str:
        raise NotImplementedError
    
    @staticmethod
    def perfective(verb: str, negative: bool, past_tense: bool) -> str:
        raise NotImplementedError
    
    @classmethod
    def conjugate(cls, verb: str, form: ConjugationForms, negative: bool, past_tense: bool) -> str:
        """Conjugates the verb to the specified form."""

        # Looking for the actual implementations?
        # Look in the Godan, Ichidan, and Irregular classes for the actual implementations for these forms (ie. Polite, Plain, etc.).

        if form == ConjugationForms.POLITE:
            return cls.polite(verb, negative, past_tense)
        elif form == ConjugationForms.PLAIN:
            return cls.plain(verb, negative, past_tense)
        elif form == ConjugationForms.TE:
            return cls.te(verb, negative, past_tense)
        elif form == ConjugationForms.DESIRE:
            return cls.desire(verb, negative, past_tense)
        elif form == ConjugationForms.CONDITIONAL:
            return cls.conditional(verb, negative, past_tense)
        elif form == ConjugationForms.POTENTIAL:
            return cls.potential(verb, negative, past_tense)
        elif form == ConjugationForms.IMPERATIVE:
            return cls.imperative(verb, negative, past_tense)
        elif form == ConjugationForms.VOLITIONAL:
            return cls.volitional(verb, negative, past_tense)
        elif form == ConjugationForms.PASSIVE:
            return cls.passive(verb, negative, past_tense)
        elif form == ConjugationForms.CAUSATIVE:
            return cls.causative(verb, negative, past_tense)
        elif form == ConjugationForms.PROGRESSIVE:
            return cls.progressive(verb, negative, past_tense)
        elif form == ConjugationForms.PERFECTIVE:
            return cls.perfective(verb, negative, past_tense)
        
        raise ValueError(f"Invalid form: {form}.")
    


GODAN_EXCEPTIONS = {'帰る', '切る', '知る', '入る', '走る', '要る', '交じる', '混じる', '限る', '取る', '減る', '割る', '探る', '滑る', '座る'}

# List of exceptions that are Ichidan verbs
ICHIDAN_EXCEPTIONS = {'着る', '煮る', '見る', '浴びる', '借りる', '降りる', '出る', 'ある', '頂く'}

def extract_vowel(hiragana_char: str) -> str:
    vowel_map = {
        # Regular Hiragana
        'あ': 'あ', 'か': 'あ', 'さ': 'あ', 'た': 'あ', 'な': 'あ', 'は': 'あ', 'ま': 'あ', 'や': 'あ', 'ら': 'あ', 'わ': 'あ',
        'い': 'い', 'き': 'い', 'し': 'い', 'ち': 'い', 'に': 'い', 'ひ': 'い', 'み': 'い', 'り': 'い',
        'う': 'う', 'く': 'う', 'す': 'う', 'つ': 'う', 'ぬ': 'う', 'ふ': 'う', 'む': 'う', 'ゆ': 'う', 'る': 'う',
        'え': 'え', 'け': 'え', 'せ': 'え', 'て': 'え', 'ね': 'え', 'へ': 'え', 'め': 'え', 'れ': 'え',
        'お': 'お', 'こ': 'お', 'そ': 'お', 'と': 'お', 'の': 'お', 'ほ': 'お', 'も': 'お', 'よ': 'お', 'ろ': 'お',
        
        # Dakuten Hiragana
        'が': 'あ', 'ざ': 'あ', 'だ': 'あ', 'ば': 'あ',
        'ぎ': 'い', 'じ': 'い', 'ぢ': 'い', 'び': 'い',
        'ぐ': 'う', 'ず': 'う', 'づ': 'う', 'ぶ': 'う',
        'げ': 'え', 'ぜ': 'え', 'で': 'え', 'べ': 'え',
        'ご': 'お', 'ぞ': 'お', 'ど': 'お', 'ぼ': 'お',

        # Handakuten Hiragana
        'ぱ': 'あ', 
        'ぴ': 'い', 
        'ぷ': 'う', 
        'ぺ': 'え', 
        'ぽ': 'お',
    }
    
    vowel = vowel_map.get(hiragana_char, None)

    if vowel is None:
        raise ValueError(f"Invalid Hiragana character: {hiragana_char}")
    
    return vowel

def detect_verb_type(verb: str) -> str:
    # List of irregular verbs
    irregular_verbs = {"する", "来る", "くる"}
    
    # Check for irregular verbs first
    if verb in irregular_verbs:
        return IRREGULAR
    
    # Check for exceptions
    if verb in GODAN_EXCEPTIONS:
        return GODAN
    if verb in ICHIDAN_EXCEPTIONS:
        return ICHIDAN
    
    # General rule for verbs ending in 'る'
    if verb.endswith('る'):
        stem = verb[:-1]

        # Convert the stem to hiragana using Pykakasi
        hiragana = ''.join([item['hira'] for item in kks.convert(stem)])
        
        # Extract the vowel sound from the last character in the hiragana
        last_vowel = extract_vowel(hiragana[-1])
        
        # Adjust logic to classify Ichidan and Godan based on the last vowel
        if last_vowel in 'いえ':
            return ICHIDAN
        else:
            return GODAN
    else:
        return GODAN
