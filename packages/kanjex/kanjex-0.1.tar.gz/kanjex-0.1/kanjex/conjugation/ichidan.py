from .forms import VerbTypeConjugator


class IchidanConjugator(VerbTypeConjugator):
    @staticmethod
    def polite(verb: str, negative: bool, past_tense: bool) -> str:
        root = verb[:-1]  # Remove the final 'る'

        if past_tense:
            return root + "ました" if not negative else root + "ませんでした"
        
        return root + "ます" if not negative else root + "ません"

    @staticmethod
    def plain(verb: str, negative: bool, past_tense: bool) -> str:
        if verb.endswith('いる') or verb.endswith('える'):
            root = verb[:-1]  # Remove the final 'る'
            if past_tense:
                return root + "た" if not negative else root + "なかった"
            else:
                return verb if not negative else root + "ない"
        else:
            # Special case handling for specific verbs
            if verb == "ある":
                if past_tense:
                    return "あった" if not negative else "なかった"
                else:
                    return "ある" if not negative else "ない"
            elif verb == "頂く":
                if past_tense:
                    return "頂いた" if not negative else "頂かなかった"
                else:
                    return "頂く" if not negative else "頂かない"
            else:
                # Default behavior for other Ichidan verbs
                if past_tense:
                    return verb[:-1] + "た" if not negative else verb[:-1] + "なかった"
                else:
                    return verb if not negative else verb[:-1] + "ない"

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
