# 1️ IMPORTS
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

# 2️ DATABASE CONFIG

DATABASE_URL = "postgresql://postgres:9999@localhost:5432/Micro_project"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 3️ DATABASE MODEL

class NiftyData(Base):
    __tablename__ = "timestamp"   

    timestamp = Column(String, primary_key=True, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    dt = Column(String)
    time = Column(Float)
# 4️⃣ Pydantic Schema (For CRUD)
class NiftyCreate(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    dt: str
    time: float


# 5️⃣ FastAPI App
app = FastAPI()

# CORS for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# 6️ Database Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# 7️ ROOT CHECK
@app.get("/")
def root():
    return {"message": "FastAPI connected to PostgreSQL successfully!"}

# 8️ ANALYTICS APIs

# Trend (Line Chart)
@app.get("/analytics/trend")
def get_trend(db: Session = Depends(get_db)):
    # REMOVED .limit(100) so the chart shows the full timeline
    data = db.query(NiftyData.timestamp, NiftyData.close).order_by(NiftyData.dt.asc()).all()
    return [{"timestamp": d[0], "close": d[1]} for d in data]

#  KPI Summary
@app.get("/analytics/summary")
def summary(db: Session = Depends(get_db)):
    records = db.query(NiftyData).all()
    total = len(records)

    if total == 0:
        return {"message": "No data found"}

    avg_close = sum(r.close for r in records) / total
    max_high = max(r.high for r in records)
    min_low = min(r.low for r in records)

    return {
        "total_records": total,
        "average_close": round(avg_close, 2),
        "max_high": max_high,
        "min_low": min_low
    }


# Filter by Date
@app.get("/filter/{date_val}")
def filter_date(date_val: str, db: Session = Depends(get_db)):
    results = db.query(NiftyData).filter(NiftyData.dt == date_val).all()
    if not results:
        return {"message": "No data found for this date"}
    return [vars(r) for r in results]


# Spread Analysis
@app.get("/analytics/spread/{ts}")
def spread(ts: str, db: Session = Depends(get_db)):
    record = db.query(NiftyData).filter(NiftyData.timestamp == ts).first()
    if not record:
        raise HTTPException(status_code=404, detail="Timestamp not found")

    spread_value = record.high - record.low

    return {
        "timestamp": record.timestamp,
        "spread": round(spread_value, 2),
        "trend": "Up" if record.close > record.open else "Down"
    }


# Correlation Heatmap Data
@app.get("/analytics/correlation")
def correlation(db: Session = Depends(get_db)):
    records = db.query(NiftyData).all()

    if not records:
        return {"message": "No data available"}

    df = pd.DataFrame([
        {
            "open": r.open,
            "high": r.high,
            "low": r.low,
            "close": r.close
        }
        for r in records
    ])

    corr = df.corr()
    return corr.to_dict()
# 9️ CRUD APIs
#  CREATE
@app.post("/data")
def create_data(data: NiftyCreate, db: Session = Depends(get_db)):
    existing = db.query(NiftyData).filter(NiftyData.timestamp == data.timestamp).first()
    if existing:
        raise HTTPException(status_code=400, detail="Timestamp already exists")

    new_record = NiftyData(**data.dict())
    db.add(new_record)
    db.commit()

    return {"message": "Record inserted successfully"}


#  READ
@app.get("/data")
def read_data(db: Session = Depends(get_db)):
    # REMOVED .limit(200) to allow 2-3 years of data to load
    records = db.query(NiftyData).order_by(NiftyData.dt.asc()).all()
    return [vars(r) for r in records]


#  UPDATE
@app.put("/data/{timestamp}")
def update_data(timestamp: str, data: NiftyCreate, db: Session = Depends(get_db)):
    record = db.query(NiftyData).filter(NiftyData.timestamp == timestamp).first()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    for key, value in data.dict().items():
        setattr(record, key, value)

    db.commit()

    return {"message": "Record updated successfully"}


#  DELETE
@app.delete("/data/{timestamp}")
def delete_data(timestamp: str, db: Session = Depends(get_db)):
    record = db.query(NiftyData).filter(NiftyData.timestamp == timestamp).first()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    db.delete(record)
    db.commit()

    return {"message": "Record deleted successfully"}