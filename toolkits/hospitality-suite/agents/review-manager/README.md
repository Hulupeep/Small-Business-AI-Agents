# ⭐ Review & Reputation Manager

**Your Online Reputation Guardian - Proactive Review Management & Brand Protection**

## 🎯 What This Agent Does

The Review & Reputation Manager monitors, manages, and optimizes your online reputation across all platforms, turning happy guests into glowing reviews while preventing negative experiences from becoming public complaints.

### Key Features

#### 🔍 Multi-Platform Monitoring
- **Real-time review alerts** from Booking.com, Airbnb, Google, TripAdvisor
- **Social media mention tracking** across Facebook, Instagram, Twitter
- **Review sentiment analysis** for immediate issue identification
- **Competitor benchmarking** and performance comparison
- **Industry trend monitoring** for reputation insights

#### 🚀 Proactive Issue Resolution
- **Guest satisfaction surveys** sent post-checkout
- **Issue identification** before they become negative reviews
- **Automated follow-up** for unresolved concerns
- **Service recovery** protocols for dissatisfied guests
- **Escalation procedures** for serious complaints

#### 📝 Intelligent Response Management
- **AI-powered response drafting** for all review types
- **Brand voice consistency** across all platforms
- **Multi-language support** for international guests
- **Response timing optimization** for maximum impact
- **Template library** for common scenarios

#### 📊 Reputation Analytics
- **Review score trending** and performance metrics
- **Competitor analysis** and market positioning
- **Guest feedback categorization** for improvement insights
- **Revenue impact analysis** of reputation changes
- **Action item prioritization** based on feedback patterns

## 💰 Financial Impact

### Annual Value: €5,000

**Revenue Protection:**
- Prevent 3 negative reviews annually (€1,000 booking loss each): €3,000
- Improve average rating by 0.2 points (5% booking increase): €1,500
- Faster issue resolution reduces compensation costs: €500

**Operational Benefits:**
- Reduced time managing reviews and complaints
- Improved staff morale through positive feedback focus
- Enhanced marketing assets from positive reviews
- Better understanding of guest needs and preferences

## 🚀 Quick Start

### 1. Installation
```bash
cd agents/review-manager
npm install
```

### 2. Configuration
```yaml
# config/review-settings.yml
property:
  name: "Fitzgerald's Guesthouse"
  brand_voice: "warm, personal, authentic"
  response_time_target: 4 # hours

platforms:
  booking_com:
    enabled: true
    api_key: "${BOOKING_COM_API_KEY}"
    property_id: "${BOOKING_COM_PROPERTY_ID}"

  airbnb:
    enabled: true
    api_key: "${AIRBNB_API_KEY}"
    listing_id: "${AIRBNB_LISTING_ID}"

  google_my_business:
    enabled: true
    api_key: "${GOOGLE_API_KEY}"
    location_id: "${GOOGLE_LOCATION_ID}"

  tripadvisor:
    enabled: true
    api_key: "${TRIPADVISOR_API_KEY}"
    property_id: "${TRIPADVISOR_PROPERTY_ID}"

monitoring:
  check_frequency: 30 # minutes
  sentiment_threshold: 0.3 # Below this triggers alert
  response_required_rating: 4 # Respond to ratings below this

satisfaction_surveys:
  send_timing: 2 # hours after checkout
  reminder_timing: 24 # hours if no response
  incentive_threshold: 3 # Offer incentive for ratings below this

alerts:
  email: "reviews@fitzgeraldsguesthouse.ie"
  sms: "+353871234567"
  slack_webhook: "${SLACK_WEBHOOK_URL}"
```

### 3. Launch
```bash
npm run start
```

## 🔧 Core Components

