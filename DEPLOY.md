# Deploy MarginLab (GitHub + Streamlit Cloud, free)

Written for a non-developer on Windows. ~15 minutes. Everything here is free.

---

## What you're deploying

This is a **new, self-contained app**. It does not patch your old code — it
replaces it. The whole thing lives in this one folder. You have two clean options:

- **Option A (recommended):** put it in a **new repo** and a **new Streamlit app**,
  leave your current one untouched until you're happy. Zero risk.
- **Option B:** replace the contents of your existing `lixiefel/Felix` repo.

Instructions below are for Option A. For Option B, skip to the note at the end.

---

## Step 1 — Create a new GitHub repo

1. Go to https://github.com/new
2. Repository name: `marginlab-workspace` (anything is fine)
3. Keep it **Private**. Don't add a README (this folder already has one).
4. Click **Create repository**.

## Step 2 — Upload the files

Easiest path, no Git install needed:

1. On the new empty repo page, click **uploading an existing file**.
2. Open this folder on your PC. Select **everything inside it**:
   - `app.py`, `requirements.txt`, `README.md`, `DEPLOY.md`, `.gitignore`
   - the `marginlab/` folder
   - the `.streamlit/` folder
   - `MarginLab_Pricing_Lab_v10.xlsx`
3. Drag them all into the GitHub upload area.

   ⚠️ GitHub's web uploader sometimes flattens folders. If after upload you do
   **not** see `marginlab/` and `.streamlit/` as folders in the repo, the
   reliable fix is GitHub Desktop:
   - Install https://desktop.github.com/
   - **File → Clone repository →** pick your new repo
   - Copy this whole folder's contents into the cloned folder on disk
   - In GitHub Desktop: type a summary → **Commit to main** → **Push origin**

4. Confirm the repo shows the `marginlab/` folder with `engine/` and `ui/` inside.

## Step 3 — Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io and sign in with GitHub.
2. **Create app → Deploy a public app from GitHub** (private repos work on the free tier too).
3. Fill in:
   - **Repository:** `your-username/marginlab-workspace`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Click **Deploy**. First build takes 2–4 minutes while it installs dependencies.
5. When it loads, click **Load demo café** on the first page to confirm it works.

That's it — you'll get a URL like `https://marginlab-workspace.streamlit.app`.

---

## Step 4 — First-run check (60 seconds)

On the live app:
1. **Client** page → **Load demo café** → **Continue**.
2. **Menu & Cost** → confirm the table is populated → **Run analysis**.
3. **Analysis** → you should see the headline lift, the quadrant chart, and the table.
4. Click through **Opportunities → Recommendations → Scenarios → Final Review**.
5. On **Scenarios**, drag the "Max raise" slider — the projected lift should move live.
6. On **Final Review**, click **Download model (XLSX)** — the workbook should download.

If all six work, you're live.

---

## Troubleshooting

- **"Error installing requirements" on deploy.** Open `requirements.txt` — it should
  be exactly four lines. Streamlit Cloud reads it automatically; no action needed beyond
  having the file in the repo root.
- **App loads but looks unstyled / plain.** The Google Fonts link is blocked on the very
  first paint sometimes; refresh once. The `.streamlit/config.toml` ensures the colours are
  right even before fonts load.
- **Charts don't show.** Confirm `plotly` is in `requirements.txt` (it is) and the build
  log shows it installed. Reboot the app from **Manage app → Reboot**.
- **"File not found" on the XLSX download.** Confirm `MarginLab_Pricing_Lab_v10.xlsx` is in
  the **repo root** (same level as `app.py`), not inside a subfolder.
- **Changes don't appear after editing on GitHub.** Streamlit auto-redeploys on push;
  give it ~1 minute, then hard-refresh (Ctrl+Shift+R). Or **Manage app → Reboot**.

---

## Updating later

Edit a file on GitHub (pencil icon) → Commit. Streamlit redeploys automatically in
about a minute. No other steps.

---

## Option B — replacing your existing repo

If you'd rather keep the same repo/URL:
1. In `lixiefel/Felix`, delete the old app files (or move them to an `old/` folder).
2. Upload everything from this folder to the repo root (Step 2 above).
3. In Streamlit Cloud, make sure the app's **Main file path** is `app.py`.
4. Reboot the app.

Keep a copy of the old code first — you can't show a half-replaced repo to a client.
