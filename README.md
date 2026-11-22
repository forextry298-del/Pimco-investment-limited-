# PIMCO Investment Platform — Local 

## Run locally (Termux / Linux / macOS / Windows)

1. Extract `pimco_investment.zip`.
2. Open a terminal in the extracted `pimco_investment` folder.
3. Install dependencies:
   `pip install -r requirements.txt`
4. Start the app:
   `python app.py`
5. Open `http://127.0.0.1:5000` in your browser.

### Termux quick start
```sh
pkg update -y
pkg install python unzip -y
unzip pimco_investment.zip
cd pimco_investment
pip install -r requirements.txt
python app.py
```

Create an account with a test name, phone number and password (minimum 6 characters), then complete the medical form. Log out and use Member Login to sign in again.

## Included
- Responsive, compact mobile-first UI; viewport is fixed against pinch zoom.
- Registration and login with password hashing; local SQLite database.
- Medical profile form shown after registration/login until completed.
- Home, Equipment, Earning and Profile pages with bottom navigation.
- Deposit and withdrawal  modals, preset amounts and locally recorded activity.
- Auto-rotating home hero and Lucide icon set.

## Important  limitations
This is a local prototype. Deposit/withdrawal requests are stored as ** pending** records only. It does not connect to MTN, Airtel, a bank, payment processor, real investment ledger, or product delivery. Balances and earnings are placeholders, not real funds or returns. Do not collect real medical information or real money with this prototype. Before any public launch, obtain legal/compliance review, implement secure production hosting, privacy controls, verified payment integrations, and truthful investment disclosures.

Icons are loaded from the Lucide CDN, so the device needs internet access for the icon library to render. All app routes and data storage run locally.
