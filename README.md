# 🌿 Aonla Connect — Setup Guide

WhatsApp-style chat app built with Python + Streamlit + Supabase + Cloudinary.

---

## 📁 File Structure

```
aonla_connect/
├── app.py                    ← Main app (yahi run karo)
├── requirements.txt
├── supabase_schema.sql       ← DB tables (ek baar Supabase mein run karo)
├── .streamlit/
│   └── secrets.toml          ← Apne keys yahan daalo
└── utils/
    ├── __init__.py
    ├── auth.py               ← Login / Register
    ├── db.py                 ← Supabase + Cloudinary
    └── ai.py                 ← Jitarth AI integration
```

---

## 🚀 Setup Steps

### Step 1 — Supabase Setup
1. **supabase.com** pe jao → New Project banao
2. SQL Editor open karo
3. `supabase_schema.sql` ka sara content paste karo aur Run karo
4. Project Settings → API se copy karo:
   - `Project URL` → `SUPABASE_URL`
   - `anon/public key` → `SUPABASE_KEY`

### Step 2 — Cloudinary Setup
1. **cloudinary.com** pe free account banao
2. Dashboard se copy karo:
   - Cloud name → `CLOUDINARY_CLOUD_NAME`
   - API Key → `CLOUDINARY_API_KEY`
   - API Secret → `CLOUDINARY_API_SECRET`

### Step 3 — Secrets File
`.streamlit/secrets.toml` mein apni keys daalo:

```toml
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGci..."

CLOUDINARY_CLOUD_NAME = "your-cloud"
CLOUDINARY_API_KEY    = "123456"
CLOUDINARY_API_SECRET = "abcdef"

# AI Options (ek choose karo):
JITARTH_AI_API = ""          # Tera Streamlit AI ka REST endpoint (agar hai)
ANTHROPIC_API_KEY = ""       # Ya Claude API key (fallback)
```

### Step 4 — Install & Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 🤖 AI Integration — Jitarth AI

Abhi 2 options hain:

**Option A (Best):** Agar tera `jitarth-ai.streamlit.app` koi REST API endpoint expose karta hai:
- `JITARTH_AI_API` mein woh URL daal do
- Example: `https://jitarth-ai.streamlit.app/api/query`

**Option B (Fallback):** Anthropic Claude API:
- `ANTHROPIC_API_KEY` mein apni key daal do
- Haiku model use hoga (fast + cheap)

---

## ✅ Features

| Feature | Status |
|---------|--------|
| Login / Register | ✅ |
| Main Group Chat (Aonla Connect) | ✅ |
| Private DM Chats | ✅ |
| Private Groups (create, add members) | ✅ |
| File/Image Upload (Cloudinary) | ✅ |
| AI Chat (Jitarth AI) | ✅ |
| Admin hidden in Main Group | ✅ |
| Admin visible in Private Groups | ✅ |
| Call/Video (UI only, WebRTC needed) | ⚠️ |
| Real-time (auto-refresh) | ⚠️ Manual refresh |

---

## ⚠️ Notes

- **Call/Video:** Streamlit mein native WebRTC nahi hota. Real calls ke liye Daily.co ya Agora SDK integrate karna hoga ya ek alag React frontend banana hoga.
- **Real-time messages:** Streamlit auto-refresh nahi karta. "Refresh" button ya `st.rerun()` on timer lagana hoga production mein.
- **Security:** Production mein Supabase RLS policies strict rakho aur service_role key use karo.
