# Footer & Gallery Setup

## Footer - One Line with Copy

### Option 1: Add Script Tag (Easiest)

Add this before `</body>` in `gallery.html`:

```html
<script src="footer_copy.js"></script>
```

This will:
- Make the entire footer line clickable
- Copy version info when clicked
- Show visual feedback (green flash)

### Option 2: Inline Script

Add this JavaScript to `gallery.html`:

```javascript
// Make version footer clickable
document.addEventListener('DOMContentLoaded', () => {
    const container = document.querySelector('.version-info') || 
                     document.querySelector('.version-footer');
    
    if (container) {
        container.style.cursor = 'pointer';
        container.title = 'Click to copy version info';
        container.style.userSelect = 'text';
        
        container.addEventListener('click', () => {
            const version = document.getElementById('app-version')?.textContent || 'Loading...';
            const build = document.getElementById('app-build-timestamp')?.textContent || 'Loading...';
            const deployed = document.getElementById('app-build-date')?.textContent || 'Loading...';
            const sdk = document.getElementById('app-firebase-sdk')?.textContent || '10.7.1';
            
            const text = `Version: ${version} | Build: ${build} | Deployed: ${deployed} | Firebase SDK: ${sdk}`;
            
            navigator.clipboard.writeText(text).then(() => {
                container.style.backgroundColor = '#d4edda';
                setTimeout(() => container.style.backgroundColor = '', 500);
                console.log('✓ Copied:', text);
            });
        });
    }
});
```

---

## How to Use Gallery Page

### 1. Open Gallery
Go to: `https://hv-ecg.web.app/gallery.html`

### 2. Copy Version Info
- **Click anywhere on the footer line** - Copies to clipboard
- **Or manually select** the text and copy

### 3. Bulk Testing

**In browser console (F12):**

```javascript
// Quick test all images
quickBulkTest();

// Or wait for images first
setTimeout(() => quickBulkTest(), 3000);
```

### 4. Individual Functions

```javascript
// Edge detection
const img = document.querySelector('.gallery-item img');
detectEdges(img, 'canny', true).then(console.log);

// Process batch
const images = Array.from(document.querySelectorAll('.gallery-item img')).slice(0, 5);
processBatch(images, {
    edge_detection: true,
    color_separation: true
}).then(console.log);
```

---

## Deploy Updates

### 1. Deploy Footer Script
```powershell
# If using footer_copy.js, make sure it's in public/ folder
firebase deploy --only hosting
```

### 2. Deploy Gallery Updates
```powershell
firebase deploy --only hosting
```

---

*Setup Guide - January 21, 2026*
