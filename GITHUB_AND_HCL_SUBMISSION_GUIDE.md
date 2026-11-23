# GitHub upload + HCL portal submission – step by step

## A. Before you upload (Windows, ~25 min total)
1. Install **Power BI Desktop** (Microsoft Store, free) and build the `.pbix` using `powerbi/POWERBI_BUILD_GUIDE.md` (30–40 min). Save it into `powerbi/Sales_Performance_Dashboard.pbix`.
2. (Optional but recommended) Install Oracle XE + SQL Developer, run the `sql/` scripts once and take 2–3 screenshots into `docs/`. If Oracle is not possible, say so honestly in the video – scripts are included and logic is verified.
3. Record the demo video with `demo/demo_video_script.md` (Win + Alt + R). Save as `demo/demo_video.mp4`. Large file? Upload to YouTube (Unlisted)/Google Drive and paste the link in README.

## B. GitHub (web, no commands)
1. github.com → **New repository** → name `sales-performance-dashboard` → Public → Create.
2. Click **uploading an existing file** → drag *everything inside* the unzipped project folder (keep folders) → Commit.
   (Files > 25 MB must use git commands below.)

## C. GitHub (command line, alternative)
```bash
cd sales-performance-dashboard
git init
git add .
git commit -m "Sales Performance Dashboard - Naitik Singh Bhadoriya (25003215410104)"
git branch -M main
git remote add origin https://github.com/<your-username>/sales-performance-dashboard.git
git push -u origin main
```
## D. HCL portal
Upload the **complete** project (the HCL team reviews it; blank/partial uploads are rejected):
* the zip `sales-performance-dashboard.zip` (or the files the portal asks for),
* the `.pbix`, the repo link, the demo video link, README.
Do it **before Monday 10:00 AM** and keep the upload confirmation screenshot.

## E. Final self-check
- [ ] `.pbix` opens; cards show ₹24.11 Cr and 8,947 orders
- [ ] Repo link opens in a private/incognito window
- [ ] README shows your name & roll number
- [ ] Demo video plays
