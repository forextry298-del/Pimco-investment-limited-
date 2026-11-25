# ITALIAN — Strategic Investment & Defense Capital

This project packages the uploaded ITALIAN HTML interface as a static website.

## Included

- `index.html` — the uploaded HTML, preserved unchanged and renamed as the website entry page
- `render.yaml` — Render static-site deployment blueprint
- `.gitignore` — common local/editor exclusions

## Important deployment and functionality notes

This package contains the HTML file supplied by the user. It does not add a server, database,
payment gateway, authentication service, or secure admin API.

The page references browser-side behavior and third-party CDN resources. Any data stored by
the page in browser storage is local to that browser/device and is not a shared account database.
A static Render deployment cannot securely process or verify deposits, withdrawals, transfers,
investment returns, referral payouts, or administrator approvals.

Do not accept real deposits or promise/issue real financial returns based only on this static
frontend. Before using it with real users or money, have the financial model and claims reviewed,
and build a secure backend with server-side authentication, authorization, transaction records,
payment verification, and audit logging. Defense-related donation options should not be used to
collect or route real funds through this static demo.

## Deploy with Termux + GitHub + Render

1. Extract this ZIP in Termux.
2. Create an empty GitHub repository named `italian-investment-platform` (do not add a README there).
3. In the extracted project directory, run:

```bash
git init
git add .
git commit -m "Add ITALIAN platform frontend"
git branch -M main
git remote add origin https://github.com/YOUR-GITHUB-USERNAME/italian-investment-platform.git
git push -u origin main
```

Replace `YOUR-GITHUB-USERNAME` with your GitHub username.

4. In Render, choose **New + → Blueprint** (or **New + → Static Site**).
5. Connect the GitHub repository. If using the Blueprint, Render reads `render.yaml`.
6. Deploy. The published site uses `index.html` as its entry page.

For a manual Static Site on Render:
- Build command: leave empty
- Publish directory: `.`
