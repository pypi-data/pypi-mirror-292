class BarcodeService:

    def __init__(self, upcString: str):
        self.upcString = upcString
        self.checkDigit = self.is_valid_upc_check_digit()

    def is_valid_upc_check_digit(self):
        """
        Checks if the final digit in a 13-digit UPC is a valid check digit.

        Args:
            upc: A 13-digit UPC code as a string.

        Returns:
            True if the final digit is a valid check digit, False otherwise.
        """

        # Extract digits and convert to integers
        digits_all = [int(digit) for digit in self.upcString]
        digits_all.reverse()
        digits = digits_all[:-1]

        # Calculate the check digit
        odd_sum = sum(digits[0::2])
        even_sum = sum(digits[1::2])
        calculated_check_digit = (10 - (((odd_sum * 3) + even_sum) % 10)) % 10

        # Compare with the provided check digit
        return calculated_check_digit == digits[-1]