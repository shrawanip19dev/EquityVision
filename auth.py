from pydantic import BaseModel

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class StockAnalysisRequest(BaseModel):
    symbol: str
    required_return: float = 15.0  # default discount rate of 15%
