# AI Agent ROI Calculator & Tracking System

## Quick ROI Overview

**Average ROI for Small Businesses: 300-800% within 90 days**

- **FAQ Bot**: 400-600% ROI (deflects 60-80% of repetitive calls)
- **Booking Bot**: 500-900% ROI (captures 24/7 bookings + reduces no-shows)
- **Lead Bot**: 300-700% ROI (qualifies leads + increases conversion)
- **Support Bot**: 400-800% ROI (handles routine requests instantly)

---

## 1. Simple Spreadsheet Template (Google Sheets)

### Copy this structure into Google Sheets:

```
A1: AI Agent ROI Calculator
A3: Business Information
A4: Business Type:
A5: Current Hourly Rate (€):
A6: Hours Worked/Week:
A7: Agent Type:
A8: Monthly Agent Cost (€):

A10: Time Savings Analysis
A11: Task/Activity | Hours/Week Before | Hours/Week After | Time Saved | Value Saved (€)
A12: Customer Calls | [Your number] | [Reduced number] | =B12-C12 | =D12*$B$5
A13: Appointment Booking | [Your number] | [Reduced number] | =B13-C13 | =D13*$B$5
A14: Lead Qualification | [Your number] | [Reduced number] | =B14-C14 | =D14*$B$5
A15: Customer Support | [Your number] | [Reduced number] | =B15-C15 | =D15*$B$5
A16: TOTAL SAVINGS: | | | =SUM(D12:D15) | =SUM(E12:E15)

A18: Additional Revenue
A19: Extra Bookings/Week: | [Number] | | | =B19*[avg booking value]*4
A20: Leads Converted: | [Number] | | | =B20*[avg deal value]
A21: After-Hours Captures: | [Number] | | | =B21*[avg job value]
A22: TOTAL EXTRA REVENUE: | | | | =SUM(E19:E21)

A24: Monthly ROI Calculation
A25: Total Monthly Savings: | =E16*4
A26: Total Monthly Extra Revenue: | =E22
A27: Total Monthly Benefit: | =B25+B26
A28: Monthly Agent Cost: | =$B$8
A29: Net Monthly Benefit: | =B27-B28
A30: ROI Percentage: | =(B29/B28)*100
A31: Break-Even Days: | =(B28/B27)*30
```

### Formulas for Quick Copy-Paste:

- **Time Saved**: `=B12-C12` (Hours before minus hours after)
- **Value Saved**: `=D12*$B$5` (Time saved × hourly rate)
- **Total Monthly Benefit**: `=(SUM(E12:E15)*4)+(SUM(E19:E21))`
- **ROI Percentage**: `=((Total Benefit - Agent Cost)/Agent Cost)*100`
- **Break-Even Days**: `=(Agent Cost/Daily Benefit)*30`

---

## 2. Agent-Specific ROI Formulas

### FAQ Bot ROI Formula
```
Monthly ROI = (Calls Deflected × Avg Call Time × Hourly Rate × 4) - Bot Cost

Example:
- Calls deflected: 50/week
- Avg call time: 8 minutes (0.13 hours)
- Hourly rate: €25
- Bot cost: €45/month

ROI = (50 × 0.13 × €25 × 4) - €45 = €650 - €45 = €605 (1,344% ROI)
```

### Booking Bot ROI Formula
```
Monthly ROI = (Bookings × Time per Booking × Rate × 4) +
              (Missed Calls Captured × Avg Job Value × 0.3) - Bot Cost

Example:
- Bookings saved time: 20/week × 10 minutes × €30/hour
- Missed calls captured: 5/week × €80 job × 30% conversion
- Bot cost: €55/month

ROI = (20 × 0.17 × €30 × 4) + (5 × €80 × 0.3 × 4) - €55 = €408 + €480 - €55 = €833 (1,515% ROI)
```

