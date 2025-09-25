/**
 * Clinical Workflow Manager
 * End-to-end patient journey optimization and care coordination
 */

class ClinicalWorkflowManager {
  constructor(config) {
    this.healthlinkClient = config.healthlinkClient;
    this.labIntegrations = config.labIntegrations;
    this.prescriptionSystem = config.prescriptionSystem;
    this.referralSystem = config.referralSystem;
    this.vaccinationTracker = config.vaccinationTracker;
    this.workflowTemplates = this.initializeWorkflowTemplates();
  }

  /**
   * Create and execute patient care pathway
   */
  async processPatientJourney(patientId, visitReason) {
    const patient = await this.getPatientRecord(patientId);
    const workflow = await this.createPatientPathway(patient, visitReason);

    // Initialize workflow tracking
    const workflowId = await this.initializeWorkflow(workflow);

    try {
      // Execute workflow steps
      const result = await this.executeWorkflowSteps(workflow);

      // Generate clinical summary
      const summary = await this.generateClinicalSummary(workflowId, result);

      // Update patient record
      await this.updatePatientRecord(patientId, summary);

      return {
        workflowId,
        status: 'completed',
        summary,
        nextSteps: result.nextSteps,
        followUpRequired: result.followUpRequired
      };

    } catch (error) {
      await this.handleWorkflowError(workflowId, error);
      throw error;
    }
  }

  /**
   * Create patient-specific care pathway
   */
  async createPatientPathway(patient, visitReason) {
    const baseTemplate = this.selectWorkflowTemplate(visitReason);

    // Personalize workflow based on patient factors
    const personalizedWorkflow = await this.personalizeWorkflow(
      baseTemplate,
      patient
    );

    // Add clinical decision points
    const enhancedWorkflow = this.addClinicalDecisionPoints(
      personalizedWorkflow,
      patient.medicalHistory
    );

    return {
      patientId: patient.id,
      visitReason,
      workflow: enhancedWorkflow,
      expectedDuration: this.calculateExpectedDuration(enhancedWorkflow),
      requiredResources: this.identifyRequiredResources(enhancedWorkflow),
      qualityMetrics: this.defineQualityMetrics(visitReason)
    };
  }

  /**
   * Execute workflow steps with real-time optimization
   */
  async executeWorkflowSteps(patientWorkflow) {
    const { workflow, patientId } = patientWorkflow;
    const executionLog = [];
    const results = {
      completedSteps: [],
      clinicalFindings: {},
      prescriptions: [],
      referrals: [],
      labOrders: [],
      followUpActions: [],
      nextSteps: []
    };

    for (const step of workflow.steps) {
      try {
        const stepResult = await this.executeWorkflowStep(step, patientId, results);

        executionLog.push({
          stepId: step.id,
          startTime: new Date(),
          status: 'completed',
          result: stepResult,
          duration: stepResult.executionTime
        });

        // Update results
        this.updateWorkflowResults(results, stepResult);

        // Check for conditional branching
        const nextSteps = await this.evaluateConditionalBranching(
          step,
          stepResult,
          patientWorkflow
        );

        if (nextSteps.length > 0) {
          workflow.steps.push(...nextSteps);
        }

      } catch (error) {
        await this.handleStepError(step, error, executionLog);
      }
    }

    return {
      ...results,
      executionLog,
      workflowCompleted: true,
      totalDuration: this.calculateTotalDuration(executionLog)
    };
  }