### Review Monitor
```javascript
class ReviewMonitor {
  constructor(config) {
    this.platforms = this.initializePlatforms(config.platforms);
    this.sentimentAnalyzer = new SentimentAnalyzer();
    this.alertManager = new AlertManager(config.alerts);
    this.checkInterval = config.monitoring.check_frequency * 60 * 1000; // Convert to ms
  }

  async startMonitoring() {
    console.log('🔍 Starting review monitoring...');

    // Initial scan
    await this.scanAllPlatforms();

    // Set up recurring monitoring
    setInterval(() => {
      this.scanAllPlatforms();
    }, this.checkInterval);
  }

  async scanAllPlatforms() {
    for (const platform of Object.keys(this.platforms)) {
      try {
        const newReviews = await this.platforms[platform].getNewReviews();

        for (const review of newReviews) {
          await this.processNewReview(review, platform);
        }

      } catch (error) {
        console.error(`Error scanning ${platform}:`, error);
        await this.alertManager.sendError(`Failed to scan ${platform}: ${error.message}`);
      }
    }
  }

  async processNewReview(review, platform) {
    // Analyze sentiment
    const sentiment = await this.sentimentAnalyzer.analyze(review.content);

    // Enrich review data
    const enrichedReview = {
      ...review,
      platform,
      sentiment: sentiment.score,
      sentiment_label: sentiment.label,
      categories: await this.categorizeReview(review),
      urgency: this.calculateUrgency(review, sentiment),
      processedAt: new Date()
    };

    // Save to database
    await this.saveReview(enrichedReview);

    // Trigger appropriate actions
    if (sentiment.score < this.config.sentiment_threshold) {
      await this.handleNegativeReview(enrichedReview);
    } else {
      await this.handlePositiveReview(enrichedReview);
    }

    // Send alerts if needed
    if (enrichedReview.urgency === 'high') {
      await this.alertManager.sendUrgentAlert(enrichedReview);
    }
  }

  async categorizeReview(review) {
    const categories = [];
    const content = review.content.toLowerCase();

    // Service categories
    if (content.includes('staff') || content.includes('service')) {
      categories.push('service');
    }
    if (content.includes('clean') || content.includes('tidy')) {
      categories.push('cleanliness');
    }
    if (content.includes('breakfast') || content.includes('food')) {
      categories.push('dining');
    }
    if (content.includes('room') || content.includes('bed')) {
      categories.push('accommodation');
    }
    if (content.includes('location') || content.includes('convenient')) {
      categories.push('location');
    }
    if (content.includes('value') || content.includes('price')) {
      categories.push('value');
    }

    return categories;
  }
}
```

### Response Generator
```javascript
class ResponseGenerator {
  constructor(config) {
    this.llm = new ChatOpenAI({ modelName: 'gpt-4' });
    this.brandVoice = config.brand_voice;
    this.propertyName = config.property.name;
    this.responseTemplates = this.loadResponseTemplates();
  }

  async generateResponse(review) {
    const responsePrompt = this.buildResponsePrompt(review);

    const response = await this.llm.call([{
      role: 'user',
      content: responsePrompt
    }]);

    // Post-process for brand consistency
    const brandConsistentResponse = await this.ensureBrandConsistency(response.content, review);

    return {
      response: brandConsistentResponse,
      tone: this.analyzeTone(review),
      personalizations: this.extractPersonalizations(review),
      generatedAt: new Date()
    };
  }

  buildResponsePrompt(review) {
    return `
You are responding to a guest review for ${this.propertyName}, a charming B&B in Westport, Ireland.

Review Details:
- Platform: ${review.platform}
- Rating: ${review.rating}/5
- Guest: ${review.guestName || 'Guest'}
- Content: "${review.content}"
- Sentiment: ${review.sentiment_label}
- Categories: ${review.categories.join(', ')}

Brand Voice: ${this.brandVoice}
Owners: Mary and John Fitzgerald

Response Guidelines:
1. Thank the guest personally
2. Address specific points they mentioned
3. Show genuine appreciation for positive feedback
4. For concerns, acknowledge and show how you're improving
5. Invite them back personally
6. Keep tone ${this.brandVoice}
7. Mention specific details from their stay if available
8. Maximum 150 words

Generate a warm, personal response that feels authentic to a family-run B&B:
`;
  }

  loadResponseTemplates() {
    return {
      excellent_5_star: `
        Thank you so much for your wonderful 5-star review!
        {specific_thanks}
        It means the world to us that {positive_highlight}.
        We can't wait to welcome you back to Westport!
        Warm regards, Mary & John
      `,

      good_4_star: `
        Thank you for taking time to review your stay with us!
        {specific_thanks}
        {improvement_note}
        We hope to see you again soon!
        Best wishes, Mary & John
      `,

      concern_resolution: `
        Thank you for your feedback and bringing {concern} to our attention.
        {acknowledgment}
        {action_taken}
        We'd love the opportunity to provide you with the experience you deserve.
        Sincerely, Mary & John
      `
    };
  }

  async ensureBrandConsistency(response, review) {
    // Check for brand voice compliance
    const voiceCheck = await this.checkBrandVoice(response);

    if (!voiceCheck.consistent) {
      // Regenerate with stronger brand voice guidance
      return await this.regenerateWithStrongerGuidance(response, review);
    }

    return response;
  }
}
```

