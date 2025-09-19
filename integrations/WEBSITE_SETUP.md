# Website Integration Setup Guide 🌐

*Connect your website to LangChain in minutes, no coding required*

## What You'll Need
- Access to your website admin panel
- 15-30 minutes of time
- Basic copy-paste skills

---

## WordPress Integration (60% of websites)

### Method 1: Plugin Installation (Easiest)
1. **Log into your WordPress dashboard** (usually yoursite.com/wp-admin)
2. **Click "Plugins"** in the left sidebar
3. **Click "Add New"** at the top
4. **Search for** "Custom HTML" or "Insert Headers and Footers"
5. **Click "Install Now"** on a plugin with good ratings
6. **Click "Activate"** after installation

### Method 2: Theme Editor (Advanced)
1. **Go to "Appearance"** in the left sidebar
2. **Click "Theme Editor"**
3. **Select "header.php"** from the file list
4. **Find the `</head>` tag**
5. **Add your integration code** just before `</head>`

### WordPress Integration Code
```html
<!-- Add this to your header.php or using a plugin -->
<script>
// LangChain Integration
window.langchainConfig = {
    apiKey: 'your-api-key-here',
    endpoint: 'your-endpoint-url',
    chatbotId: 'your-chatbot-id'
};
</script>
<script src="https://cdn.langchain.com/widget.js"></script>

<!-- Chat widget will appear automatically -->
```

### WordPress Troubleshooting
**Problem**: "Permission denied to edit files"
**Solution**: Use a plugin instead of theme editor

**Problem**: "Code disappeared after theme update"
**Solution**: Use a child theme or plugin for permanent changes

---

## Shopify Integration

### Step 1: Access Theme Editor
1. **Log into your Shopify admin** (yourstore.myshopify.com/admin)
2. **Click "Online Store"** in the left sidebar
3. **Click "Themes"**
4. **Find your active theme** and click **"Actions" → "Edit code"**

### Step 2: Add Integration Code
1. **Click on "theme.liquid"** in the left file tree
2. **Scroll down** to find the `</head>` tag
3. **Click just before** `</head>`
4. **Paste this code:**

```html
<!-- Shopify LangChain Integration -->
<script>
window.langchainConfig = {
    apiKey: '{{ settings.langchain_api_key }}',
    shopDomain: '{{ shop.domain }}',
    customerId: '{{ customer.id }}',
    cartTotal: '{{ cart.total_price | money_without_currency }}'
};
</script>
<script src="https://cdn.langchain.com/shopify-widget.js"></script>
```

5. **Click "Save"**

### Step 3: Add Settings (Optional)
1. **Go back to your theme list**
2. **Click "Customize"** on your active theme
3. **Click "Theme settings"** at the bottom
4. **Add a text field** for "LangChain API Key"
5. **Save your changes**

### Shopify Troubleshooting
**Problem**: "Changes don't appear on website"
**Solution**: Clear your browser cache and check if you edited the correct theme

**Problem**: "Code breaks website design"
**Solution**: Remove the code and contact support

---

## Wix Integration

### Step 1: Access Developer Tools
1. **Log into your Wix account** and select your site
2. **Click "Edit Site"**
3. **Click the "+" button** to add elements
4. **Select "Embed"** from the menu
5. **Choose "Custom Embeds" → "Embed HTML"**

### Step 2: Add Integration Code
1. **Click "Add Custom Code"**
2. **Choose "HTML"** as the code type
3. **Paste this code:**

```html
<div id="langchain-widget"></div>
<script>
window.langchainConfig = {
    apiKey: 'your-api-key-here',
    siteId: 'wix-site',
    container: 'langchain-widget'
};
</script>
<script src="https://cdn.langchain.com/widget.js"></script>
```

4. **Click "Update"**
5. **Position the widget** where you want it on your page
6. **Click "Publish"** to make changes live

### Wix Troubleshooting
**Problem**: "Custom code not allowed"
**Solution**: Upgrade to a premium Wix plan

**Problem**: "Widget appears too small"
**Solution**: Resize the embed container or adjust CSS

---

## Squarespace Integration

### Step 1: Access Code Injection
1. **Log into Squarespace** and select your site
2. **Go to "Settings"** in the main menu
3. **Click "Developer Tools"**
4. **Click "Code Injection"**

### Step 2: Add Integration Code
1. **Scroll to "Header"** section
2. **Paste this code:**

```html
<!-- Squarespace LangChain Integration -->
<script>
window.langchainConfig = {
    apiKey: 'your-api-key-here',
    platform: 'squarespace',
    siteId: '{{websiteId}}'
};

// Wait for page to load
document.addEventListener('DOMContentLoaded', function() {
    var script = document.createElement('script');
    script.src = 'https://cdn.langchain.com/widget.js';
    document.head.appendChild(script);
});
</script>
```

3. **Click "Save"**

### Squarespace Troubleshooting
**Problem**: "Code injection not available"
**Solution**: Upgrade to Business plan or higher

**Problem**: "Widget conflicts with site design"
**Solution**: Customize CSS or contact support

