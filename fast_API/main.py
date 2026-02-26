from fastapi import FastAPI
import pandas as pd

app = FastAPI()

# Load CSV once when server starts
df = pd.read_csv("nifty50.csv")

@app.get("/")
def home():
    return {"message": "Welcome to DataDash Analytics API"}

# Get total rows
@app.get("/total-rows")
def total_rows():
    return {"total_rows": len(df)}

# Get column names
@app.get("/columns")
def get_columns():
    return {"columns": list(df.columns)}

# Example: Get average of a numeric column (change column name accordingly)
@app.get("/average-close")
def average_close():
    if "Close" in df.columns:
        return {"average_close": float(df["Close"].mean())}
    return {"error": "Column 'Close' not found"}
