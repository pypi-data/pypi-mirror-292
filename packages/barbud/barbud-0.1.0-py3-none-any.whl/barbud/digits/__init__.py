from barbud.services import BarcodeService

class ElevenDigit(BarcodeService):

    def __init__(self, number):
        super().__init__(number)

    def getType(self):

        return "UPC11"
    
class TwelveDigit(BarcodeService):

    def __init__(self, number):
        super().__init__(number)

    def getType(self):

        return "UPC12"
    
class ThirteenDigit(BarcodeService):

    def __init__(self, number):
        super().__init__(number)
    
    def getType(self):

        if self.checkDigit:
            
            return "UPC13CD"
        else:
            
            return "UPC13"
        
class FourteenDigit(BarcodeService):

    def __init__(self, number):
        super().__init__(number)

    def getType(self):

        if self.checkDigit:
        
            return "UPC14CD"
        
        else:
            
            return "UPC14"