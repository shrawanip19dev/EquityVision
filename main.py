from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from auth import UserRegister, UserLogin, StockAnalysisRequest
from google_sheet import register_user_in_sheet, validate_user_in_sheet, save_analysis_result, get_analysis_history
from scraper import scrape_stock_data
from calculator import calculate_valuation

app = FastAPI(
    title="EquityVision API",
    description="Backend service for stock scraper, calculator, and Google Sheets database storage.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "app": "EquityVision",
        "status": "running",
        "message": "Welcome to the EquityVision FastAPI backend!"
    }

@app.post("/register")
def register(user: UserRegister):
    res = register_user_in_sheet(user.username, user.password)
    print("REGISTER RESPONSE  :",res)
    if res.get("status") == "success":
        return {
            "status": "success",
            "message": "User registered successfully in Google Sheets."
        }
    elif res.get("status") == "exists":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists."
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=res.get("error", "Failed to register user in Google Sheets.")
        )

@app.post("/login")
def login(user: UserLogin):
    success = validate_user_in_sheet(user.username, user.password)
    if success:
        return {
            "status": "success",
            "message": "Login successful."
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )

@app.post("/analyze")
def analyze(req: StockAnalysisRequest):
    symbol = req.symbol.strip().upper()
    if not symbol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock symbol cannot be empty."
        )
        
    try:
        # 1. Scrape raw data from Screener
        raw_data = scrape_stock_data(symbol)
        
        current_price = raw_data["current_price"]
        stock_pe = raw_data["stock_pe"]
        current_eps = raw_data["current_eps"]
        eps_3yr_ago = raw_data["eps_3yr_ago"]
        historical_return = raw_data["historical_return_3yr"]
        stock_name = raw_data["stock_name"]
        
        # Validate that we got numbers
        if current_price is None or current_eps is None or eps_3yr_ago is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Incomplete financial data extracted for {symbol}. Scraping yielded: Price: {current_price}, EPS: {current_eps}, 3Yr Ago EPS: {eps_3yr_ago}"
            )
            
        # 2. Run Valuation Calculations
        analysis = calculate_valuation(
            current_eps=current_eps,
            eps_3yr_ago=eps_3yr_ago,
            stock_pe=stock_pe,
            current_price=current_price,
            required_return_annual=req.required_return
        )
        
        # 3. Store Results in Google Sheet
        save_res = save_analysis_result(
            stock_name=stock_name,
            current_price=current_price,
            fair_value=analysis["fair_value"],
            profit=analysis["profit"]
        )
        if save_res.get("status") != "success":
            print(f"Warning: Failed to save results to Google Sheets: {save_res.get('error')}")
            
        # 4. Construct response
        return {
            "symbol": symbol,
            "stock_name": stock_name,
            "current_price": current_price,
            "stock_pe": stock_pe if stock_pe else "N/A",
            "current_eps": current_eps,
            "eps_3yr_ago": eps_3yr_ago,
            "historical_return_3yr": historical_return,
            "required_return": req.required_return,
            
            # Calculated metrics
            "eps_growth_cagr": analysis["eps_growth_cagr"],
            "future_eps": analysis["future_eps"],
            "future_price": analysis["future_price"],
            "fair_value": analysis["fair_value"],
            "profit": analysis["profit"],
            "upside_percent": analysis["upside_percent"],
            "margin_of_safety": analysis["margin_of_safety"],
            "status": analysis["status"]
        }
        
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during analysis: {str(e)}"
        )

@app.get("/history")
def get_history():
    history = get_analysis_history()
    return {
        "status": "success",
        "data": history
    }
