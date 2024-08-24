from .exceptions import ZeroValueError

def free_cash_flow(operating_cash_flow: float, capital_expenditures: float) -> float:
    """
    Calculate the Free Cash Flow
    
    Parameters:
        operating_cash_flow (float): The operating cash flow
        capital_expenditures (float): The capital expenditures
        
    Returns:
        float: The Free Cash Flow
    """
    return operating_cash_flow - capital_expenditures

def operating_cash_flow_ratio(operating_cash_flow: float, current_liabilities: float) -> float:
    """
    Calculate the Operating Cash Flow Ratio
    
    Parameters:
        operating_cash_flow (float): The operating cash flow
        current_liabilities (float): The current liabilities
        
    Returns:
        float: The Operating Cash Flow Ratio
    """
    if current_liabilities == 0:
        raise ZeroValueError("Current Liabilities")
    return operating_cash_flow / current_liabilities

