Eastradge Medical Hospital — MedInvest Uganda
Complete reconstructed local demo build

Contents:
- index.html: complete responsive single-page demo application.

This is a complete reconstruction based on the source fragments and detailed
descriptions retained in the conversation. It is not a byte-for-byte recovery
of every original pasted line from Parts 2–9. The original snippets that were
available have informed the layout, names, product catalogue, balances and
behaviour; missing markup was rebuilt so the app can run locally.

Run in Termux:
  pkg install python -y
  cd /storage/emulated/0/Download/Eastradge_Complete
  python -m http.server 8080
Then open http://127.0.0.1:8080

Tailwind, Google Fonts and Lucide are loaded from CDNs, so internet access is
needed for those external assets. The app's balances, leases and transactions
are local demo data only. No real MTN MoMo/Airtel Money payment or payout occurs.
The displayed income/return figures are illustrative and are not guarantees.