### Satisfaction Survey Manager
```javascript
class SatisfactionSurveyManager {
  async sendPostStaySurvey(guest) {
    const survey = await this.generatePersonalizedSurvey(guest);

    // Send survey via preferred communication channel
    const sent = await this.sendSurvey(guest, survey);

    if (sent) {
      // Schedule reminder if no response
      await this.scheduleReminder(guest, survey.id);

      // Track survey metrics
      await this.trackSurveyMetrics(guest, survey);
    }

    return sent;
  }

  async generatePersonalizedSurvey(guest) {
    const survey = {
      id: this.generateSurveyId(),
      guestId: guest.id,
      guestName: guest.name,
      checkoutDate: guest.checkOut,
      roomNumber: guest.roomNumber,
      lengthOfStay: guest.nights,
      questions: [
        {
          id: 'overall_rating',
          type: 'rating',
          question: 'How would you rate your overall experience at Fitzgerald\'s Guesthouse?',
          scale: 5,
          required: true
        },
        {
          id: 'recommendation_likelihood',
          type: 'nps',
          question: 'How likely are you to recommend us to friends or family?',
          scale: 10,
          required: true
        },
        {
          id: 'room_satisfaction',
          type: 'rating',
          question: `How satisfied were you with Room ${guest.roomNumber}?`,
          scale: 5,
          required: true
        },
        {
          id: 'breakfast_rating',
          type: 'rating',
          question: 'How would you rate our breakfast?',
          scale: 5,
          required: false
        },
        {
          id: 'improvement_suggestions',
          type: 'text',
          question: 'What could we do to improve your experience?',
          required: false
        },
        {
          id: 'public_review_permission',
          type: 'boolean',
          question: 'May we invite you to share your experience on Booking.com or Google?',
          required: false
        }
      ],
      incentive: this.determineIncentive(guest)
    };

    return survey;
  }

  async processSurveyResponse(surveyId, responses) {
    const survey = await this.getSurvey(surveyId);
    const guest = await this.getGuest(survey.guestId);

    // Calculate satisfaction scores
    const scores = this.calculateSatisfactionScores(responses);

    // Identify issues needing attention
    const issues = this.identifyIssues(responses, scores);

    // Store responses
    await this.storeSurveyResponse({
      surveyId,
      guestId: guest.id,
      responses,
      scores,
      issues,
      completedAt: new Date()
    });

    // Take action based on scores
    if (scores.overall < 4) {
      await this.handleUnsatisfiedGuest(guest, responses, issues);
    } else if (scores.overall >= 4 && responses.public_review_permission) {
      await this.invitePublicReview(guest, scores);
    }

    return { scores, issues, actionsTaken: await this.getActionsTaken(scores, issues) };
  }

  async handleUnsatisfiedGuest(guest, responses, issues) {
    // Send personalized follow-up
    await this.sendServiceRecoveryMessage(guest, issues);

    // Offer compensation if appropriate
    const compensation = this.determineCompensation(issues);
    if (compensation) {
      await this.offerCompensation(guest, compensation);
    }

    // Alert management
    await this.alertManagement({
      type: 'unsatisfied_guest',
      guest: guest,
      issues: issues,
      urgency: 'high'
    });

    // Schedule follow-up
    await this.scheduleFollowUp(guest, 7); // 7 days
  }
}
```

