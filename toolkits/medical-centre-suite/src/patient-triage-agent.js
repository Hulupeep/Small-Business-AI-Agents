/**
 * Patient Triage & Booking Agent
 * Intelligent appointment scheduling with clinical assessment
 */

class PatientTriageAgent {
  constructor(config) {
    this.hseProtocols = config.hseProtocols;
    this.doctorSchedules = config.doctorSchedules;
    this.urgencyMatrix = this.initializeUrgencyMatrix();
    this.specialtyMapping = this.initializeSpecialtyMapping();
  }

  /**
   * Assess patient symptoms and determine urgency level
   * @param {Object} symptoms - Patient reported symptoms
   * @returns {Object} Triage assessment with urgency and recommendations
   */
  async assessSymptoms(symptoms) {
    const {
      primarySymptoms,
      duration,
      severity,
      patientAge,
      medicalHistory,
      vitals
    } = symptoms;

    // AI-powered symptom analysis using HSE clinical protocols
    const riskFactors = this.calculateRiskFactors(symptoms);
    const urgencyScore = this.calculateUrgencyScore(riskFactors);
    const clinicalPriority = this.determineClinicalPriority(urgencyScore);

    // Red flag symptom detection
    const redFlags = this.detectRedFlags(primarySymptoms, vitals, medicalHistory);

    if (redFlags.length > 0) {
      return this.createEmergencyResponse(redFlags, symptoms);
    }

    // Specialty-based doctor matching
    const recommendedSpecialty = this.matchSpecialty(primarySymptoms);
    const availableDoctors = await this.findAvailableDoctors(
      recommendedSpecialty,
      clinicalPriority
    );

    return {
      urgency: clinicalPriority,
      urgencyScore,
      recommendedSpecialty,
      availableDoctors,
      suggestedTimeframe: this.calculateTimeframe(clinicalPriority),
      clinicalNotes: this.generateClinicalNotes(symptoms, riskFactors),
      followUpRequired: this.assessFollowUpNeeds(symptoms),
      patientEducation: this.getPatientEducation(primarySymptoms)
    };
  }

  /**
   * Book appointment with intelligent scheduling
   */
  async bookAppointment(triageResult, patientPreferences) {
    const { urgency, recommendedSpecialty, availableDoctors } = triageResult;
    const { preferredTime, preferredDoctor, flexibleTiming } = patientPreferences;

    // Smart scheduling algorithm
    const optimalSlots = await this.findOptimalSlots({
      doctors: availableDoctors,
      urgency,
      preferredTime,
      preferredDoctor,
      flexibility: flexibleTiming
    });

    // Handle urgent vs routine booking logic
    if (urgency === 'urgent' || urgency === 'emergency') {
      return this.handleUrgentBooking(optimalSlots, triageResult);
    }

    return this.handleRoutineBooking(optimalSlots, patientPreferences);
  }

  /**
   * Initialize urgency matrix based on HSE protocols
   */
  initializeUrgencyMatrix() {
    return {
      emergency: {
        symptoms: [
          'chest pain with radiation',
          'severe breathing difficulty',
          'loss of consciousness',
          'severe allergic reaction',
          'suspected stroke'
        ],
        timeframe: 'immediate',
        priority: 1
      },
      urgent: {
        symptoms: [
          'moderate chest pain',
          'high fever with confusion',
          'severe abdominal pain',
          'significant bleeding',
          'suspected fracture'
        ],
        timeframe: 'within 2 hours',
        priority: 2
      },
      routine: {
        symptoms: [
          'minor cold symptoms',
          'routine check-up',
          'prescription renewal',
          'minor skin conditions',
          'general wellness'
        ],
        timeframe: 'within 1-2 weeks',
        priority: 3
      }
    };
  }

  /**
   * Map symptoms to medical specialties
   */
  initializeSpecialtyMapping() {
    return {
      'cardiology': [
        'chest pain', 'palpitations', 'shortness of breath',
        'high blood pressure', 'heart murmur'
      ],
      'dermatology': [
        'skin rash', 'moles', 'acne', 'eczema', 'skin cancer screening'
      ],
      'orthopedics': [
        'joint pain', 'back pain', 'sports injury', 'fracture'
      ],
      'general_practice': [
        'cold symptoms', 'flu', 'general check-up', 'vaccination',
        'prescription renewal', 'health screening'
      ],
      'pediatrics': [
        'child fever', 'child vaccination', 'growth concerns',
        'behavioral issues'
      ]
    };
  }

  /**
   * Calculate risk factors based on patient presentation
   */
  calculateRiskFactors(symptoms) {
    const riskFactors = [];

    // Age-based risk
    if (symptoms.patientAge > 65) {
      riskFactors.push({ factor: 'elderly', weight: 0.3 });
    }

    // Comorbidity risk
    const highRiskConditions = [
      'diabetes', 'heart disease', 'COPD', 'immunocompromised'
    ];

    symptoms.medicalHistory?.forEach(condition => {
      if (highRiskConditions.includes(condition.toLowerCase())) {
        riskFactors.push({ factor: condition, weight: 0.4 });
      }
    });

    // Symptom severity
    if (symptoms.severity === 'severe') {
      riskFactors.push({ factor: 'severe_symptoms', weight: 0.5 });
    }

    // Duration factor
    if (symptoms.duration && this.parseToHours(symptoms.duration) < 1) {
      riskFactors.push({ factor: 'acute_onset', weight: 0.3 });
    }

    return riskFactors;
  }

