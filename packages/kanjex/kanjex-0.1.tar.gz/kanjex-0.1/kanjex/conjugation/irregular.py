from .forms import VerbTypeConjugator


class IrregularConjugator(VerbTypeConjugator):

    @staticmethod
    def polite(verb: str, negative: bool, past_tense: bool) -> str:
        raise NotImplementedError
    
    @staticmethod
    def plain(verb: str, negative: bool, past_tense: bool) -> str:
        if verb == "する":
            if past_tense:
                return "しなかった" if negative else "した"
            else:
                return "しない" if negative else "する"
        elif verb in ["来る", "くる"]:
            if past_tense:
                return "来なかった" if negative else "来た"
            else:
                return "来ない" if negative else "来る"
        else:
            raise ValueError(f"Unknown irregular verb: {verb}")
        
    @staticmethod
    def te(verb: str, negative: bool, past_tense: bool) -> str:
        if verb == "する":
            return "しないで" if negative else "して"
        elif verb in ["来る", "くる"]:
            return "来ないで" if negative else "来て"
        else:
            raise ValueError(f"Unknown irregular verb: {verb}")
        
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