---

## Custom HTML Website

### For Static HTML Sites
1. **Open your HTML file** in a text editor
2. **Find the `<head>` section**
3. **Add this code** before the closing `</head>` tag:

```html
<!-- LangChain Integration for Custom HTML -->
<script>
window.langchainConfig = {
    apiKey: 'your-api-key-here',
    siteUrl: window.location.hostname,
    customStyling: true
};
</script>
<script src="https://cdn.langchain.com/widget.js"></script>

<!-- Custom styling (optional) -->
<style>
.langchain-widget {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 1000;
}
</style>
```

4. **Save the file**
5. **Upload to your web server**

### For React/Vue/Angular Sites
```javascript
// React example
import { useEffect } from 'react';

function App() {
  useEffect(() => {
    window.langchainConfig = {
      apiKey: 'your-api-key-here',
      framework: 'react'
    };

    const script = document.createElement('script');
    script.src = 'https://cdn.langchain.com/widget.js';
    document.head.appendChild(script);
  }, []);

  return (
    <div className="App">
      {/* Your app content */}
    </div>
  );
}
```

---

## Testing Your Integration

### 1. Visual Check
- **Look for the chat widget** (usually bottom-right corner)
- **Check if it matches your site design**
- **Verify it doesn't block important content**

### 2. Functionality Test
1. **Click on the chat widget**
2. **Type a test message**
3. **Verify you get a response**
4. **Test on both desktop and mobile**

### 3. Performance Check
- **Page should load normally** (no significant slowdown)
- **No JavaScript errors** in browser console
- **Widget should appear within 3 seconds**

---

## Customization Options

### Change Widget Position
```css
.langchain-widget {
    position: fixed;
    bottom: 20px;    /* Distance from bottom */
    right: 20px;     /* Distance from right */
    left: 20px;      /* Use this instead of right for left side */
    top: 20px;       /* Use this instead of bottom for top */
}
```

### Change Widget Colors
```css
.langchain-widget {
    --primary-color: #007cba;      /* Your brand color */
    --text-color: #333333;         /* Text color */
    --background-color: #ffffff;   /* Background color */
}
```

### Hide on Specific Pages
```javascript
// Don't show on checkout/payment pages
if (window.location.pathname.includes('/checkout') ||
    window.location.pathname.includes('/payment')) {
    window.langchainConfig.disabled = true;
}
```

---

## Common Problems & Solutions

### Widget Doesn't Appear
**Check:**
- ✅ Code is added in the correct location
- ✅ No JavaScript errors in browser console
- ✅ API key is correct
- ✅ Page has finished loading

### Widget Appears But Doesn't Work
**Check:**
- ✅ Internet connection is stable
- ✅ API endpoints are reachable
- ✅ Configuration object is correct
- ✅ No ad blockers interfering

### Widget Breaks Website Design
**Solutions:**
- Adjust CSS positioning
- Change z-index value
- Modify widget size
- Use custom styling

### Slow Page Loading
**Solutions:**
- Load widget script asynchronously
- Delay widget initialization
- Optimize other page elements
- Contact support for performance tips

---

## Mobile Optimization

### Responsive Design Tips
```css
/* Mobile-friendly widget */
@media (max-width: 768px) {
    .langchain-widget {
        bottom: 10px;
        right: 10px;
        width: 80%;
        max-width: 300px;
    }
}
```

### Touch-Friendly Interface
```javascript
window.langchainConfig = {
    apiKey: 'your-api-key-here',
    mobile: {
        touchOptimized: true,
        fullScreenMode: false,
        minimumTouchTarget: '44px'
    }
};
```

---

## Getting Your API Key

### Step 1: Register Account
1. **Go to** your LangChain provider's website
2. **Click "Sign Up"** or "Get Started"
3. **Fill out the registration form**
4. **Verify your email address**

### Step 2: Generate API Key
1. **Log into your dashboard**
2. **Look for "API Keys"** or "Integrations"
3. **Click "Create New Key"**
4. **Name it** "Website Integration"
5. **Copy the key** and keep it secure

### Step 3: Configure Integration
1. **Replace** `'your-api-key-here'` in the code above
2. **Save your changes**
3. **Test the integration**

---

## Security Best Practices

### ✅ DO:
- Keep API keys secure and private
- Use environment variables for sensitive data
- Regularly rotate API keys
- Monitor usage and set limits

### ❌ DON'T:
- Share API keys publicly
- Commit keys to version control
- Use same key across multiple sites
- Ignore security warnings

---

## Need Help?

### Before Contacting Support:
1. **Check browser console** for error messages
2. **Test on different browsers** (Chrome, Firefox, Safari)
3. **Verify all steps** were followed correctly
4. **Try on different devices** (desktop, mobile)

### When Contacting Support:
- Specify your website platform (WordPress, Shopify, etc.)
- Include your website URL
- Describe exactly what you see vs. what you expected
- Share any error messages or screenshots

---

*Looking for other integrations? Check out our EMAIL_SETUP.md and SOCIAL_MEDIA.md guides!*