# What is CORS and Why Configure It?

## 🔒 What is CORS?

**CORS** = **Cross-Origin Resource Sharing**

It's a browser security feature that controls which websites can access resources from other domains.

---

## 🚨 The Problem

When your website (`https://hv-ecg.web.app`) tries to load images from GCS buckets (`https://storage.googleapis.com`), the browser blocks it because:

- **Different domains** = Different "origins"
- Browser says: "This website can't access that resource!"
- **Result:** Images don't load, you see CORS errors in console

---

## ✅ What CORS Configuration Does

When you configure CORS on GCS buckets, you're telling Google Cloud:

> "Allow requests from `https://hv-ecg.web.app` to access images in these buckets"

**CORS rules specify:**
- ✅ **Which websites** can access (origins)
- ✅ **What methods** they can use (GET, POST, etc.)
- ✅ **What headers** they can send/receive
- ✅ **How long** to cache the permission (maxAgeSeconds)

---

## 📋 Example CORS Configuration

```json
[
  {
    "origin": [
      "https://hv-ecg.web.app",
      "https://hv-ecg.firebaseapp.com"
    ],
    "method": ["GET", "HEAD", "OPTIONS"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
```

This says:
- ✅ Allow `hv-ecg.web.app` to GET images
- ✅ Allow these response headers
- ✅ Cache permission for 1 hour

---

## ⚠️ Without CORS

- ❌ Images won't load
- ❌ Browser console shows: "CORS policy blocked"
- ❌ Gallery appears empty
- ❌ Fetch requests fail

---

## ✅ With CORS Configured

- ✅ Images load successfully
- ✅ Gallery displays images
- ✅ No console errors
- ✅ Everything works!

---

## 🔧 How to Configure

```powershell
python scripts/configure_gcs_cors.py
```

This sets CORS rules on all 5 GCS buckets to allow your website to access images.

---

**In simple terms: CORS is like a bouncer at a club - it decides which websites are allowed to access your images!** 🎫
