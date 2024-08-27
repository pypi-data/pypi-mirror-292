from .forms import VerbTypeConjugator


def _root_and_last_char(verb: str):
    return verb[:-1], verb[-1]


class GodanConjugator(VerbTypeConjugator):
    @staticmethod
    def polite(verb: str, negative: bool, past_tense: bool) -> str:
        root, last_char = _root_and_last_char(verb)

        if last_char == 'む':
            root = root + 'み'
        elif last_char == 'ぶ':
            root = root + 'び'
        elif last_char == 'ぬ':
            root = root + 'に'
        elif last_char == 'す':
            root = root + 'し'
        elif last_char == 'く':
            root = root + 'き'
        elif last_char == 'ぐ':
            root = root + 'ぎ'
        elif last_char == 'る':
            root = root + 'り'
        elif last_char in 'う':
            root = root + 'い'
        elif last_char == 'つ':
            root = root + 'ち'
        else:
            raise ValueError(f"Invalid verb ending: {last_char}")

        if past_tense:
            if negative:
                return root + "ませんでした"
            return root + "ました"
        if negative:
            return root + "ません"
        return root + "ます"

    @staticmethod
    def plain(verb: str, negative: bool, past_tense: bool) -> str:
        root, last_char = _root_and_last_char(verb)

        # special case for 行く and 行いた
        if verb == "行く":
            if not negative and past_tense:
                return "行った"
            
        # Apply root modification based on the verb ending
        if last_char == 'う':
            if negative:
                root += 'わ'
            elif past_tense:
                root += 'っ'
        elif last_char == 'く':
            root += 'か' if negative else ''
        elif last_char == 'ぐ':
            root += 'が' if negative else ''
        elif last_char == 'す':
            root += 'さ' if negative else ''
        elif last_char == 'つ':
            root += 'た'
        elif last_char == 'ぬ':
            root += 'な'
        elif last_char == 'む':
            root += 'ま'
        elif last_char == 'る':
            root += 'ら' if negative else ''  # Ensure 'ら' is correctly added
        elif last_char == 'ぶ':
            root += 'ば'

        # Apply past tense or non-past tense
        if past_tense:
            if negative:
                return root + "なかった"  # Correct for negative past tense
            else:
                # Handle specific endings for past tense of Godan verbs
                if last_char == 'く':
                    return root + "いた"  # e.g., 書く -> 書いた
                elif last_char == 'ぐ':
                    return root + "いだ"  # e.g., 泳ぐ -> 泳いだ
                elif last_char == 'す':
                    return root + "した"  # e.g., 話す -> 話した
                elif last_char in ['む', 'ぬ', 'ぶ']:
                    return root[:-1] + "んだ"  # e.g., 読む -> 読んだ, 飲む -> 飲んだ
                elif last_char == 'う':
                    return root + "た"  # e.g., 買う -> 買った
                elif last_char == 'る':
                    return root + "った"  # e.g., 切る -> 切った (past tense for Godan る)
                elif last_char == 'つ':
                    return root[:-1] + "った"
                else:
                    return root + "った"  # e.g., 待つ -> 待った, 切る -> 切った
        else:
            if negative:
                return root + "ない"  # Correct for negative non-past
            else:
                return verb  # Present positive form is just the verb itself
            
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