  /**
   * Detect red flag symptoms requiring immediate attention
   */
  detectRedFlags(symptoms, vitals, medicalHistory) {
    const redFlags = [];

    // Cardiac red flags
    if (symptoms.includes('chest pain') && symptoms.includes('shortness of breath')) {
      redFlags.push('suspected_acute_coronary_syndrome');
    }

    // Neurological red flags
    if (symptoms.includes('sudden severe headache') ||
        symptoms.includes('facial drooping') ||
        symptoms.includes('speech difficulty')) {
      redFlags.push('suspected_stroke');
    }

    // Vital sign red flags
    if (vitals) {
      if (vitals.bloodPressure?.systolic > 180 || vitals.bloodPressure?.diastolic > 110) {
        redFlags.push('hypertensive_crisis');
      }
      if (vitals.temperature > 39.5) {
        redFlags.push('high_fever');
      }
    }

    return redFlags;
  }

  /**
   * Find optimal appointment slots using multi-criteria optimization
   */
  async findOptimalSlots(criteria) {
    const { doctors, urgency, preferredTime, preferredDoctor, flexibility } = criteria;

    const availableSlots = [];

    for (const doctor of doctors) {
      const schedule = await this.getDoctorSchedule(doctor.id);
      const slots = this.findAvailableSlots(schedule, urgency);

      slots.forEach(slot => {
        const score = this.calculateSlotScore(slot, criteria);
        availableSlots.push({
          ...slot,
          doctorId: doctor.id,
          doctorName: doctor.name,
          specialty: doctor.specialty,
          score
        });
      });
    }

    // Sort by score (best matches first)
    return availableSlots.sort((a, b) => b.score - a.score);
  }

  /**
   * Handle urgent appointment booking with priority access
   */
  async handleUrgentBooking(optimalSlots, triageResult) {
    const urgentSlot = optimalSlots[0]; // Take the best available slot

    if (!urgentSlot) {
      // No immediate slots available - implement overflow protocol
      return this.activateUrgentProtocol(triageResult);
    }

    // Book the urgent appointment
    const booking = await this.createBooking({
      slot: urgentSlot,
      priority: 'urgent',
      triageNotes: triageResult.clinicalNotes,
      preparationInstructions: this.getPreparationInstructions(triageResult)
    });

    // Notify clinical staff of urgent booking
    await this.notifyUrgentBooking(booking, triageResult);

    return booking;
  }

  /**
   * Generate clinical notes for handoff to medical staff
   */
  generateClinicalNotes(symptoms, riskFactors) {
    const notes = {
      chiefComplaint: symptoms.primarySymptoms.join(', '),
      duration: symptoms.duration,
      severity: symptoms.severity,
      associatedSymptoms: symptoms.secondarySymptoms || [],
      riskFactors: riskFactors.map(rf => rf.factor),
      vitals: symptoms.vitals,
      allergies: symptoms.allergies,
      currentMedications: symptoms.currentMedications,
      triageDateTime: new Date().toISOString(),
      triageNurse: 'AI_TRIAGE_SYSTEM'
    };

    return notes;
  }

  /**
   * Provide patient education based on symptoms
   */
  getPatientEducation(symptoms) {
    const educationMap = {
      'cold symptoms': {
        advice: 'Rest, increase fluid intake, consider over-the-counter remedies',
        warning: 'Seek immediate care if fever exceeds 39°C or breathing becomes difficult',
        duration: 'Symptoms typically resolve in 7-10 days'
      },
      'chest pain': {
        advice: 'Avoid strenuous activity until medical assessment',
        warning: 'Call 999 immediately if pain worsens or spreads to arm/jaw',
        preparation: 'Bring list of current medications and recent ECG if available'
      },
      'skin rash': {
        advice: 'Avoid scratching, keep area clean and dry',
        warning: 'Seek urgent care if rash spreads rapidly or you develop fever',
        preparation: 'Take photos of rash progression to show doctor'
      }
    };

    return symptoms.map(symptom =>
      educationMap[symptom] || { advice: 'Follow pre-appointment instructions' }
    );
  }

  /**
   * Activate urgent care protocol when no slots available
   */
  async activateUrgentProtocol(triageResult) {
    // Protocol options in order of preference:
    // 1. Double-book with existing appointment
    // 2. Extend practice hours
    // 3. Refer to urgent care center
    // 4. Arrange telephone consultation

    const protocolOptions = await this.evaluateUrgentOptions(triageResult);

    return {
      status: 'urgent_protocol_activated',
      options: protocolOptions,
      recommendedAction: protocolOptions[0],
      escalationRequired: true,
      contactNumber: this.getUrgentContactNumber()
    };
  }
}

module.exports = PatientTriageAgent;