export interface MedicalHistory {
  id: number;
  condition: string;
  diagnosis_date: string | null;
  notes: string | null;
}

export interface BloodPressureMeasurement {
  id: number;
  systolic: number;
  diastolic: number;
  measured_at: string;
}

export interface Medication {
  id: number;
  name: string;
  dosage: string;
  frequency: string;
  start_date: string | null;
  active: boolean;
}

export interface LabExam {
  id: number;
  exam_type: string;
  result: string | null;
  reference_range: string | null;
  status: string;
  performed_at: string | null;
}

export interface Patient {
  id: number;
  name: string;
  birth_date: string;
  sex: string;
  weight_kg: number | null;
  height_cm: number | null;
}

export interface PatientDetail extends Patient {
  medical_history: MedicalHistory[];
  blood_pressure_measurements: BloodPressureMeasurement[];
  medications: Medication[];
  lab_exams: LabExam[];
}

export interface AssistantRequest {
  patient_id: number;
  question: string;
}

export interface AssistantResponse {
  patient_id: number;
  response: string;
  safety_status: string;
  safety_violations: string[];
  sources: string[];
  audit_log_id: number;
}

export interface AuditLog {
  id: number;
  patient_id: number;
  question: string;
  model_response: string;
  retrieved_context: Record<
    string,
    unknown
  >;
  validation_result: Record<
    string,
    unknown
  >;
  sources: string[];
  created_at: string;
}