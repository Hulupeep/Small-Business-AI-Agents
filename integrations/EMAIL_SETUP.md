# Email Integration Setup Guide 📧

*A step-by-step guide for complete beginners*

## What You'll Need Before Starting
- Your email account login details
- 15-30 minutes of time
- A computer or smartphone

---

## Gmail Setup (Most Popular)

### Step 1: Enable App Passwords
1. **Open Gmail** in your web browser
2. **Click your profile picture** (top right corner - it's a circle with your photo or initials)
3. **Click "Manage your Google Account"**
4. **Look for "Security"** on the left side menu and click it
5. **Scroll down** until you see "2-Step Verification"
6. **Click "2-Step Verification"** (if it says "Off", you'll need to turn it on first)
7. **Scroll down** to find "App passwords"
8. **Click "App passwords"**
9. **Select "Mail"** from the dropdown
10. **Select "Other"** and type "LangChain Integration"
11. **Click "Generate"**
12. **Copy the 16-character password** that appears (it looks like: abcd efgh ijkl mnop)

### Step 2: Get Your Integration Settings
```
SMTP Server: smtp.gmail.com
Port: 587
Security: TLS/STARTTLS
Username: your-email@gmail.com
Password: [the 16-character password from Step 1]
```

### Step 3: Test Your Connection
1. **Save these settings** in your integration tool
2. **Send a test email** to yourself
3. **Check your inbox** - you should receive the test email within 1-2 minutes

**🚨 Troubleshooting Gmail:**
- **"Authentication failed"**: Double-check your app password
- **"Connection refused"**: Make sure 2-Step Verification is enabled
- **"Less secure apps"**: Use app passwords instead

---

## Outlook/Hotmail Setup

### Step 1: Enable App Passwords
1. **Go to** https://account.microsoft.com
2. **Sign in** with your Outlook/Hotmail email
3. **Click "Security"** at the top
4. **Click "Advanced security options"**
5. **Under "App passwords"**, click **"Create a new app password"**
6. **Name it** "LangChain Integration"
7. **Copy the password** that appears

### Step 2: Get Your Integration Settings
```
SMTP Server: smtp-mail.outlook.com
Port: 587
Security: TLS/STARTTLS
Username: your-email@outlook.com (or @hotmail.com)
Password: [the app password from Step 1]
```

### Step 3: Test Your Connection
Follow the same testing steps as Gmail above.

**🚨 Troubleshooting Outlook:**
- **"SMTP AUTH disabled"**: Enable SMTP AUTH in your account settings
- **"Authentication failed"**: Verify your app password is correct

---

## Yahoo Mail Setup

### Step 1: Generate App Password
1. **Go to** https://login.yahoo.com
2. **Sign in** to your Yahoo account
3. **Click your name** (top right corner)
4. **Click "Account Info"**
5. **Click "Account Security"** on the left
6. **Scroll down** to "Generate app password"
7. **Select "Other app"** and type "LangChain"
8. **Click "Generate"**
9. **Copy the password** shown

### Step 2: Get Your Integration Settings
```
SMTP Server: smtp.mail.yahoo.com
Port: 587 or 465
Security: TLS/STARTTLS (for 587) or SSL (for 465)
Username: your-email@yahoo.com
Password: [the app password from Step 1]
```

**🚨 Troubleshooting Yahoo:**
- **"Invalid credentials"**: Make sure you're using the app password, not your regular password
- **"Connection timeout"**: Try port 465 with SSL instead of 587

---

## Common Integration Code

### For Developers - Python Example
```python
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

def send_email(smtp_server, port, username, password, to_email, subject, body):
    # Create message
    msg = MimeMultipart()
    msg['From'] = username
    msg['To'] = to_email
    msg['Subject'] = subject

    # Add body to email
    msg.attach(MimeText(body, 'plain'))

    # Create SMTP session
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()  # Enable TLS encryption
    server.login(username, password)

    # Send email
    text = msg.as_string()
    server.sendmail(username, to_email, text)
    server.quit()

# Example usage
send_email(
    smtp_server="smtp.gmail.com",
    port=587,
    username="your-email@gmail.com",
    password="your-app-password",
    to_email="recipient@example.com",
    subject="Test from LangChain",
    body="This is a test email!"
)
```

### For No-Code Tools (Zapier, Make.com, etc.)
**Copy these exact settings:**
- **Server**: smtp.gmail.com (or appropriate server from above)
- **Port**: 587
- **Username**: your full email address
- **Password**: your app password (NOT your regular password)
- **Authentication**: Login/Plain
- **Encryption**: TLS/STARTTLS

---

## Testing Your Setup

### Quick Test Checklist
1. ✅ **Send test email to yourself**
2. ✅ **Check spam folder** if email doesn't arrive
3. ✅ **Verify sender name** appears correctly
4. ✅ **Test with different email addresses**
5. ✅ **Check delivery time** (should be under 30 seconds)

### What Success Looks Like
- Email arrives in inbox within 30 seconds
- Sender shows your correct email address
- No error messages in your integration tool
- Email formatting looks correct

---

## Security Best Practices

### ✅ DO:
- Use app passwords (never your main password)
- Keep app passwords secure and private
- Delete unused app passwords regularly
- Enable 2-factor authentication

### ❌ DON'T:
- Share your app passwords with anyone
- Use your main email password for integrations
- Store passwords in plain text files
- Disable security features to "make it easier"

---

## Common Error Messages & Solutions

### "Authentication Failed"
**Solution**: Double-check your app password and username

### "Connection Timeout"
**Solution**: Check your internet connection and try a different port

### "SSL/TLS Error"
**Solution**: Verify you're using the correct encryption method (TLS for port 587)

### "Relay Access Denied"
**Solution**: Make sure you're authenticating with your username and password

### "Daily Sending Limit Exceeded"
**Solution**: Wait 24 hours or upgrade to a business email plan

---

## Getting Help

### Before Contacting Support:
1. ✅ **Double-check all settings** against this guide
2. ✅ **Test with a simple email first**
3. ✅ **Check your email provider's status page**
4. ✅ **Try the setup on a different device**

### When Contacting Support:
- Mention you're setting up email integration
- Share the exact error message (screenshot is helpful)
- Specify which email provider you're using
- Confirm you followed this guide step-by-step

---

*Need help with other integrations? Check out our other guides in this folder!*