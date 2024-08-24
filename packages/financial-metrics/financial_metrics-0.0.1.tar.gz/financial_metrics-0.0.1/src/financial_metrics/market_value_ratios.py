from .exceptions import ZeroValueError

def price_to_earnings(price_per_share: float, earnings_per_share: float) -> float:
    """
    Calculate the Price-to-Earnings (P/E) ratio
    
    Parameters:
        price_per_share (float): The current market price per share
        earnings_per_share (float): The earnings per share
        
    Returns:
        float: The Price-to-Earnings (P/E) ratio
    """
    if earnings_per_share == 0:
        raise ZeroValueError("Earnings Per Share")
    return price_per_share / earnings_per_share

def price_to_book(price_per_share: float, book_value_per_share: float) -> float:
    """
    Calculate the Price-to-Book (P/B) ratio.
    
    Parameters:
        price_per_share (float): The current market price per share
        book_value_per_share (float): The book value per share
        
    Returns:
        float: The Price-to-Book (P/B) ratio
    """
    if book_value_per_share == 0:
        raise ZeroValueError("Book Value Per Share")
    return price_per_share / book_value_per_share

def dividend_yield(dividend_per_share: float, price_per_share: float) -> float:
    """
    Calculate the Dividend Yield
    
    Parameters:
        dividend_per_share (float): The dividend per share
        price_per_share (float): The current market price per share
        
    Returns:
        float: The Dividend Yield as a percentage.
    """
    if price_per_share == 0:
        raise ZeroValueError("Price Per Share")
    return (dividend_per_share / price_per_share) * 100

def price_to_earnings_growth(price_per_share: float, earnings_per_share: float, earnings_growth_rate: float) -> float:
    """
    Calculate the Price-to-Earnings Growth (PEG) ratio
    
    Parameters:
        price_per_share (float): The current market price per share
        earnings_per_share (float): The earnings per share
        earnings_growth_rate (float): The expected growth rate of earnings (in percentage)
        
    Returns:
        float: The Price-to-Earnings Growth (PEG) ratio
    """
    if earnings_per_share == 0:
        raise ZeroValueError("Earnings Per Share")
    if earnings_growth_rate == 0:
        raise ZeroValueError("Earnings Growth Rate")
    pe_ratio = price_per_share / earnings_per_share
    return pe_ratio / (earnings_growth_rate / 100)
