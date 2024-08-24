
class FinancialCalculationError(Exception):
    pass

class ZeroLiabilityError(FinancialCalculationError):
    def __init__(self,message="Current Liabilities cannot be zero."):
        self.message = message
        super.__init__(self.message)

class ZeroRevenueError(FinancialCalculationError):
    def __init__(self, message="Revenue cannot be zero."):
        self.message = message
        super.__init__(self.message)

class ZeroValueError(FinancialCalculationError):
    def __init__(self, parameter: str):
        self.message = f"{parameter} canot be zero."
        super.__init__(self.message)
