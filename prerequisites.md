# 📋 Prerequisites - Your 5-Minute Setup Guide

## 🎯 Quick Decision Tree

**"I have zero technical experience"** → Use **Claude** (easiest)
**"I want to code occasionally"** → Use **Cursor** (best balance)
**"I'm technical and want free"** → Use **Gemini** (most flexible)

---

## 🚀 Option 1: Claude (Easiest - No Coding)

### What You Get
- ✅ **Best for beginners** - Zero technical knowledge required
- ✅ **Natural conversation** - Just describe what you want
- ✅ **Instant deployment** - Works immediately
- ✅ **No installation** - Works in your browser

### Setup (3 minutes)
1. **Go to:** [claude.ai](https://claude.ai)
2. **Sign up:** Free tier or $20/month Pro
3. **Start:** Copy any agent prompt, paste, chat!

### How to Use Our Agents
```
1. Open Claude
2. Copy the agent prompt from any toolkit
3. Replace [YOUR BUSINESS] with your info
4. Start chatting - it works immediately!
```

### Example
```
You: "A customer asks about our return policy"
Claude: "I'd be happy to help! Our return policy allows..."
```

**Best For:** Customer service, email responses, content creation
**Limitations:** Can't directly integrate with your systems (copy-paste required)

---

## 💻 Option 2: Cursor (Best Balance)

### What You Get
- ✅ **Visual code editor** - See and edit agent code
- ✅ **AI assistance** - Helps you customize
- ✅ **Direct integration** - Connects to your systems
- ✅ **Test locally** - Try before deploying

### Setup (5 minutes)
1. **Download:** [cursor.sh](https://cursor.sh) (Free)
2. **Install:** Run the installer
3. **Open:** Create new project
4. **AI Setup:** Settings → Add Claude API key

### How to Use Our Agents
```
1. Open Cursor
2. File → Open Folder → Select this repository
3. Open any agent file in src/agents/
4. Press Cmd+K (Mac) or Ctrl+K (Windows)
5. Ask: "Run this agent with my business data"
```

### Your First Test
```python
# In Cursor, open: src/agents/customer_service_agent.py
# Press Cmd+K and type: "Test this with a sample question"
# Cursor will run it and show results!
```

**Best For:** All agents, especially those needing system integration
**Bonus:** Can modify and deploy agents permanently

---

## 🔧 Option 3: Gemini (Most Powerful - Free)

### What You Get
- ✅ **Completely free** - No subscription needed
- ✅ **Google integration** - Works with Google Workspace
- ✅ **Advanced features** - Code execution, web search
- ✅ **Scalable** - Handle unlimited requests

### Setup (5 minutes)
1. **Go to:** [ai.google.dev](https://ai.google.dev)
2. **Get API Key:** Click "Get API Key" (free)
3. **Google AI Studio:** [aistudio.google.com](https://aistudio.google.com)
4. **Test:** Paste any agent prompt

### How to Use Our Agents
```
1. Open Google AI Studio
2. New Chat → System Instructions
3. Paste the agent prompt
4. Add your API key to code samples
5. Run and test immediately
```

### Integration Example
```python
# Add to any Python script:
import google.generativeai as genai
genai.configure(api_key="YOUR_KEY")

# Now use any of our agents!
```

**Best For:** Developers, high-volume usage, Google Workspace users
**Note:** Requires basic Python knowledge for full features

---

## 📱 Quick Comparison Table

| Feature | Claude | Cursor | Gemini |
|---------|---------|---------|---------||
| **No Code Required** | ✅ Yes | ⚠️ Optional | ❌ Some needed |
| **Free Tier** | ✅ Limited | ✅ Yes | ✅ Unlimited |
| **Setup Time** | 3 min | 5 min | 5 min |
| **Direct Integration** | ❌ Copy-paste | ✅ Yes | ✅ Yes |
| **Best For Beginners** | ✅✅✅ | ✅✅ | ✅ |
| **Can Customize Agents** | ❌ No | ✅ Yes | ✅ Yes |
| **Monthly Cost** | $0-20 | $0-20 | $0 |

---

## 🎯 Which Agents Work With Each Tool?

### Claude (Chat Interface)
✅ **Perfect for:**
- Customer Service Agent
- Email Responder
- FAQ Assistant
- Social Media Manager
- Lead Qualifier

⚠️ **Needs copy-paste for:**
- Inventory Manager
- Report Generator
- Invoice Processor

### Cursor (Full Integration)
✅ **All agents work perfectly**
- Direct database connection
- API integrations
- Automated workflows
- Real-time processing

### Gemini (Developer Friendly)
✅ **All agents work with setup**
- Requires API configuration
- Best for batch processing
- Great for Google Workspace

---

## 🚨 Common Setup Issues (And Instant Fixes)

### "I can't sign up for Claude"
**Fix:** Use a different email or try Cursor/Gemini instead

### "API Key not working"
**Fix:**
```
1. Check for spaces before/after the key
2. Make sure you copied the entire key
3. Wait 2 minutes (keys take time to activate)
```

### "Agent not responding correctly"
**Fix:**
```
1. Make sure you replaced ALL [EDIT THIS] sections
2. Include your actual business information
3. Test with simple questions first
```

### "Integration not working"
**Fix:**
```
1. Check your .env file has all keys
2. Run: pip install -r requirements.txt
3. Restart the application
```

---

## ✅ Pre-Flight Checklist

Before using any agent, have ready:

**Business Information:**
- [ ] Business name and type
- [ ] Products/services you offer
- [ ] Common customer questions
- [ ] Your website URL

**For Integrations (Optional):**
- [ ] Email account credentials (for Email Responder)
- [ ] Social media API keys (for Social Manager)
- [ ] Calendar access (for Appointment Scheduler)
- [ ] Payment processor API (for Order Processing)

**Quick Test Data:**
- [ ] 5 sample customer questions
- [ ] 3 sample products with prices
- [ ] Your business hours
- [ ] Return/refund policy

---

## 🏃 Your Next Step

**Absolute Beginner?**
1. Sign up for [Claude](https://claude.ai) (3 min)
2. Go to [Customer Service Toolkit](toolkits/customer-service/)
3. Copy the prompt, paste in Claude
4. Replace [YOUR BUSINESS] with your info
5. Save $2,000/month starting today!

**Want Full Power?**
1. Download [Cursor](https://cursor.sh) (5 min)
2. Open this repository
3. Follow any 10-minute quickstart
4. Deploy all 10 agents this week!

---

## 🆘 Need Help?

**Can't decide?** → Start with Claude (you can switch later)
**Stuck on setup?** → Each toolkit has troubleshooting
**Want personal help?** → Check our [video guides](make-your-own-agents/videos/)

---

## 💡 Pro Tips

1. **Start with ONE agent** - Don't try all 10 at once
2. **Customer Service first** - Easiest and biggest impact
3. **Test with real scenarios** - Use actual customer questions
4. **Keep the free tier** - It's enough for most small businesses
5. **Upgrade when you grow** - Not before you need it

---

## ⏰ Time Investment Reality Check

**Today (10 minutes):**
- 5 min: Sign up for your chosen tool
- 5 min: Deploy your first agent
- Result: Start saving immediately

**This Week (2 hours total):**
- Deploy 3-4 key agents
- Save 20+ hours/week

**This Month:**
- All 10 agents running
- Save $15,000+/month
- Focus on growing your business

---

**Remember:** The best tool is the one you'll actually use. Start simple, upgrade later.

**Ready?** [Choose your first agent →](toolkits/)