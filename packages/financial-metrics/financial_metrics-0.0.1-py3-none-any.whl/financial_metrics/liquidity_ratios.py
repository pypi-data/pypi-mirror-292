from .exceptions import ZeroLiabilityError

def current_ratio(current_assets: float, current_liabilities: float) -> float:
    """
    Calculate the current ratio.
    
    Parameters:
        current_assets (float): The total current assets
        current_liabilities (float): The total current liabilities
        
    Returns:
        float: The current ratio
    """   
    if current_liabilities == 0:
        raise ZeroLiabilityError
    return current_assets/current_liabilities

def quick_ratio(current_assets: float, current_liabilities: float, inventory: float) -> float:
    """
    Calculate the quick ratio.
    
    Parameters:
        current_assets (float): The total current assets
        current_liabilities (float): The total current liabilities
        inventory (float): The total inventory
        
    Returns:
        float: The quick ratio
    """ 
    if current_liabilities == 0:
        raise ZeroLiabilityError
    return (current_assets-inventory)/current_liabilities

def cash_ratio(cash: float, cash_equivalents: float, current_liabilities:float) -> float:
    """
    Calculate the quick ratio.
    
    Parameters:
        cash(float): The total cash
        cash equivalents (float): The total cash equivalents
        current_liabilites (float): The total current liabilities
        
    Returns:
        float: The cash ratio
    """ 
    if current_liabilities == 0:
        raise ZeroLiabilityError 
    return (cash+cash_equivalents)/current_liabilities 









    