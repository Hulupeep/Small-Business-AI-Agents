# Social Media Integration Guide 📱

*Connect your social media accounts to LangChain for automated posting and engagement*

## What You'll Need
- Access to your social media accounts
- Administrator permissions (for business accounts)
- 20-40 minutes per platform
- Smartphone for some authentication steps

---

## Facebook Integration

### Step 1: Create Facebook App
1. **Go to** https://developers.facebook.com
2. **Click "Get Started"** (top right)
3. **Choose "Consumer"** or "Business" (Business recommended)
4. **Click "Next"** and complete account setup
5. **Click "Create App"**
6. **Select "Business"** as app type
7. **Fill in app details:**
   - **App Display Name**: "LangChain Integration"
   - **App Contact Email**: Your email
   - **Business Manager Account**: Create new or select existing

### Step 2: Set Up Page Access
1. **In your new app dashboard**, click **"Add Product"**
2. **Find "Facebook Login"** and click **"Set Up"**
3. **Click "Settings"** under Facebook Login
4. **Add these Valid OAuth URIs:**
   ```
   https://your-domain.com/auth/facebook/callback
   https://localhost:3000/auth/facebook/callback
   ```
5. **Click "Save Changes"**

### Step 3: Get Your Tokens
1. **Go to "Tools & Support" → "Graph API Explorer"**
2. **Select your app** from dropdown
3. **Click "Generate Access Token"**
4. **Select permissions:**
   - `pages_read_engagement`
   - `pages_manage_posts`
   - `pages_show_list`
5. **Copy the access token** (starts with EAA...)

### Step 4: Test Your Integration
```javascript
// Test posting to Facebook Page
const facebookPost = {
    message: "Hello from LangChain!",
    access_token: "YOUR_ACCESS_TOKEN",
    page_id: "YOUR_PAGE_ID"
};

fetch(`https://graph.facebook.com/${page_id}/feed`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(facebookPost)
});
```

### Facebook Troubleshooting
**"Invalid OAuth access token"**
- **Solution**: Regenerate token and check expiration

**"Insufficient permissions"**
- **Solution**: Add required permissions in Graph API Explorer

**"App not approved"**
- **Solution**: Submit app for review or use test users

---

## Instagram Business Integration

### Step 1: Connect Instagram to Facebook
1. **Go to** https://business.facebook.com
2. **Select your Business Manager account**
3. **Click "Business Settings"**
4. **Under "Accounts"**, click **"Instagram Accounts"**
5. **Click "Add" → "Connect an Instagram account"**
6. **Log into Instagram** when prompted
7. **Select the account** you want to connect

### Step 2: Get Instagram Business Account ID
1. **Go to Graph API Explorer**
2. **Select your app**
3. **In the query box**, type: `me/accounts`
4. **Click "Submit"**
5. **Find your Instagram account** in the response
6. **Copy the "id"** field

### Step 3: Instagram Posting Code
```javascript
// Post to Instagram Business Account
const instagramPost = {
    image_url: "https://your-domain.com/image.jpg",
    caption: "Posted via LangChain! #automation",
    access_token: "YOUR_ACCESS_TOKEN"
};

// First, create media container
fetch(`https://graph.facebook.com/${instagram_account_id}/media`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(instagramPost)
})
.then(response => response.json())
.then(data => {
    // Then publish the media
    const publishData = {
        creation_id: data.id,
        access_token: "YOUR_ACCESS_TOKEN"
    };

    return fetch(`https://graph.facebook.com/${instagram_account_id}/media_publish`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(publishData)
    });
});
```

### Instagram Troubleshooting
**"Account not found"**
- **Solution**: Ensure Instagram account is connected to Facebook Business

**"Media type not supported"**
- **Solution**: Use JPEG/PNG images or MP4 videos only

---

## LinkedIn Integration

### Step 1: Create LinkedIn App
1. **Go to** https://www.linkedin.com/developers/
2. **Click "Create App"**
3. **Fill in required information:**
   - **App name**: "LangChain Integration"
   - **LinkedIn Page**: Select your company page
   - **Privacy policy URL**: Your website's privacy policy
   - **App logo**: Upload a square image
4. **Check "Sign In with LinkedIn"** and **"Share on LinkedIn"**
5. **Click "Create app"**

### Step 2: Configure App Settings
1. **Go to the "Auth" tab**
2. **Add redirect URLs:**
   ```
   https://your-domain.com/auth/linkedin/callback
   https://localhost:3000/auth/linkedin/callback
   ```
3. **Note down:**
   - **Client ID**
   - **Client Secret**
4. **Under "Default Application Permissions"**, request:
   - `r_liteprofile`
   - `w_member_social`

### Step 3: Get Access Token
```javascript
// OAuth flow for LinkedIn
const linkedinAuth = {
    client_id: "YOUR_CLIENT_ID",
    response_type: "code",
    redirect_uri: "https://your-domain.com/auth/linkedin/callback",
    scope: "r_liteprofile w_member_social"
};

