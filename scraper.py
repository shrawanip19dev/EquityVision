import requests
from bs4 import BeautifulSoup
import re

def scrape_stock_data(symbol: str):
    """
    Scrapes Screener.in for a given stock symbol.
    Returns a dictionary of parsed raw inputs or raises ValueError.
    """
    symbol = symbol.upper().strip()
    
    # Try consolidated page first, then standalone fallback
    urls = [
        f"https://www.screener.in/company/{symbol}/consolidated/",
        f"https://www.screener.in/company/{symbol}/"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    html_content = None
    success_url = None
    
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                html_content = response.content
                success_url = url
                break
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            
    if not html_content:
        raise ValueError(f"Could not fetch data for stock symbol '{symbol}' from Screener.in (page not found or blocked).")
        
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract Stock Name
    company_name_div = soup.find('div', class_='company-name')
    if company_name_div:
        company_name = company_name_div.find('h1')
        stock_name = company_name.text.strip() if company_name else symbol
    else:
        stock_name = symbol

    # 1. Parse Top Ratios (Current Price and Stock P/E)
    current_price = None
    stock_pe = None
    
    top_ratios = soup.find('ul', id='top-ratios')
    if not top_ratios:
        top_ratios = soup.find('ul', class_='top-ratios')
        
    if top_ratios:
        ratios = top_ratios.find_all('li')
        for r in ratios:
            name_span = r.find('span', class_='name')
            num_span = r.find('span', class_='number')
            if name_span and num_span:
                name_text = name_span.text.strip().lower()
                val_text = num_span.text.strip().replace(',', '')
                
                if 'current price' in name_text:
                    try:
                        current_price = float(val_text)
                    except ValueError:
                        pass
                elif 'stock p/e' in name_text or 'stock pe' in name_text:
                    try:
                        stock_pe = float(val_text)
                    except ValueError:
                        pass
                        
    # 2. Parse P&L Table (Current EPS and EPS 3 Years ago)
    eps_values = []
    headers_text = []
    
    pl_section = soup.find('section', id='profit-loss')
    if pl_section:
        table = pl_section.find('table', class_='data-table')
        if table:
            # Get table headers (years)
            thead = table.find('thead')
            if thead:
                headers_text = [th.text.strip() for th in thead.find_all('th')]
            
            # Find EPS row
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['td', 'th'])
                col_texts = [c.text.strip().replace(',', '') for c in cols]
                if col_texts and 'eps in rs' in col_texts[0].lower():
                    # Strip empty and non-numeric fields if any, but match headers length
                    eps_values = col_texts[1:]
                    break
                    
    if not eps_values:
        raise ValueError(f"Could not locate Earnings Per Share (EPS) history for {symbol} in P&L section.")

    # Convert EPS values to float, handling any empty or non-numeric cells
    parsed_eps = []
    for val in eps_values:
        try:
            # Handle negative EPS written as (12.3) or -12.3
            cleaned_val = val
            if cleaned_val.startswith('(') and cleaned_val.endswith(')'):
                cleaned_val = '-' + cleaned_val[1:-1]
            parsed_eps.append(float(cleaned_val) if cleaned_val else 0.0)
        except ValueError:
            parsed_eps.append(0.0)

    # Calculate Current EPS and EPS 3 Years Ago
    # Index -1 represents latest column, index -4 represents 3 years ago
    if len(parsed_eps) < 4:
        raise ValueError(f"Insufficient EPS history for {symbol}. Need at least 3 years of data.")
        
    current_eps = parsed_eps[-1]
    eps_3yr_ago = parsed_eps[-4]
    
    # 3. Parse Stock Price CAGR 3 Years (Return over three years)
    return_3yr = 15.0  # default fallback return (e.g. 15%)
    
    tables = soup.find_all('table', class_='ranges-table')
    cagr_found = False
    for t in tables:
        headers_t = t.find_all('th')
        header_text = headers_t[0].text.strip().lower() if headers_t else ""
        
        # We look for "Stock Price CAGR" or "stock price cagr"
        if "stock price cagr" in header_text or "compounded stock price cagr" in header_text:
            rows = t.find_all('tr')
            for r in rows:
                cols = r.find_all('td')
                if len(cols) >= 2:
                    period_name = cols[0].text.strip().lower()
                    cagr_val_text = cols[1].text.strip().replace('%', '')
                    if "3 years" in period_name:
                        try:
                            return_3yr = float(cagr_val_text)
                            cagr_found = True
                            break
                        except ValueError:
                            pass
            if cagr_found:
                break
                
    # If no Stock Price CAGR found, try to look at CAGR Sales or ROE 3 year average
    if not cagr_found:
        print("Stock Price CAGR for 3 years not found on page, defaulting return_3yr to 15.0")
        
    # Return everything as a dictionary
    return {
        "stock_name": stock_name,
        "current_price": current_price,
        "stock_pe": stock_pe,
        "current_eps": current_eps,
        "eps_3yr_ago": eps_3yr_ago,
        "historical_return_3yr": return_3yr
    }