### Lead Bot ROI Formula
```
Monthly ROI = (Leads Qualified × Qualification Time × Rate × 4) +
              (Conversion Rate Increase × Avg Deal × Leads/Month) - Bot Cost

Example:
- Leads qualified: 15/week × 20 minutes × €40/hour
- Conversion increase: 15% × €200 avg deal × 60 leads/month
- Bot cost: €75/month

ROI = (15 × 0.33 × €40 × 4) + (0.15 × €200 × 60) - €75 = €792 + €1,800 - €75 = €2,517 (3,356% ROI)
```

### Support Bot ROI Formula
```
Monthly ROI = (Tickets Handled × Handling Time × Rate × 4) -
              (Escalations × Extra Time × Rate × 4) - Bot Cost

Example:
- Tickets handled: 80/week × 15 minutes × €25/hour
- Escalations: 5/week × 30 minutes × €25/hour
- Bot cost: €65/month

ROI = (80 × 0.25 × €25 × 4) - (5 × 0.5 × €25 × 4) - €65 = €2,000 - €250 - €65 = €1,685 (2,592% ROI)
```

---

## 3. Quick Calculators (Plug In Your Numbers)

### Restaurant Takeout Bot Calculator
```
Your Current Situation:
- Phone orders taken/week: [____]
- Minutes per order: [____]
- Your hourly rate: €[____]
- Missed calls/week (busy periods): [____]
- Average order value: €[____]

Quick ROI:
Time Saved = [orders] × [minutes] ÷ 60 × €[rate] × 4 weeks
Lost Revenue Captured = [missed calls] × €[order value] × 0.4 × 4 weeks
Monthly Benefit = Time Saved + Lost Revenue - €45 bot cost

Example: 100 orders × 8 minutes × €20/hour + 20 missed × €25 × 0.4 - €45 = €1,022 ROI
```

### Hair Salon Booking Bot Calculator
```
Your Current Situation:
- Appointment calls/week: [____]
- Minutes per booking call: [____]
- Your hourly rate: €[____]
- After-hours calls missed: [____]
- Average service value: €[____]
- No-show rate without reminders: [____%]

Quick ROI:
Booking Time Saved = [calls] × [minutes] ÷ 60 × €[rate] × 4
After-Hours Captures = [missed] × €[service] × 0.3 × 4
No-Show Reduction = [bookings] × ([old rate] - 5%) × €[service]
Monthly Benefit = All savings - €55 bot cost

Example: 60 calls × 12 minutes × €35/hour + 8 missed × €45 × 0.3 + no-show savings - €55 = €1,156 ROI
```

### Plumber After-Hours Bot Calculator
```
Your Current Situation:
- After-hours calls/week: [____]
- Emergency call conversion rate: [____%]
- Average emergency job value: €[____]
- Weekend/evening rate premium: €[____]/hour
- Time spent on initial assessment: [____] minutes

Quick ROI:
Lost Revenue Captured = [calls] × [conversion%] × €[job value] × 4
Assessment Time Saved = [calls] × [minutes] ÷ 60 × €[premium rate] × 4
Monthly Benefit = Revenue + Time - €65 bot cost

Example: 15 calls × 40% × €180 + 15 × 10 minutes × €50/hour - €65 = €1,435 ROI
```

### Retail Customer Service Bot Calculator
```
Your Current Situation:
- Customer service inquiries/week: [____]
- Minutes per inquiry: [____]
- Staff hourly cost: €[____]
- % of inquiries that are routine: [____%]
- Inquiries leading to sales: [____%]
- Average sale value: €[____]

Quick ROI:
Staff Time Saved = [inquiries] × [routine%] × [minutes] ÷ 60 × €[hourly cost] × 4
Sales Opportunities = [inquiries] × [sales%] × €[sale value] × 0.2 improvement × 4
Monthly Benefit = Savings + Sales - €70 bot cost

Example: 200 inquiries × 70% × 8 minutes × €18/hour + sales uplift - €70 = €1,285 ROI
```

---

