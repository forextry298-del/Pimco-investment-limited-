PIMCO Products Update v2

Overlay contents:
- Replaces templates/equipment.html
- Includes 20 product card image files, using 8 different uploaded medical product/clinic images in rotation
- Each plan shows purchase price, daily income, duration, total projected income, and purchase functionality
- Removed the word "demo" from visible product page copy and removed literal escaped newline sequences
- Kept a concise disclosure that projected figures are illustrative and not guaranteed

Install in Termux:
cd ~/pimco_investment || exit 1
cp templates/equipment.html templates/equipment.html.backup-v2
unzip -o ~/storage/downloads/pimco_products_update_v2.zip -d ~/pimco_investment

The ZIP does not modify app.py or the database.
