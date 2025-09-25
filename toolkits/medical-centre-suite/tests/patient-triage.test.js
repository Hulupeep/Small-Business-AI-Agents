/**
 * Test Suite for Patient Triage & Booking Agent
 * Comprehensive testing of clinical assessment and booking algorithms
 */

const PatientTriageAgent = require('../src/patient-triage-agent');

describe('Patient Triage & Booking Agent', () => {
  let triageAgent;

  beforeEach(() => {
    triageAgent = new PatientTriageAgent({
      hseProtocols: {},
      doctorSchedules: mockDoctorSchedules
    });
  });

  describe('Symptom Assessment', () => {
    test('should correctly identify emergency symptoms', async () => {
      const symptoms = {
        primarySymptoms: ['chest pain', 'shortness of breath'],
        duration: '30 minutes',
        severity: 'severe',
        patientAge: 65,
        medicalHistory: ['diabetes', 'hypertension'],
        vitals: {
          bloodPressure: { systolic: 160, diastolic: 95 },
          heartRate: 110,
          temperature: 37.2
        }
      };

      const assessment = await triageAgent.assessSymptoms(symptoms);

      expect(assessment.urgency).toBe('emergency');
      expect(assessment.suggestedTimeframe).toBe('immediate');
      expect(assessment.recommendedSpecialty).toBe('cardiology');
    });

    test('should handle routine symptoms appropriately', async () => {
      const symptoms = {
        primarySymptoms: ['runny nose', 'mild cough'],
        duration: '3 days',
        severity: 'mild',
        patientAge: 35,
        medicalHistory: [],
        vitals: {
          temperature: 37.8
        }
      };

      const assessment = await triageAgent.assessSymptoms(symptoms);

      expect(assessment.urgency).toBe('routine');
      expect(assessment.recommendedSpecialty).toBe('general_practice');
      expect(assessment.suggestedTimeframe).toBe('within 1-2 weeks');
    });

    test('should detect red flag symptoms', async () => {
      const symptoms = {
        primarySymptoms: ['sudden severe headache', 'confusion'],
        duration: '1 hour',
        severity: 'severe',
        patientAge: 55,
        medicalHistory: ['hypertension'],
        vitals: {
          bloodPressure: { systolic: 190, diastolic: 115 }
        }
      };

      const assessment = await triageAgent.assessSymptoms(symptoms);

      expect(assessment.urgency).toBe('emergency');
      expect(assessment.clinicalNotes.riskFactors).toContain('hypertensive_crisis');
    });
  });

  describe('Doctor Matching Algorithm', () => {
    test('should match symptoms to appropriate specialty', () => {
      const skinSymptoms = ['rash', 'itching', 'skin lesion'];
      const specialty = triageAgent.matchSpecialty(skinSymptoms);
      expect(specialty).toBe('dermatology');

      const cardiacSymptoms = ['chest pain', 'palpitations'];
      const cardiacSpecialty = triageAgent.matchSpecialty(cardiacSymptoms);
      expect(cardiacSpecialty).toBe('cardiology');
    });

    test('should find available doctors for specialty', async () => {
      const availableDoctors = await triageAgent.findAvailableDoctors(
        'general_practice',
        'routine'
      );

      expect(availableDoctors).toBeDefined();
      expect(availableDoctors.length).toBeGreaterThan(0);
      expect(availableDoctors[0]).toHaveProperty('specialty', 'general_practice');
    });
  });

  describe('Appointment Booking', () => {
    test('should book urgent appointment with priority access', async () => {
      const triageResult = {
        urgency: 'urgent',
        recommendedSpecialty: 'cardiology',
        availableDoctors: mockCardiologists,
        clinicalNotes: {
          chiefComplaint: 'chest pain',
          riskFactors: ['elderly', 'diabetes']
        }
      };

      const patientPreferences = {
        preferredTime: 'morning',
        flexibleTiming: true
      };

      const booking = await triageAgent.bookAppointment(triageResult, patientPreferences);

      expect(booking.status).toBe('confirmed');
      expect(booking.priority).toBe('urgent');
      expect(booking.slot).toBeDefined();
    });

    test('should handle no available slots for urgent cases', async () => {
      // Mock scenario with no available slots
      jest.spyOn(triageAgent, 'findOptimalSlots').mockResolvedValue([]);

      const triageResult = {
        urgency: 'urgent',
        recommendedSpecialty: 'cardiology',
        availableDoctors: [],
        clinicalNotes: { chiefComplaint: 'chest pain' }
      };

      const patientPreferences = { flexibleTiming: true };

      const result = await triageAgent.bookAppointment(triageResult, patientPreferences);

      expect(result.status).toBe('urgent_protocol_activated');
      expect(result.escalationRequired).toBe(true);
      expect(result.options).toBeDefined();
    });
  });

  describe('Risk Factor Calculation', () => {
    test('should calculate risk factors correctly', () => {
      const symptoms = {
        patientAge: 75,
        severity: 'severe',
        duration: '30 minutes',
        medicalHistory: ['diabetes', 'heart disease', 'COPD']
      };

      const riskFactors = triageAgent.calculateRiskFactors(symptoms);

      expect(riskFactors).toEqual(
        expect.arrayContaining([
          expect.objectContaining({ factor: 'elderly' }),
          expect.objectContaining({ factor: 'diabetes' }),
          expect.objectContaining({ factor: 'heart disease' }),
          expect.objectContaining({ factor: 'severe_symptoms' }),
          expect.objectContaining({ factor: 'acute_onset' })
        ])
      );
    });

    test('should weight risk factors appropriately', () => {
      const riskFactors = [
        { factor: 'elderly', weight: 0.3 },
        { factor: 'diabetes', weight: 0.4 },
        { factor: 'severe_symptoms', weight: 0.5 }
      ];

      const urgencyScore = triageAgent.calculateUrgencyScore(riskFactors);
      expect(urgencyScore).toBeGreaterThan(0.5); // High risk should yield high score
    });
  });

  describe('Patient Education', () => {
    test('should provide appropriate education for symptoms', () => {
      const chestPainEducation = triageAgent.getPatientEducation(['chest pain']);

      expect(chestPainEducation[0]).toHaveProperty('warning');
      expect(chestPainEducation[0].warning).toContain('999');
      expect(chestPainEducation[0]).toHaveProperty('preparation');
    });

    test('should provide generic advice for unknown symptoms', () => {
      const unknownEducation = triageAgent.getPatientEducation(['rare condition']);

      expect(unknownEducation[0]).toHaveProperty('advice');
      expect(unknownEducation[0].advice).toBe('Follow pre-appointment instructions');
    });
  });

  describe('Clinical Notes Generation', () => {
    test('should generate comprehensive clinical notes', () => {
      const symptoms = {
        primarySymptoms: ['chest pain', 'shortness of breath'],
        secondarySymptoms: ['nausea'],
        duration: '2 hours',
        severity: 'moderate',
        vitals: {
          bloodPressure: { systolic: 140, diastolic: 90 },
          heartRate: 95
        },
        allergies: ['penicillin'],
        currentMedications: ['metformin', 'lisinopril']
      };

      const riskFactors = [{ factor: 'diabetes', weight: 0.4 }];
      const notes = triageAgent.generateClinicalNotes(symptoms, riskFactors);

      expect(notes).toHaveProperty('chiefComplaint', 'chest pain, shortness of breath');
      expect(notes).toHaveProperty('duration', '2 hours');
      expect(notes).toHaveProperty('severity', 'moderate');
      expect(notes).toHaveProperty('riskFactors', ['diabetes']);
      expect(notes).toHaveProperty('allergies', ['penicillin']);
      expect(notes).toHaveProperty('triageDateTime');
    });
  });

  describe('Slot Optimization', () => {
    test('should calculate slot scores correctly', () => {
      const slot = {
        datetime: '2024-01-15T10:00:00Z',
        doctorId: 'doc123'
      };

      const criteria = {
        urgency: 'routine',
        preferredTime: 'morning',
        preferredDoctor: 'doc123',
        flexibility: 0.8
      };

      const score = triageAgent.calculateSlotScore(slot, criteria);
      expect(score).toBeGreaterThan(0.5); // Should score well due to matching preferences
    });
  });

  describe('Error Handling', () => {
    test('should handle invalid symptom input gracefully', async () => {
      const invalidSymptoms = {
        primarySymptoms: null,
        patientAge: 'invalid'
      };

      await expect(triageAgent.assessSymptoms(invalidSymptoms))
        .rejects
        .toThrow('Invalid symptom data provided');
    });

    test('should handle booking system failures', async () => {
      // Mock booking system failure
      jest.spyOn(triageAgent, 'createBooking').mockRejectedValue(
        new Error('Booking system unavailable')
      );

      const triageResult = { urgency: 'routine' };
      const preferences = { flexibleTiming: true };

      await expect(triageAgent.bookAppointment(triageResult, preferences))
        .rejects
        .toThrow('Booking system unavailable');
    });
  });
});

// Mock data for testing
const mockDoctorSchedules = [
  {
    id: 'doc001',
    name: 'Dr. Sarah O\'Connor',
    specialty: 'general_practice',
    schedule: {
      monday: [
        { start: '09:00', end: '17:00', available: true }
      ]
    }
  },
  {
    id: 'doc002',
    name: 'Dr. Michael Murphy',
    specialty: 'cardiology',
    schedule: {
      monday: [
        { start: '08:00', end: '16:00', available: true }
      ]
    }
  }
];

const mockCardiologists = [
  {
    id: 'doc002',
    name: 'Dr. Michael Murphy',
    specialty: 'cardiology',
    experience: 15,
    rating: 4.8
  }
];