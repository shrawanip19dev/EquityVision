import sys
import os
import random

# Include backend in python path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from scraper import scrape_stock_data
from calculator import calculate_valuation
import google_sheet

def run_test():
    symbol = "APARINDS"
    print(f"--- Starting EquityVision Pipeline Test for {symbol} ---")

    # 1. Test Scraper
    try:
        data = scrape_stock_data(symbol)
        print("\n[1/4] Scraper Test: PASSED")
        print(f"  Stock Name:             {data['stock_name']}")
        print(f"  Current Price:          {data['current_price']}")
        print(f"  Stock P/E:              {data['stock_pe']}")
        print(f"  Current EPS:            {data['current_eps']}")
        print(f"  EPS 3 Years Ago:        {data['eps_3yr_ago']}")
        print(f"  Stock CAGR (3 Years):   {data['historical_return_3yr']}%")
    except Exception as e:
        print(f"\n[1/4] Scraper Test: FAILED. Error: {e}")
        return

    # 2. Test Valuation Calculations
    try:
        required_return = 15.0
        analysis = calculate_valuation(
            current_eps=data['current_eps'],
            eps_3yr_ago=data['eps_3yr_ago'],
            stock_pe=data['stock_pe'],
            current_price=data['current_price'],
            required_return_annual=required_return
        )
        print("\n[2/4] Calculator Test: PASSED")
        print(f"  EPS 3-Yr Growth CAGR:   {analysis['eps_growth_cagr']}%")
        print(f"  Projected 3-Yr EPS:     {analysis['future_eps']}")
        print(f"  Projected 3-Yr Price:   {analysis['future_price']}")
        print(f"  Fair Value (Discounted): {analysis['fair_value']}")
        print(f"  Profit Upside:          {analysis['profit']}")
        print(f"  Upside Percent:         {analysis['upside_percent']}%")
        print(f"  Margin of Safety:       {analysis['margin_of_safety']}%")
        print(f"  Valuation Status:       {analysis['status']}")
    except Exception as e:
        print(f"\n[2/4] Calculator Test: FAILED. Error: {e}")
        return

    # 3. Test Google Sheets Auth Integration
    print("\n[3/4] Testing Google Sheets User Authentication...")
    test_username = f"test_user_{random.randint(100, 999)}"
    test_password = "password123"

    print(f"  Attempting to register user: '{test_username}'...")
    reg_result = google_sheet.register_user_in_sheet(test_username, test_password)

    if reg_result.get("status") == "success":
        print("  User registration in Sheet: Success!")
        print("  Attempting to log in with new user...")
        login_success = google_sheet.validate_user_in_sheet(test_username, test_password)
        if login_success:
            print("  User login verification in Sheet: Success!")
            print("  Auth Test: PASSED")
        else:
            print("  User login verification in Sheet: FAILED")
            print("  Auth Test: FAILED")
            return
    else:
        print(f"  User registration in Sheet: FAILED. Error: {reg_result.get('error')}")
        print("  Auth Test: FAILED (Double-check your Google Apps Script URL in backend/.env)")
        return

    # 4. Test Google Sheets Data Logging
    print("\n[4/4] Testing Google Sheets Data Logging...")
    print(f"  Attempting to save calculations for {data['stock_name']}...")
    save_result = google_sheet.save_analysis_result(
        stock_name=data['stock_name'],
        current_price=data['current_price'],
        fair_value=analysis['fair_value'],
        profit=analysis['profit']
    )

    if save_result.get("status") == "success":
        print("  Analysis saved successfully in Sheet!")
        print("  Data Logging Test: PASSED")
    else:
        print(f"  Analysis saving in Sheet: FAILED. Error: {save_result.get('error')}")
        print("  Data Logging Test: FAILED")
        return

    print("\n==============================================")
    print("🎉 ALL TESTS PASSED SUCCESSFULLY! 🎉")
    print("Your FastAPI scraping pipeline, calculations, and Google Sheets")
    print("database integrations are 100% working.")
    print("Check your Google Sheet now - you will see the new user and stock rows!")
    print("==============================================")

if __name__ == "__main__":
    run_test()