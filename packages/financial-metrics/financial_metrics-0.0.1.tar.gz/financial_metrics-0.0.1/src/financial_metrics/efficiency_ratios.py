from .exceptions import ZeroValueError

def inventory_turnover(cost_of_goods_sold: float, average_inventory: float) -> float:
    """
    Calculate the inventory turnover ratio
    
    Parameters:
        cost_of_goods_sold (float): The cost of goods sold
        average_inventory (float): The average inventory
        
    Returns:
        float: The inventory turnover ratio
    """
    if average_inventory == 0:
        raise ZeroValueError("Average inventory")
    return cost_of_goods_sold / average_inventory

def receivables_turnover(net_credit_sales: float, average_accounts_receivable: float) -> float:
    """
    Calculate the receivables turnover ratio
    
    Parameters:
        net_credit_sales (float): The net credit sales
        average_accounts_receivable (float): The average accounts receivable
        
    Returns:
        float: The receivables turnover ratio
    """
    if average_accounts_receivable == 0:
        raise ZeroValueError("Average accounts receivable")
    return net_credit_sales / average_accounts_receivable

def asset_turnover_ratio(revenue: float, average_total_assets: float) -> float:
    """
    Calculate the asset turnover ratio
    
    Parameters:
        revenue (float): The total revenue
        average_total_assets (float): The average total assets
        
    Returns:
        float: The asset turnover ratio
    """
    if average_total_assets == 0:
        raise ZeroValueError("Average total assets")
    return revenue / average_total_assets

def accounts_payable_turnover(cost_of_goods_sold: float, average_accounts_payable: float) -> float:
    """
    Calculate the accounts payable turnover ratio
    
    Parameters:
        cost_of_goods_sold (float): The cost of goods sold
        average_accounts_payable (float): The average accounts payable
        
    Returns:
        float: The accounts payable turnover ratio
    """
    if average_accounts_payable == 0:
        raise ZeroValueError("Average accounts payable")
    return cost_of_goods_sold / average_accounts_payable

def days_sales_outstanding(accounts_receivable: float, net_credit_sales: float) -> float:
    """
    Calculate the days sales outstanding (DSO)
    
    Parameters:
        accounts_receivable (float): The accounts receivable
        net_credit_sales (float): The net credit sales
        
    Returns:
        float: The days sales outstanding in days
    """
    if net_credit_sales == 0:
        raise ZeroValueError("Net credit sales")
    return (accounts_receivable / net_credit_sales) * 365