// User visits this URL to authorize
const authUrl = `https://www.linkedin.com/oauth/v2/authorization?${new URLSearchParams(linkedinAuth).toString()}`;
```

### Step 4: Post to LinkedIn
```javascript
// Post to LinkedIn
const linkedinPost = {
    author: "urn:li:person:YOUR_PERSON_ID",
    lifecycleState: "PUBLISHED",
    specificContent: {
        "com.linkedin.ugc.ShareContent": {
            shareCommentary: {
                text: "Sharing insights via LangChain automation!"
            },
            shareMediaCategory: "NONE"
        }
    },
    visibility: {
        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
    }
};

fetch('https://api.linkedin.com/v2/ugcPosts', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${access_token}`,
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    },
    body: JSON.stringify(linkedinPost)
});
```

### LinkedIn Troubleshooting
**"Invalid client credentials"**
- **Solution**: Double-check Client ID and Secret

**"Insufficient permissions"**
- **Solution**: Request additional permissions in app settings

---

## Twitter/X Integration

### Step 1: Apply for Developer Account
1. **Go to** https://developer.twitter.com
2. **Click "Apply for a developer account"**
3. **Choose "Making a bot"** or **"Academic research"**
4. **Fill out the application** (be specific about your use case)
5. **Wait for approval** (can take 1-7 days)

### Step 2: Create Twitter App
1. **Once approved**, go to **"Projects & Apps"**
2. **Click "Create App"**
3. **Name your app**: "LangChain Bot"
4. **Save your API keys:**
   - **API Key**
   - **API Secret Key**
   - **Bearer Token**

### Step 3: Generate Access Tokens
1. **Go to your app settings**
2. **Click "Keys and tokens" tab**
3. **Under "Access Token and Secret"**, click **"Generate"**
4. **Save these tokens:**
   - **Access Token**
   - **Access Token Secret**

### Step 4: Post to Twitter
```javascript
// Using Twitter API v2
const twitterPost = {
    text: "Hello from LangChain! 🤖 #automation #AI"
};

fetch('https://api.twitter.com/2/tweets', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${bearer_token}`,
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(twitterPost)
});
```

### Twitter Troubleshooting
**"Application approval pending"**
- **Solution**: Wait for Twitter's approval, can take up to a week

**"Rate limit exceeded"**
- **Solution**: Reduce posting frequency, Twitter has strict limits

---

## TikTok for Business Integration

### Step 1: Set Up TikTok Business Account
1. **Download TikTok app** on your phone
2. **Create business account** or convert personal account
3. **Go to** https://ads.tiktok.com
4. **Click "Get Started"**
5. **Complete business verification**

### Step 2: Apply for Content Posting API
1. **Go to** https://developers.tiktok.com
2. **Click "Apply for Content Posting API"**
3. **Fill out application** (requires business justification)
4. **Wait for approval** (can take 2-4 weeks)

*Note: TikTok's Content Posting API has limited availability and requires approval*

### TikTok Alternative: Manual Scheduling
```javascript
// Since TikTok API is limited, use scheduling tools
const tiktokSchedule = {
    platform: "tiktok",
    content: {
        video_url: "https://your-domain.com/video.mp4",
        caption: "Amazing content from LangChain! #viral",
        schedule_time: "2024-01-15T10:00:00Z"
    },
    // Use tools like Later, Hootsuite, or Buffer
    scheduling_tool: "buffer"
};
```

---

## Multi-Platform Posting Solution

### Universal Social Media Manager
```javascript
class SocialMediaManager {
    constructor() {
        this.platforms = {
            facebook: { token: 'FB_TOKEN', pageId: 'FB_PAGE_ID' },
            instagram: { token: 'IG_TOKEN', accountId: 'IG_ACCOUNT_ID' },
            linkedin: { token: 'LI_TOKEN', personId: 'LI_PERSON_ID' },
            twitter: { bearerToken: 'TWITTER_BEARER_TOKEN' }
        };
    }

    async postToAll(content) {
        const results = await Promise.allSettled([
            this.postToFacebook(content),
            this.postToInstagram(content),
            this.postToLinkedIn(content),
            this.postToTwitter(content)
        ]);

        return results.map((result, index) => ({
            platform: Object.keys(this.platforms)[index],
            success: result.status === 'fulfilled',
            error: result.reason || null
        }));
    }

    async postToFacebook(content) {
        const response = await fetch(`https://graph.facebook.com/${this.platforms.facebook.pageId}/feed`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: content.text,
                access_token: this.platforms.facebook.token
            })
        });
        return response.json();
    }

    // Similar methods for other platforms...
}

// Usage
const socialManager = new SocialMediaManager();
socialManager.postToAll({
    text: "Check out our latest feature!",
    image: "https://example.com/image.jpg",
    hashtags: ["#AI", "#automation", "#tech"]
});
```

---

## Content Planning & Automation

### Content Calendar Template
```javascript
const contentCalendar = {
    "2024-01-15": {
        platforms: ["facebook", "linkedin"],
        content: {
            text: "Monday motivation: AI is transforming business!",
            image: "motivational-monday.jpg",
            hashtags: ["#MondayMotivation", "#AI"]
        },
        scheduled_time: "09:00"
    },
    "2024-01-16": {
        platforms: ["twitter", "instagram"],
        content: {
            text: "Tech tip Tuesday: Automate your social media!",
            image: "tech-tip.jpg",
            hashtags: ["#TechTip", "#Automation"]
        },
        scheduled_time: "14:00"
    }
};
```

### Automated Posting Schedule
```javascript
class ContentScheduler {
    constructor(socialManager) {
        this.socialManager = socialManager;
        this.schedule = contentCalendar;
    }