## 4. Tracking Metrics

### Daily Metrics to Track

**For All Bots:**
- Number of interactions
- Resolution rate
- Escalations to human
- User satisfaction (if measured)

**Bot-Specific Metrics:**

**FAQ Bot:**
- Questions answered
- Deflection rate
- Top unresolved queries

**Booking Bot:**
- Appointments scheduled
- Conversion rate (inquiry to booking)
- No-show rate comparison

**Lead Bot:**
- Leads captured
- Qualification score
- Follow-up scheduling rate

**Support Bot:**
- Tickets resolved
- Average resolution time
- Customer satisfaction

### Weekly Review Template

```
Week of: [Date]

Bot Performance:
- Total interactions: [____]
- Successful resolutions: [____]
- Success rate: [____%]
- Time saved (hours): [____]

Business Impact:
- Revenue generated/saved: €[____]
- New appointments/leads: [____]
- Customer feedback score: [____]

Areas for Improvement:
- [ ] Update FAQ responses for: [____]
- [ ] Adjust booking flow for: [____]
- [ ] Add training for: [____]

Next Week Goals:
- Target interactions: [____]
- Success rate goal: [____%]
- Focus area: [____]
```

### Monthly Reporting Format

```
Month: [Month Year]

ROI Summary:
- Total Investment: €[____]
- Time Saved Value: €[____]
- Revenue Generated: €[____]
- Net Benefit: €[____]
- ROI Percentage: [____%]

Key Metrics:
- Total Interactions: [____]
- Average Daily Interactions: [____]
- Success Rate: [____%]
- Customer Satisfaction: [____/10]

Business Outcomes:
- Hours Saved: [____]
- New Customers: [____]
- Retained Customers: [____]
- Missed Opportunities Captured: [____]

Improvements Made:
- [ ] Updated responses: [____]
- [ ] Added new flows: [____]
- [ ] Integration improvements: [____]

Next Month Focus:
- [ ] Priority 1: [____]
- [ ] Priority 2: [____]
- [ ] Priority 3: [____]
```

---

## 5. Break-Even Analysis

### Days to Break Even by Agent Type

**FAQ Bot (€45/month):**
- High-volume business (100+ calls/week): 3-7 days
- Medium business (50-99 calls/week): 7-14 days
- Small business (20-49 calls/week): 14-30 days

**Booking Bot (€55/month):**
- Service business (30+ bookings/week): 2-5 days
- Appointment-based (15-29 bookings/week): 5-12 days
- Occasional bookings (5-14 bookings/week): 15-30 days

**Lead Bot (€75/month):**
- High-ticket services (€500+ avg deal): 1-3 days
- Medium deals (€100-499): 5-15 days
- Small deals (€50-99): 20-45 days

**Support Bot (€65/month):**
- E-commerce/SaaS (50+ tickets/week): 2-6 days
- Service business (20-49 tickets/week): 8-18 days
- Small operation (5-19 tickets/week): 20-40 days

### Investment Recovery Timeline

**Month 1:** Setup and optimization
- 50-80% of full potential ROI
- Learning and adjustment period
- Break-even typically achieved

**Month 2-3:** Full efficiency
- 100%+ of projected ROI
- Optimized workflows
- Full recovery of investment

**Month 4+:** Scaling benefits
- Additional features and integrations
- Compound time savings
- Maximum ROI realization

### Scale-Up Decision Framework

**When to Add Another Bot:**
- Current bot ROI > 300%
- Time savings reinvested productively
- New pain points identified
- Customer feedback indicates needs

**When to Upgrade Bot Features:**
- Basic ROI > 200%
- Identified specific improvement areas
- Integration opportunities available
- Competition requires advancement

**When to Expand to Multiple Channels:**
- Single channel ROI > 400%
- Customer preference data supports it
- Resources available for management
- Clear additional value proposition

---

## 6. Real Examples & Case Studies

### Local Bakery Case Study
**Investment:** €50/month FAQ + Ordering Bot

