def calculate_valuation(
    current_eps: float,
    eps_3yr_ago: float,
    stock_pe: float,
    current_price: float,
    required_return_annual: float  # e.g., 15.0 for 15%
):
    """
    Runs the stock valuation calculations based on:
    - current_eps: EPS of the latest period (e.g., TTM)
    - eps_3yr_ago: EPS from 3 years ago
    - stock_pe: Target P/E multiple (usually current stock PE)
    - current_price: Current market price of the stock
    - required_return_annual: Required annual growth return rate (%) (discount rate)
    """
    
    # 1. EPS growth rate (CAGR) over 3 years
    # If EPS was negative in the past or is negative now, CAGR is complex.
    # We will handle boundary cases (like division by zero or negative earnings) gracefully.
    if eps_3yr_ago <= 0 or current_eps <= 0:
        # Default to a conservative growth rate if negative earnings exist
        eps_cagr = 0.05  # 5% default
    else:
        eps_cagr = (current_eps / eps_3yr_ago) ** (1 / 3.0) - 1.0

    # 2. Projected Future EPS in 3 years
    future_eps = current_eps * ((1.0 + eps_cagr) ** 3)
    
    # 3. Projected Stock Price in 3 years
    # We apply the stock P/E multiple to the future EPS
    # If PE is negative, we default it to a standard multiple of 15x or 0
    pe_multiple = max(0.0, stock_pe if stock_pe else 15.0)
    future_price = future_eps * pe_multiple
    
    # 4. Fair Value (discount future price to present day)
    r = required_return_annual / 100.0
    fair_value = future_price / ((1.0 + r) ** 3)
    
    # Round calculations
    eps_cagr_pct = round(eps_cagr * 100.0, 2)
    future_eps = round(future_eps, 2)
    future_price = round(future_price, 2)
    fair_value = round(fair_value, 2)
    
    # 5. Profit and Margins
    profit = round(fair_value - current_price, 2)
    upside_percent = round((profit / current_price) * 100.0, 2) if current_price > 0 else 0.0
    
    # Margin of Safety (if undervalued)
    margin_of_safety = round((1 - (current_price / fair_value)) * 100.0, 2) if fair_value > current_price else 0.0
    
    status = "UNDERVALUED" if current_price < fair_value else "OVERVALUED"
    
    return {
        "eps_growth_cagr": eps_cagr_pct,
        "future_eps": future_eps,
        "future_price": future_price,
        "fair_value": fair_value,
        "profit": profit,
        "upside_percent": upside_percent,
        "margin_of_safety": margin_of_safety,
        "status": status
    }
