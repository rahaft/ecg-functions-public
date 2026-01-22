# Gallery Pagination & Lazy Loading

## ✅ What's New

The gallery now has **pagination** to improve performance:

- ✅ **Lazy loading** - Only loads 30 images or 3 groups at a time
- ✅ **"Load More" button** - Loads next batch when clicked
- ✅ **Smart grouping** - Respects both group and image limits
- ✅ **Performance** - Faster initial load, smoother scrolling

---

## 🎯 How It Works

### Initial Load
- Shows **up to 3 groups** OR **30 images** (whichever limit is hit first)
- Groups are sorted: Train → Test → Others

### Load More Button
- Click to load next batch
- Shows remaining group count
- Button disappears when all groups are loaded

### Limits
- **Groups per page:** 3 groups maximum
- **Images per page:** 30 images maximum
- **Whichever limit is hit first** applies

---

## 📋 Configuration

You can adjust these limits in `gallery.html`:

```javascript
const GROUPS_PER_PAGE = 3;  // Show 3 groups at a time
const IMAGES_PER_PAGE = 30; // Or 30 images total
```

---

## 🎨 Features

### Group Headers
- 📚 Train groups
- 🧪 Test groups  
- 📁 Other groups
- Shows image count per group

### Lazy Loading
- Images use `loading="lazy"` attribute
- Browser loads images as you scroll
- Reduces initial page load time

### Load More Button
- Appears at bottom of gallery
- Shows remaining groups count
- Auto-hides when all loaded
- Smooth loading animation

---

## 🧪 Testing Still Works

All testing functions work with paginated images:

```javascript
// Test visible images (up to 10)
quickBulkTest()

// Test specific group
testGroup('test')

// Test with options
bulkTestGallery({ edge_detection: true }, 'train')
```

---

## 💡 Benefits

1. **Faster initial load** - Only loads 30 images instead of 8,795
2. **Better performance** - Less DOM elements, smoother scrolling
3. **Lower bandwidth** - Images load on demand
4. **Better UX** - Users can choose when to load more

---

**The gallery now loads efficiently with pagination!** 🚀