**Before:**
- 80 phone orders/week × 12 minutes = 16 hours
- 20 missed calls during rush hours
- Owner's time: €25/hour

**After:**
- 85% of orders automated (68 orders)
- Time saved: 13.6 hours/week
- Missed calls captured: 16/week

**Monthly ROI:**
- Time saved: 13.6 × €25 × 4 = €1,360
- Revenue from captured calls: 16 × €18 × 0.4 × 4 = €461
- Total benefit: €1,821
- Net ROI: €1,821 - €50 = €1,771 (3,542% ROI)

**Break-even:** 3 days

### Dental Clinic Case Study
**Investment:** €75/month Booking + FAQ Bot

**Before:**
- 45 booking calls/week × 15 minutes = 11.25 hours
- Receptionist cost: €20/hour
- 12 after-hours missed calls/week
- Average appointment value: €85

**After:**
- 70% booking automation
- 90% FAQ deflection for 60 calls/week

**Monthly ROI:**
- Receptionist time saved: (31.5 + 7.5) × €20 × 4 = €3,120
- After-hours captures: 12 × €85 × 0.25 × 4 = €1,020
- Total benefit: €4,140
- Net ROI: €4,140 - €75 = €4,065 (5,420% ROI)

**Break-even:** 2 days

### IT Consultant Case Study
**Investment:** €100/month Lead Qualification Bot

**Before:**
- 25 leads/week × 30 minutes qualification = 12.5 hours
- Consultant rate: €75/hour
- Conversion rate: 12%
- Average project: €2,500

**After:**
- 80% of initial qualification automated
- Improved lead quality increased conversion to 18%
- Time saved for billable work

**Monthly ROI:**
- Time saved for billing: 10 × €75 × 4 = €3,000
- Improved conversion: 6% × 100 leads × €2,500 × 0.18 = €2,700
- Total benefit: €5,700
- Net ROI: €5,700 - €100 = €5,600 (5,600% ROI)

**Break-even:** 1.5 days

### Restaurant Chain Case Study (3 locations)
**Investment:** €150/month (€50 per location) Ordering + Support Bot

**Before per location:**
- 120 phone orders/week × 8 minutes = 16 hours
- Staff cost: €15/hour
- 25 support calls/week × 12 minutes = 5 hours

**After per location:**
- 90% order automation
- 75% support deflection

**Monthly ROI per location:**
- Order time saved: 14.4 × €15 × 4 = €864
- Support time saved: 3.75 × €15 × 4 = €225
- Total per location: €1,089
- All locations: €3,267
- Net ROI: €3,267 - €150 = €3,117 (2,078% ROI)

**Break-even:** 4 days

---

## ROI Optimization Tips

### Maximize Your Returns:

1. **Comprehensive Training:** Upload all your FAQs, processes, and common scenarios
2. **Integration Setup:** Connect to your existing systems (calendar, CRM, POS)
3. **Regular Updates:** Review and improve bot responses monthly
4. **Performance Monitoring:** Track metrics and optimize based on data
5. **Staff Training:** Ensure team knows how to work with the bot effectively

### Common ROI Killers to Avoid:

- **Incomplete Setup:** Rushing implementation without proper training
- **No Integration:** Making customers switch between systems
- **Poor Maintenance:** Not updating responses or fixing issues
- **Over-Escalation:** Not trusting the bot to handle routine tasks
- **Under-Promotion:** Not telling customers about the new service options

### Scale-Up Strategy:

1. **Start with highest-impact bot** (usually FAQ or Booking)
2. **Achieve 300%+ ROI** before adding complexity
3. **Add complementary bots** that work together
4. **Expand to multiple channels** (web, WhatsApp, social media)
5. **Integrate with business systems** for maximum efficiency

---

**Remember:** These are conservative estimates. Most businesses see higher returns once fully optimized. Start with one bot, measure results, then scale based on proven ROI.