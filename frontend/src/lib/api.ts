import type {
  AssistantRequest,
  AssistantResponse,
  AuditLog,
  Patient,
  PatientDetail,
} from "@/types/api";


const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";


async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(
    `${API_URL}${path}`,
    {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    },
  );

  if (!response.ok) {
    const body = await response.text();

    throw new Error(
      body ||
        `Request failed with status ${response.status}`,
    );
  }

  return response.json() as Promise<T>;
}


export function getPatients(): Promise<Patient[]> {
  return request<Patient[]>("/patients");
}


export function getPatient(
  patientId: number,
): Promise<PatientDetail> {
  return request<PatientDetail>(
    `/patients/${patientId}`,
  );
}


export function askAssistant(
  payload: AssistantRequest,
): Promise<AssistantResponse> {
  return request<AssistantResponse>(
    "/assistant/chat",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}


export function getAuditLogs(): Promise<AuditLog[]> {
  return request<AuditLog[]>("/audit");
}


export function getPatientAuditLogs(
  patientId: number,
): Promise<AuditLog[]> {
  return request<AuditLog[]>(
    `/audit/patient/${patientId}`,
  );
}