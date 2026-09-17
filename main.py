import os
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import jwt

# ==========================================
# 1. APP INITIALIZATION & CORS
# ==========================================
app = FastAPI(
    title="AgriConnect API",
    description="Smart Market Linkage, Price Discovery & Escrow State Machine",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 2. MOCK DATABASES & SECURITY
# ==========================================
OTP_STORE: Dict[str, str] = {}
ORDERS_DB: Dict[str, dict] = {}
SECRET_KEY = "hackathon_super_secret_key_2026"
ALGORITHM = "HS256"
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ==========================================
# 3. PYDANTIC SCHEMAS
# ==========================================
class AuthRequest(BaseModel):
    mobile: str

class VerifyOTPRequest(BaseModel):
    mobile: str
    otp: str

class ChatRequest(BaseModel):
    message: str

class OrderCreateRequest(BaseModel):
    buyer_id: str
    crop: str
    quantity_kg: float
    agreed_rate: float

class DeliveryVerifyRequest(BaseModel):
    delivery_otp: str

# ==========================================
# 4. AUTHENTICATION ENDPOINTS
# ==========================================
@app.post("/api/auth/send-otp", tags=["Auth"])
async def send_otp(request: AuthRequest):
    mock_otp = str(random.randint(100000, 999999))
    OTP_STORE[request.mobile] = mock_otp
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🔐 LOGIN OTP for {request.mobile} is: {mock_otp}\n")
    return {"message": "OTP sent successfully"}

@app.post("/api/auth/verify-otp", tags=["Auth"])
async def verify_otp(request: VerifyOTPRequest):
    stored_otp = OTP_STORE.get(request.mobile)
    if not stored_otp or stored_otp != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    expire = datetime.now(timezone.utc) + timedelta(hours=48)
    token = jwt.encode({"sub": request.mobile, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    del OTP_STORE[request.mobile]
    return {"access_token": token, "token_type": "bearer"}

# ==========================================
# 5. ESCROW & ORDER STATE MACHINE
# ==========================================
@app.post("/api/orders", tags=["Order Lifecycle"])
async def create_order(request: OrderCreateRequest, user: str = Depends(get_current_user)):
    order_id = f"ORD-{random.randint(1000,9999)}"
    
    ORDERS_DB[order_id] = {
        "farmer": user,
        "details": request.dict(), # Pydantic v1 compatible .dict()
        "status": "OFFER_ACCEPTED",
        "delivery_otp": str(random.randint(100000, 999999)),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    return {"order_id": order_id, "status": "OFFER_ACCEPTED"}

@app.patch("/api/orders/{order_id}/lock-escrow", tags=["Order Lifecycle"])
async def lock_escrow(order_id: str, user: str = Depends(get_current_user)):
    if order_id not in ORDERS_DB:
        raise HTTPException(status_code=404, detail="Order not found")
    ORDERS_DB[order_id]["status"] = "ESCROW_LOCKED"
    return {"order_id": order_id, "status": "ESCROW_LOCKED"}

@app.patch("/api/orders/{order_id}/in-transit", tags=["Order Lifecycle"])
async def dispatch_transit(order_id: str, user: str = Depends(get_current_user)):
    if order_id not in ORDERS_DB:
        raise HTTPException(status_code=404, detail="Order not found")
    ORDERS_DB[order_id]["status"] = "IN_TRANSIT"
    delivery_otp = ORDERS_DB[order_id]["delivery_otp"]
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🚚 DELIVERY OTP for Order {order_id} is: {delivery_otp}\n")
    return {"order_id": order_id, "status": "IN_TRANSIT"}

@app.patch("/api/orders/{order_id}/verify-delivery", tags=["Order Lifecycle"])
async def verify_delivery(order_id: str, request: DeliveryVerifyRequest, user: str = Depends(get_current_user)):
    order = ORDERS_DB.get(order_id)
    if not order or order["status"] != "IN_TRANSIT":
        raise HTTPException(status_code=400, detail="Order must be in transit.")
    if request.delivery_otp != order["delivery_otp"]:
        raise HTTPException(status_code=403, detail="Invalid Delivery OTP.")
    order["status"] = "DELIVERY_VERIFIED"
    return {"order_id": order_id, "status": "DELIVERY_VERIFIED"}

@app.patch("/api/orders/{order_id}/release-payment", tags=["Order Lifecycle"])
async def release_payment(order_id: str, user: str = Depends(get_current_user)):
    order = ORDERS_DB.get(order_id)
    if not order or order["status"] != "DELIVERY_VERIFIED":
        raise HTTPException(status_code=400, detail="Order must be verified first.")
        
    qty = order["details"]["quantity_kg"]
    rate = order["details"]["agreed_rate"]
    
    gross_revenue = qty * rate
    freight_cost = 800.00
    cess = gross_revenue * 0.015
    nrv = gross_revenue - freight_cost - cess
    
    order["status"] = "PAYMENT_RELEASED"
    return {
        "order_id": order_id,
        "status": "PAYMENT_RELEASED",
        "settlement": {
            "gross_revenue": gross_revenue,
            "freight_deduction": freight_cost,
            "cess_deduction": cess,
            "net_realizable_value_transferred": nrv
        }
    }

# ==========================================
# 6. AI ASSISTANT ENDPOINT
# ==========================================
@app.post("/api/chat", tags=["AI"])
async def chat_assistant(request: ChatRequest, user: str = Depends(get_current_user)):
    msg = request.message.lower()
    if "sell" in msg or "hold" in msg:
        reply = "AI signal abhi 'Hold & Wait' hai, par tomato jaise perishable crops ke liye turant dispatch karna behtar hai."
    else:
        reply = "Namaste! AgriConnect backend is live and fully connected."
    return {"reply": reply}