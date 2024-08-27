from barbud.digits import ElevenDigit, TwelveDigit, ThirteenDigit, FourteenDigit

def identifyUPC(upcString: str) -> str:
    
    if len(upcString) == 11:
            
            return ElevenDigit(upcString).getType()
        
    elif len(upcString) == 12:

        return TwelveDigit(upcString).getType()

    elif len(upcString) == 13:

        return ThirteenDigit(upcString).getType()

    elif len(upcString) == 14:

        return FourteenDigit(upcString).getType()

    else:

        return f'UPC{len(upcString)}'