    startScheduler() {
        setInterval(() => {
            this.checkAndPost();
        }, 60000); // Check every minute
    }

    checkAndPost() {
        const now = new Date();
        const today = now.toISOString().split('T')[0];
        const currentTime = now.toTimeString().slice(0, 5);

        const todayContent = this.schedule[today];
        if (todayContent && todayContent.scheduled_time === currentTime) {
            this.socialManager.postToSelected(
                todayContent.platforms,
                todayContent.content
            );
        }
    }
}
```

---

## Analytics & Monitoring

### Track Post Performance
```javascript
async function getPostAnalytics(platform, postId) {
    switch(platform) {
        case 'facebook':
            const fbResponse = await fetch(`https://graph.facebook.com/${postId}/insights?metric=post_impressions,post_engaged_users&access_token=${FB_TOKEN}`);
            return fbResponse.json();

        case 'twitter':
            const twitterResponse = await fetch(`https://api.twitter.com/2/tweets/${postId}?tweet.fields=public_metrics`, {
                headers: { 'Authorization': `Bearer ${TWITTER_BEARER_TOKEN}` }
            });
            return twitterResponse.json();

        case 'linkedin':
            const linkedinResponse = await fetch(`https://api.linkedin.com/v2/socialActions/${postId}/statistics`, {
                headers: { 'Authorization': `Bearer ${LINKEDIN_TOKEN}` }
            });
            return linkedinResponse.json();
    }
}
```

### Engagement Report
```javascript
async function generateEngagementReport() {
    const platforms = ['facebook', 'twitter', 'linkedin', 'instagram'];
    const report = {};

    for (const platform of platforms) {
        try {
            const metrics = await getPostAnalytics(platform, 'latest_post_id');
            report[platform] = {
                impressions: metrics.impressions || 0,
                engagements: metrics.engagements || 0,
                engagement_rate: ((metrics.engagements / metrics.impressions) * 100).toFixed(2) + '%'
            };
        } catch (error) {
            report[platform] = { error: error.message };
        }
    }

    return report;
}
```

---

## Common Problems & Solutions

### API Rate Limits
**Problem**: "Rate limit exceeded"
**Solutions:**
- Space out posts (at least 1 hour apart)
- Use scheduling tools that respect limits
- Monitor usage with analytics
- Consider upgrading to business/premium plans

### Authentication Errors
**Problem**: "Token expired" or "Invalid credentials"
**Solutions:**
- Refresh access tokens regularly
- Store tokens securely
- Implement token refresh logic
- Check app permissions

### Content Policy Violations
**Problem**: Posts get rejected or removed
**Solutions:**
- Review each platform's content policies
- Avoid spam-like behavior
- Use original content and images
- Test posts manually first

### Image Upload Issues
**Problem**: Images fail to upload
**Solutions:**
- Use correct image formats (JPEG, PNG)
- Check file size limits
- Ensure images are publicly accessible
- Optimize images for web

---

## Best Practices

### ✅ DO:
- Post consistently but not too frequently
- Customize content for each platform
- Monitor engagement and adjust strategy
- Respect platform-specific content guidelines
- Use high-quality images and videos

### ❌ DON'T:
- Post identical content across all platforms
- Ignore platform-specific best practices
- Spam followers with too many posts
- Use copyrighted content without permission
- Forget to monitor for responses and engagement

---

## Security & Compliance

### Protect Your API Keys
```javascript
// Use environment variables
const config = {
    facebook: {
        token: process.env.FACEBOOK_ACCESS_TOKEN,
        pageId: process.env.FACEBOOK_PAGE_ID
    },
    twitter: {
        bearerToken: process.env.TWITTER_BEARER_TOKEN
    }
};

// Never hardcode in source code
// ❌ const token = "EAA123abc456def...";
// ✅ const token = process.env.FACEBOOK_ACCESS_TOKEN;
```

### Regular Security Audits
1. **Review app permissions** monthly
2. **Rotate API keys** quarterly
3. **Monitor unusual activity** daily
4. **Keep access logs** for compliance

---

## Getting Help

### Before Contacting Support:
1. **Check platform status pages** for outages
2. **Verify API credentials** are correct and active
3. **Test with simple posts** first
4. **Review error messages** carefully

### Platform-Specific Support:
- **Facebook**: https://developers.facebook.com/support/
- **Instagram**: Use Facebook Business Support
- **LinkedIn**: https://www.linkedin.com/help/linkedin/
- **Twitter**: https://developer.twitter.com/en/support

---

*Ready to connect more platforms? Check out our MESSAGING.md guide for WhatsApp and SMS integration!*