  /**
   * Execute individual workflow step
   */
  async executeWorkflowStep(step, patientId, currentResults) {
    const startTime = Date.now();
    let result;

    switch (step.type) {
      case 'clinical_assessment':
        result = await this.performClinicalAssessment(step, patientId);
        break;

      case 'diagnostic_test':
        result = await this.orderDiagnosticTest(step, patientId);
        break;

      case 'lab_order':
        result = await this.processLabOrder(step, patientId);
        break;

      case 'prescription':
        result = await this.generatePrescription(step, patientId, currentResults);
        break;

      case 'referral':
        result = await this.createReferral(step, patientId, currentResults);
        break;

      case 'patient_education':
        result = await this.providePatientEducation(step, patientId);
        break;

      case 'follow_up_scheduling':
        result = await this.scheduleFollowUp(step, patientId, currentResults);
        break;

      case 'vaccination':
        result = await this.administerVaccination(step, patientId);
        break;

      default:
        throw new Error(`Unknown workflow step type: ${step.type}`);
    }

    return {
      ...result,
      executionTime: Date.now() - startTime,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Process laboratory orders with automated result tracking
   */
  async processLabOrder(step, patientId) {
    const patient = await this.getPatientRecord(patientId);
    const labOrder = {
      patientId,
      patientPPS: patient.ppsNumber,
      tests: step.tests,
      priority: step.priority || 'routine',
      clinicalIndication: step.indication,
      orderingDoctor: step.doctorId,
      expectedResults: step.expectedResultDate
    };

    // Submit to connected laboratories
    const labSubmissions = await Promise.all(
      this.labIntegrations.map(async (lab) => {
        if (lab.supportsTests(step.tests)) {
          return await lab.submitOrder(labOrder);
        }
        return null;
      })
    );

    // Set up result monitoring
    const trackingId = await this.setupResultTracking(labOrder, labSubmissions);

    // Schedule result follow-up
    await this.scheduleResultFollowUp(trackingId, step.expectedResultDate);

    return {
      orderId: trackingId,
      labSubmissions: labSubmissions.filter(Boolean),
      status: 'submitted',
      tests: step.tests,
      expectedDate: step.expectedResultDate,
      trackingActive: true
    };
  }

  /**
   * Generate electronic prescription with drug interaction checking
   */
  async generatePrescription(step, patientId, currentResults) {
    const patient = await this.getPatientRecord(patientId);
    const currentMedications = patient.currentMedications || [];

    // Check for drug interactions
    const interactionCheck = await this.checkDrugInteractions(
      step.medication,
      currentMedications,
      patient.allergies
    );

    if (interactionCheck.hasInteractions) {
      await this.handleDrugInteractions(interactionCheck, step);
    }

    // Generate prescription
    const prescription = {
      patientId,
      patientPPS: patient.ppsNumber,
      medication: step.medication,
      dosage: step.dosage,
      frequency: step.frequency,
      duration: step.duration,
      quantity: step.quantity,
      repeats: step.repeats || 0,
      prescribingDoctor: step.doctorId,
      indication: step.indication,
      instructions: step.patientInstructions,
      interactionChecked: true,
      timestamp: new Date().toISOString()
    };

    // Submit to ePrescription system
    const prescriptionId = await this.prescriptionSystem.submitPrescription(prescription);

    // Add to patient's medication list
    await this.updatePatientMedications(patientId, step.medication);

    return {
      prescriptionId,
      medication: step.medication,
      status: 'prescribed',
      pharmacyNotified: true,
      patientInstructions: step.patientInstructions,
      interactionWarnings: interactionCheck.warnings
    };
  }

  /**
   * Create specialist referral with HealthLink integration
   */
  async createReferral(step, patientId, currentResults) {
    const patient = await this.getPatientRecord(patientId);
    const clinicalSummary = this.generateReferralSummary(currentResults);

    const referral = {
      patientId,
      patientPPS: patient.ppsNumber,
      patientDetails: {
        name: patient.name,
        dateOfBirth: patient.dateOfBirth,
        address: patient.address,
        phone: patient.phone
      },
      referralType: step.specialty,
      urgency: step.urgency || 'routine',
      clinicalQuestion: step.clinicalQuestion,
      relevantHistory: patient.relevantHistory,
      currentMedications: patient.currentMedications,
      allergies: patient.allergies,
      clinicalSummary,
      requestedInvestigations: step.requestedInvestigations,
      referringDoctor: step.doctorId,
      preferredConsultant: step.preferredConsultant,
      preferredHospital: step.preferredHospital
    };

    // Submit via HealthLink
    const referralId = await this.healthlinkClient.submitReferral(referral);

    // Set up status tracking
    await this.setupReferralTracking(referralId, referral);

    // Schedule follow-up reminder
    await this.scheduleReferralFollowUp(referralId, step.followUpDays || 14);

    return {
      referralId,
      specialty: step.specialty,
      status: 'submitted',
      trackingActive: true,
      estimatedAppointmentDate: await this.estimateAppointmentDate(step.specialty, step.urgency),
      patientNotified: true
    };
  }

  /**
   * Manage vaccination administration and record keeping
   */
  async administerVaccination(step, patientId) {
    const patient = await this.getPatientRecord(patientId);
    const vaccinationHistory = await this.vaccinationTracker.getHistory(patientId);

    // Check vaccination eligibility
    const eligibilityCheck = await this.checkVaccinationEligibility(
      step.vaccine,
      patient,
      vaccinationHistory
    );

    if (!eligibilityCheck.eligible) {
      throw new Error(`Vaccination not eligible: ${eligibilityCheck.reason}`);
    }

    // Record vaccination
    const vaccination = {
      patientId,
      patientPPS: patient.ppsNumber,
      vaccine: step.vaccine,
      batchNumber: step.batchNumber,
      expiryDate: step.expiryDate,
      administrationSite: step.site,
      administeredBy: step.nursId,
      administrationDate: new Date().toISOString(),
      nextDueDate: this.calculateNextDueDate(step.vaccine, patient.dateOfBirth)
    };

    // Update national immunization registry
    await this.vaccinationTracker.recordVaccination(vaccination);

    // Schedule next vaccination if required
    if (vaccination.nextDueDate) {
      await this.scheduleVaccinationReminder(patientId, vaccination.nextDueDate);
    }

    return {
      vaccinationId: vaccination.id,
      vaccine: step.vaccine,
      status: 'administered',
      nextDueDate: vaccination.nextDueDate,
      recordUpdated: true,
      registryNotified: true
    };
  }

  /**
   * Initialize workflow templates for common conditions
   */
  initializeWorkflowTemplates() {
    return {
      'annual_check_up': {
        name: 'Annual Health Check',
        steps: [
          { id: 'vitals', type: 'clinical_assessment', required: true },
          { id: 'history_review', type: 'clinical_assessment', required: true },
          { id: 'screening_labs', type: 'lab_order', conditional: true },
          { id: 'vaccinations', type: 'vaccination', conditional: true },
          { id: 'health_education', type: 'patient_education', required: true },
          { id: 'next_appointment', type: 'follow_up_scheduling', required: true }
        ],
        duration: 30,
        qualityMetrics: ['bp_measured', 'weight_recorded', 'smoking_status_updated']
      },

      'diabetes_review': {
        name: 'Diabetes Management Review',
        steps: [
          { id: 'glucose_check', type: 'diagnostic_test', required: true },
          { id: 'hba1c_order', type: 'lab_order', required: true },
          { id: 'foot_examination', type: 'clinical_assessment', required: true },
          { id: 'bp_check', type: 'clinical_assessment', required: true },
          { id: 'medication_review', type: 'prescription', conditional: true },
          { id: 'dietician_referral', type: 'referral', conditional: true },
          { id: 'diabetes_education', type: 'patient_education', required: true },
          { id: 'follow_up_3months', type: 'follow_up_scheduling', required: true }
        ],
        duration: 45,
        qualityMetrics: ['hba1c_target', 'bp_target', 'foot_risk_assessed']
      },

      'hypertension_management': {
        name: 'Blood Pressure Management',
        steps: [
          { id: 'bp_measurement', type: 'clinical_assessment', required: true },
          { id: 'cardiovascular_risk', type: 'clinical_assessment', required: true },
          { id: 'baseline_labs', type: 'lab_order', conditional: true },
          { id: 'medication_adjustment', type: 'prescription', conditional: true },
          { id: 'lifestyle_counseling', type: 'patient_education', required: true },
          { id: 'follow_up_4weeks', type: 'follow_up_scheduling', required: true }
        ],
        duration: 25,
        qualityMetrics: ['bp_target_achieved', 'medication_adherence']
      }
    };
  }

  /**
   * Check drug interactions using comprehensive database
   */
  async checkDrugInteractions(newMedication, currentMedications, allergies) {
    const interactions = [];
    const warnings = [];

    // Check drug-drug interactions
    for (const currentMed of currentMedications) {
      const interaction = await this.prescriptionSystem.checkInteraction(
        newMedication,
        currentMed
      );

      if (interaction.severity === 'major') {
        interactions.push({
          type: 'major_interaction',
          medication1: newMedication,
          medication2: currentMed,
          description: interaction.description,
          recommendation: interaction.recommendation
        });
      }
    }

    // Check allergies
    for (const allergy of allergies || []) {
      if (await this.prescriptionSystem.checkAllergy(newMedication, allergy)) {
        interactions.push({
          type: 'allergy_alert',
          medication: newMedication,
          allergy: allergy,
          severity: 'major'
        });
      }
    }

    return {
      hasInteractions: interactions.length > 0,
      interactions,
      warnings,
      safe: interactions.length === 0
    };
  }

  /**
   * Generate comprehensive clinical summary
   */
  generateClinicalSummary(workflowId, results) {
    return {
      workflowId,
      completionDate: new Date().toISOString(),
      clinicalFindings: results.clinicalFindings,
      diagnosticResults: results.diagnosticResults,
      treatmentPlan: {
        medications: results.prescriptions,
        referrals: results.referrals,
        followUpActions: results.followUpActions
      },
      qualityIndicators: this.calculateQualityIndicators(results),
      outcomeMetrics: this.calculateOutcomeMetrics(results),
      nextReviewDate: this.calculateNextReviewDate(results),
      clinicalDecisions: results.clinicalDecisions,
      patientEducationProvided: results.patientEducation
    };
  }
}

module.exports = ClinicalWorkflowManager;