### Reputation Analytics
```javascript
class ReputationAnalytics {
  async generateReputationReport(period = 30) {
    const reviews = await this.getReviewsInPeriod(period);
    const surveys = await this.getSurveysInPeriod(period);

    return {
      overview: {
        totalReviews: reviews.length,
        averageRating: this.calculateAverageRating(reviews),
        ratingDistribution: this.getRatingDistribution(reviews),
        sentimentBreakdown: this.getSentimentBreakdown(reviews),
        responseRate: this.calculateResponseRate(reviews)
      },

      platformPerformance: {
        booking_com: this.analyzePlatformPerformance(reviews, 'booking_com'),
        airbnb: this.analyzePlatformPerformance(reviews, 'airbnb'),
        google: this.analyzePlatformPerformance(reviews, 'google'),
        tripadvisor: this.analyzePlatformPerformance(reviews, 'tripadvisor')
      },

      feedback_analysis: {
        common_complaints: this.getCommonComplaints(reviews),
        improvement_areas: this.getImprovementAreas(reviews, surveys),
        guest_highlights: this.getGuestHighlights(reviews),
        category_performance: this.getCategoryPerformance(reviews)
      },

      trends: {
        rating_trend: this.calculateRatingTrend(reviews),
        volume_trend: this.calculateVolumeTrend(reviews),
        sentiment_trend: this.calculateSentimentTrend(reviews),
        seasonal_patterns: this.analyzeSeasonalPatterns(reviews)
      },

      competitive_analysis: {
        market_position: await this.getMarketPosition(),
        competitor_comparison: await this.getCompetitorComparison(),
        ranking_changes: await this.getRankingChanges()
      },

      action_items: this.generateActionItems(reviews, surveys)
    };
  }

  generateActionItems(reviews, surveys) {
    const actionItems = [];

    // Analyze feedback patterns
    const commonComplaints = this.getCommonComplaints(reviews);

    for (const complaint of commonComplaints) {
      if (complaint.frequency > 3) { // More than 3 mentions
        actionItems.push({
          type: 'improvement_needed',
          category: complaint.category,
          issue: complaint.issue,
          frequency: complaint.frequency,
          priority: this.calculatePriority(complaint),
          suggested_actions: this.getSuggestedActions(complaint)
        });
      }
    }

    // Check response times
    const slowResponses = reviews.filter(r => r.responseTime > 24); // Hours
    if (slowResponses.length > 0) {
      actionItems.push({
        type: 'response_time_improvement',
        affected_reviews: slowResponses.length,
        priority: 'medium',
        suggested_actions: ['Set up automated response alerts', 'Assign backup response team']
      });
    }

    // Identify review request opportunities
    const satisfiedGuests = surveys.filter(s => s.overall_rating >= 4 && !s.public_review_given);
    if (satisfiedGuests.length > 0) {
      actionItems.push({
        type: 'review_request_opportunity',
        potential_reviews: satisfiedGuests.length,
        priority: 'low',
        suggested_actions: ['Send personalized review requests', 'Offer small incentive for reviews']
      });
    }

    return actionItems.sort((a, b) => this.priorityWeight(b.priority) - this.priorityWeight(a.priority));
  }
}
```

## 🤖 AI Conversation Flows

### Proactive Issue Resolution
```yaml
flows:
  post_checkout_survey:
    trigger: "2_hours_after_checkout"
    message: |
      Hi {guest_name}! 👋

      Thank you for staying with us at Fitzgerald's Guesthouse.

      We'd love to hear about your experience!

      📋 Quick 2-minute survey: {survey_link}

      Your feedback helps us improve and means the world to us.

      Mary & John 💚

  unsatisfied_guest_follow_up:
    trigger: "survey_rating_below_4"
    message: |
      Hi {guest_name},

      Thank you for taking time to complete our survey.

      I'm personally sorry that your experience wasn't up to our usual standards. 😔

      {specific_issue_acknowledgment}

      I'd love to speak with you directly to understand how we can improve and make this right.

      Could you spare 5 minutes for a quick call?
      📞 +353 87 123 4567

      Or simply reply to this message.

      With sincere apologies,
      Mary Fitzgerald

  review_invitation:
    trigger: "high_satisfaction_score"
    delay: "24_hours"
    message: |
      Hi {guest_name}!

      We're so delighted you enjoyed your stay with us! 🌟

      Would you mind sharing your experience to help other travelers discover Westport?

      📝 Leave a review:
      • Booking.com: {booking_review_link}
      • Google: {google_review_link}
      • TripAdvisor: {tripadvisor_review_link}

      As a small thank you, here's 10% off your next stay: CODE: REVIEW10

      Warmly,
      Mary & John
```

### Review Response Templates
```yaml
response_templates:
  excellent_5_star:
    template: |
      Dear {guest_name},

      What a wonderful review to read! 🌟 Thank you so much for choosing Fitzgerald's Guesthouse.

      {specific_praise_acknowledgment}

      It's guests like you who make running our little B&B such a joy. We're thrilled that {specific_highlight}.

      We can't wait to welcome you back to Westport!

      Warmest regards,
      Mary & John Fitzgerald

  good_4_star:
    template: |
      Thank you {guest_name} for taking time to review your stay!

      We're so pleased you enjoyed {positive_aspects}.

      {gentle_improvement_note}

      Your feedback helps us continue improving, and we hope to welcome you back soon!

      Best wishes,
      Mary & John

  constructive_3_star:
    template: |
      Dear {guest_name},

      Thank you for your honest feedback about your stay with us.

      {specific_issue_acknowledgment}

      {action_taken_or_planned}

      We'd be honored to have another opportunity to provide you with the experience you deserve.

      Sincerely,
      Mary & John Fitzgerald

  concerning_2_star:
    template: |
      Dear {guest_name},

      I'm genuinely sorry that your stay didn't meet expectations. 😔

      {detailed_issue_acknowledgment}

      {immediate_action_taken}

      I'd very much like to speak with you personally to understand how we can improve.

      Please call me directly: +353 87 123 4567

      With sincere apologies,
      Mary Fitzgerald
```

