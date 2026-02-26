from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import pandas as pd

# 1.connection to database in postgresql
DATABASE_URL = "postgresql://postgres:9999@localhost:5432/Micro_project"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Model - updated to match csv file columns in database
class NiftyData(Base):
    __tablename__ = "timestamp" 
    
    timestamp = Column(String, primary_key=True, index=True) 
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    dt = Column(String)
    time = Column(Float)

app = FastAPI()

# 3. DB Session Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"status": "Connected to PostgreSQL!"}

# 4. GET Route to fetch data
@app.get("/get-all-data")
def read_nifty_data(db: Session = Depends(get_db)):
    # it helps to return the first 100 rows from the csv file
    data = db.query(NiftyData).limit(100).all()
    return data

# 5. UPLOAD Route to the csv file
@app.get("/upload-my-csv")
def upload_csv():
    try:
        df = pd.read_csv("nifty50.csv") 
        
        # This pushes the data into the 'timestamp' table
        # 'replace':It ensures the table structure that matches to the csv  exactly
        df.to_sql('timestamp', con=engine, if_exists='replace', index=False)
        
        return {"message": f"Success! Uploaded {len(df)} rows from nifty50.csv"}
    except Exception as e:
        return {"error": str(e)}

    return {"error": "Timestamp not found"}
    # Helps to search data for a specific date
@app.get("/get-by-date/{date_val}")
def get_by_date(date_val: str, db: Session = Depends(get_db)):
    results = db.query(NiftyData).filter(NiftyData.dt == date_val).all()
    if not results:
        return {"message": f"No records found for {date_val}"}
    return results

# 7. To get the high-low spread for a specific date
@app.get("/analytics/spread/{ts}")
def get_spread(ts: str, db: Session = Depends(get_db)):
    record = db.query(NiftyData).filter(NiftyData.timestamp == ts).first()
    if record:
        spread = record.high - record.low
        return {
            "timestamp": record.timestamp,
            "spread": round(spread, 2),
            "is_volatile": spread > 5.0  
        }
    return {"error": "Timestamp not found"}
@app.get("/analytics/volatility")
def get_volatility_report(limit: int = 10, db: Session = Depends(get_db)):
    #  changing the number of records from the UI!
    records = db.query(NiftyData).limit(limit).all()
    analysis = []
    for r in records:
        analysis.append({
            "timestamp": r.timestamp,
            "range": round(r.high - r.low, 2),
            "trend": "Bullish (Up)" if r.close > r.open else "Bearish (Down)"
        })
    return analysis