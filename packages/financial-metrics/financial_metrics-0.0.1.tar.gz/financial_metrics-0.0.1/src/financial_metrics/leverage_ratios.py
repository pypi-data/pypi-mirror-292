from .exceptions import ZeroValueError

def debt_to_equity_ratio(total_debt: float, equity: float) -> float:
    """
    Calculate the debt-to-equity ratio
    
    Parameters:
        total_debt (float): The total debt
        equity (float): The total equity
        
    Returns:
        float: The inventory turnover ratio.
    """
    if equity == 0:
        raise ZeroValueError("Equity")
    return total_debt / equity

def debt_ratio(total_debt: float, total_assets: float) -> float:
    """
    Calculate the debt ratio
    
    Parameters:
        total_debt (float): The total debt
        total_assets (float): The total assets
        
    Returns:
        float: The inventory turnover ratio
    """
    if total_assets == 0:
        raise ZeroValueError("Total assets")
    return total_debt / total_assets

def interest_coverage_ratio(operating_income: float, interest_expense: float) -> float:
    """
    Calculate the interest coverage ratio
    
    Parameters:
        operating_income (float): The operating income
        interest_expense (float): The interest expense
        
    Returns:
        float: The interest coverage ratio
    """
    if interest_expense == 0:
        raise ZeroValueError("Interest expense")
    return operating_income / interest_expense