## 📊 Analytics Dashboard

### Real-time Reputation Metrics
```javascript
class ReputationDashboard {
  async getCurrentMetrics() {
    return {
      liveRating: {
        booking_com: await this.getLiveRating('booking_com'),
        airbnb: await this.getLiveRating('airbnb'),
        google: await this.getLiveRating('google'),
        tripadvisor: await this.getLiveRating('tripadvisor'),
        overall: await this.getOverallRating()
      },

      recentActivity: {
        newReviews: await this.getNewReviews(24), // Last 24 hours
        pendingResponses: await this.getPendingResponses(),
        satisfactionSurveys: await this.getRecentSurveys(7), // Last 7 days
        alertsTriggered: await this.getRecentAlerts(24)
      },

      trends: {
        ratingTrend: await this.getRatingTrend(30), // Last 30 days
        volumeTrend: await this.getVolumeTrend(30),
        responseTimeTrend: await this.getResponseTimeTrend(30),
        satisfactionTrend: await this.getSatisfactionTrend(30)
      },

      competitivePosition: {
        marketRanking: await this.getMarketRanking(),
        competitorComparison: await this.getCompetitorComparison(),
        marketShare: await this.getMarketShare()
      }
    };
  }

  async generateImprovementInsights() {
    const reviews = await this.getRecentReviews(90); // Last 90 days
    const surveys = await this.getRecentSurveys(90);

    return {
      strengthsToLeverage: this.identifyStrengths(reviews),
      improvementOpportunities: this.identifyImprovements(reviews, surveys),
      guestExpectationGaps: this.analyzeExpectationGaps(surveys),
      seasonalConsiderations: this.analyzeSeasonalFeedback(reviews),
      competitiveAdvantages: this.identifyCompetitiveAdvantages(reviews)
    };
  }
}
```

## 🔗 Platform Integrations

### Review Platform APIs
```javascript
// Booking.com Integration
class BookingComConnector {
  async getNewReviews() {
    const response = await this.api.get(`/properties/${this.propertyId}/reviews`, {
      params: {
        since: this.lastCheckTimestamp,
        limit: 100
      }
    });

    return response.data.reviews.map(review => ({
      id: review.review_id,
      platform: 'booking_com',
      guestName: review.guest.display_name,
      rating: review.review_score,
      content: review.content,
      date: review.review_date,
      language: review.language,
      stayDate: review.stay_date,
      roomType: review.room_type
    }));
  }

  async postResponse(reviewId, response) {
    return await this.api.post(`/reviews/${reviewId}/responses`, {
      response_text: response,
      responder_name: 'Mary & John Fitzgerald'
    });
  }
}

// Google My Business Integration
class GoogleMyBusinessConnector {
  async getNewReviews() {
    const response = await this.api.get(`/accounts/${this.accountId}/locations/${this.locationId}/reviews`);

    return response.data.reviews
      .filter(review => new Date(review.createTime) > this.lastCheckTimestamp)
      .map(review => ({
        id: review.name,
        platform: 'google',
        guestName: review.reviewer.displayName,
        rating: review.starRating,
        content: review.comment,
        date: review.createTime
      }));
  }
}
```

## 🛠️ Maintenance & Updates

### Daily Tasks
- Monitor new reviews across all platforms
- Send satisfaction surveys to recent checkouts
- Process survey responses and identify issues
- Generate and send review responses
- Update reputation dashboard metrics

### Weekly Tasks
- Analyze review trends and patterns
- Generate competitive analysis reports
- Review and optimize response templates
- Follow up on unresolved guest issues

### Monthly Tasks
- Generate comprehensive reputation reports
- Analyze ROI of reputation management efforts
- Update review platform integrations
- Plan reputation improvement initiatives

## 📞 Support

For questions about the Review & Reputation Manager:
- 📧 Email: reputation-support@floutlabs.com
- 📱 WhatsApp: +353 1 234 5678
- 🌐 Documentation: [docs.floutlabs.com/reputation](https://docs.floutlabs.com/reputation)

---

*Protect and enhance your reputation while turning guests into advocates.*