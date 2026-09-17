# AgriConnect
 
Helping farmers get a fair price by showing them what they'll *actually* take home, not just the number on the board at the mandi.
 
## The Problem
 
Smallholder farmers across India often end up losing money even when the mandi price looks good on paper. Why? Because nobody's accounting for the freight cost of getting the produce there, the APMC cess, or the middlemen taking a cut along the way. Most platforms just show gross prices at faraway mandis — they don't tell farmers what they'll actually walk away with. That gap is where farmers lose the most.
 
## What We Built
 
AgriConnect is a marketplace that connects farmers and FPOs directly with buyers, but the core idea is simple: instead of showing raw mandi prices, we calculate the **Net Realizable Value (NRV)** — the actual profit after subtracting transport and handling costs — so farmers can pick the mandi that's genuinely most profitable, not just the one with the highest sticker price.
 
On top of that, we added ML-based price forecasting, a buyer-matching system, and a secure escrow flow with QR-based delivery tracking, so the whole transaction  from listing to payment stays transparent and trustworthy for both sides.
 
## Features
 
- **NRV Optimization** — Ranks mandis by real take-home profit, factoring in freight and APMC cess, not just gross price.
- **AI Price Forecasting** — Uses an XGBoost model trained on historical prices to predict short-term trends and give a data-backed hold/sell recommendation.
- **Smart Buyer & FPO Matching** — Connects farmers with bulk buyers based on crop quality, quantity, and location.
- **QR-Based Order Tracking** — Follows produce through a clear chain of custody: Created → In Transit → Delivered.
- **Secure Escrow with OTP Verification** — Buyer funds sit in escrow and only release once delivery is confirmed, with an automatic, transparent payment split.
- **Multilingual AI Assistant** — Built on Gemini, so farmers who aren't comfortable with English or complex apps can still get help navigating listings in their own language.
## Tech Stack
 
- **Backend:** Python, FastAPI, JWT Authentication, Firebase / DB layer
- **Frontend:** HTML5, CSS3, Vanilla JavaScript, QRCode.js
- **AI/ML:** XGBoost for price forecasting, Google Gemini API for vernacular assistance
## How It Works
 
1. **List the crop** — Farmer logs in and enters details: crop type, quantity, harvest location.
2. **Compare NRV across mandis** — The system ranks nearby mandis by predicted price minus freight cost, not raw price.
3. **Get an AI forecast** — A time-series model gives a short-term price trend and a clear hold/sell suggestion.
4. **Buyer matching** — Verified buyers or FPOs review the listing and place an order into escrow.
5. **Lock escrow & dispatch** — Funds are locked, and a unique QR code is generated for the shipment.
6. **Delivery & auto-release** — Once delivered, scanning the QR and verifying the OTP releases the escrow automatically, with a clear breakdown of every deduction.
## Running It Locally
 
Clone the repo:
 
```bash
git clone https://github.com/your-username/agriconnect.git
cd agriconnect
```
 
Set up the backend:
 
```bash
cd backend
python -m venv venv
 
# Windows
venv\Scripts\activate
 
# macOS/Linux
source venv/bin/activate
```
 
Install dependencies:
 
```bash
pip install -r requirements.txt
```
 
Run the server:
 
```bash
uvicorn main:app --reload
```
 
Then just open `index.html` in your browser (or use a Live Server extension in VS Code) to see the frontend.
 
## Team
 
Team Avenix
 
## A Note on the Demo
 
For this prototype, delivery OTPs are printed to the console rather than sent via an actual SMS gateway. In a production version, this would plug into a service like MSG91 to send real OTPs to farmers and buyers.
 
