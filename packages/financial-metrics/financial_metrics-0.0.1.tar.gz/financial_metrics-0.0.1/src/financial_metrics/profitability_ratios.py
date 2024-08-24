from .exceptions import ZeroRevenueError

def gross_profit_margin(gross_profit: float, revenue: float) -> float:
    """
    Calculate the gross profit margin.
    
    Parameters:
        gross_profit (float): The gross profit
        revenue (float): The total revenue
        
    Returns:
        float: Gross profit margin
    """
    if revenue == 0:
        raise ZeroRevenueError("Revenue cannot be zero.")
    return gross_profit / revenue

def net_profit_margin(net_income: float, revenue: float) -> float:
    """
    Calculate the net profit margin
    
    Parameters:
        net_income (float): The net income
        revenue (float): The total revenue
        
    Returns:
        float: The net profit margin
    """
    if revenue == 0:
        raise ZeroRevenueError("Revenue cannot be zero.")
    return net_income / revenue

def return_on_assets(net_income: float, total_assets: float) -> float:
    """
    Calculate the return on assets (ROA)
    
    Parameters:
        net_income (float): The net income
        total_assets (float): The total assets
        
    Returns:
        float: The return on assets
    """
    if total_assets == 0:
        raise ZeroRevenueError("Total assets cannot be zero.")
    return net_income / total_assets

def return_on_equity(net_income: float, equity: float) -> float:
    """
    Calculate the return on equity (ROE).
    
    Parameters:
        net_income (float): The net income
        equity (float): The total equity
        
    Returns:
        float: The return on equity
    """
    if equity == 0:
        raise ZeroRevenueError("Equity cannot be zero.")
    return net_income / equity
