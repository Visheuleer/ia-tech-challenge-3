"use client";

import Link from "next/link";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  useParams,
} from "next/navigation";

import ReactMarkdown
  from "react-markdown";

import {
  Activity,
  AlertCircle,
  ArrowLeft,
  Bot,
  CalendarDays,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  CircleUserRound,
  ClipboardCheck,
  FileClock,
  FileText,
  HeartPulse,
  LoaderCircle,
  MessageSquareText,
  Pill,
  Send,
  ShieldCheck,
  Sparkles,
  Stethoscope,
  TestTube2,
  UserRound,
} from "lucide-react";

import {
  askAssistant,
  getPatient,
  getPatientAuditLogs,
} from "@/lib/api";

import type {
  AssistantResponse,
  AuditLog,
  PatientDetail,
} from "@/types/api";


function formatDate(
  value: string,
): string {
  return new Intl.DateTimeFormat(
    "pt-BR",
  ).format(
    new Date(
      value,
    ),
  );
}


function formatDateTime(
  value: string,
): string {
  return new Intl.DateTimeFormat(
    "pt-BR",
    {
      dateStyle: "short",
      timeStyle: "short",
    },
  ).format(
    new Date(
      value,
    ),
  );
}


function getInitials(
  name: string,
): string {
  return name
    .split(" ")
    .slice(0, 2)
    .map(
      (part) =>
        part.charAt(0),
    )
    .join("")
    .toUpperCase();
}


function SafetyBadge({
  status,
}: {
  status: string;
}) {
  const normalized =
    status.toLowerCase();

  if (
    normalized ===
    "safe"
  ) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">
        <CheckCircle2 className="size-3.5" />
        Seguro
      </span>
    );
  }

  if (
    normalized ===
    "needs_review"
  ) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-200 bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-700">
        <AlertCircle className="size-3.5" />
        Requer revisão
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-red-200 bg-red-50 px-2.5 py-1 text-xs font-semibold text-red-700">
      <AlertCircle className="size-3.5" />
      Bloqueado
    </span>
  );
}


function BloodPressureBadge({
  systolic,
  diastolic,
}: {
  systolic: number;
  diastolic: number;
}) {
  const critical =
    systolic >= 180 ||
    diastolic >= 110;

  const elevated =
    systolic >= 140 ||
    diastolic >= 90;

  if (critical) {
    return (
      <span className="rounded-full border border-red-200 bg-red-50 px-2 py-1 text-[10px] font-semibold text-red-700">
        Atenção crítica
      </span>
    );
  }

  if (elevated) {
    return (
      <span className="rounded-full border border-amber-200 bg-amber-50 px-2 py-1 text-[10px] font-semibold text-amber-700">
        Elevada
      </span>
    );
  }

  return (
    <span className="rounded-full border border-emerald-200 bg-emerald-50 px-2 py-1 text-[10px] font-semibold text-emerald-700">
      Estável
    </span>
  );
}


function AuditItem({
  log,
}: {
  log: AuditLog;
}) {
  const [
    expanded,
    setExpanded,
  ] = useState(false);

  const validation =
    log.validation_result as {
      status?: string;
      violations?: string[];
    };

  return (
    <article className="overflow-hidden rounded-2xl border border-slate-200 bg-white transition hover:border-slate-300">

      <button
        type="button"
        onClick={() =>
          setExpanded(
            (value) =>
              !value,
          )
        }
        className="flex w-full items-center justify-between gap-4 p-5 text-left"
      >

        <div className="flex min-w-0 items-center gap-4">

          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-slate-100">
            <FileClock className="size-4.5 text-slate-600" />
          </div>


          <div className="min-w-0">

            <div className="flex flex-wrap items-center gap-2">

              <span className="font-semibold text-slate-900">
                Audit #{log.id}
              </span>

              <SafetyBadge
                status={
                  validation.status ??
                  "unknown"
                }
              />

            </div>


            <p className="mt-1 truncate text-sm text-slate-500">
              {log.question}
            </p>


            <p className="mt-1 text-xs text-slate-400">
              {formatDateTime(
                log.created_at,
              )}
            </p>

          </div>

        </div>


        {expanded ? (
          <ChevronUp className="size-4 shrink-0 text-slate-400" />
        ) : (
          <ChevronDown className="size-4 shrink-0 text-slate-400" />
        )}

      </button>


      {expanded && (
        <div className="border-t border-slate-100 bg-slate-50/70 px-5 py-5">

          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-400">
              Pergunta
            </p>

            <p className="mt-2 text-sm leading-6 text-slate-700">
              {log.question}
            </p>
          </div>


          <div className="mt-5">

            <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-400">
              Saída do modelo
            </p>

            <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-700">
              {log.model_response}
            </p>

          </div>


          {log.sources.length >
            0 && (
            <div className="mt-5">

              <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-400">
                Fontes recuperadas
              </p>

              <div className="mt-2 flex flex-wrap gap-2">

                {log.sources.map(
                  (
                    source,
                  ) => (
                    <span
                      key={
                        source
                      }
                      className="rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 font-mono text-[11px] text-slate-600"
                    >
                      {
                        source
                      }
                    </span>
                  ),
                )}

              </div>

            </div>
          )}

        </div>
      )}

    </article>
  );
}


export default function PatientPage() {
  const params =
    useParams();

  const patientId =
    Number(
      params.id,
    );


  const [
    patient,
    setPatient,
  ] =
    useState<PatientDetail | null>(
      null,
    );

  const [
    auditLogs,
    setAuditLogs,
  ] =
    useState<AuditLog[]>(
      [],
    );

  const [
    question,
    setQuestion,
  ] =
    useState("");

  const [
    assistantResponse,
    setAssistantResponse,
  ] =
    useState<AssistantResponse | null>(
      null,
    );

  const [
    loadingPatient,
    setLoadingPatient,
  ] =
    useState(true);

  const [
    loadingAssistant,
    setLoadingAssistant,
  ] =
    useState(false);

  const [
    error,
    setError,
  ] =
    useState<string | null>(
      null,
    );


  useEffect(() => {
    async function loadData() {
      try {
        const [
          patientData,
          auditData,
        ] =
          await Promise.all([
            getPatient(
              patientId,
            ),
            getPatientAuditLogs(
              patientId,
            ),
          ]);

        setPatient(
          patientData,
        );

        setAuditLogs(
          auditData,
        );

      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Erro ao carregar dados.",
        );
      } finally {
        setLoadingPatient(
          false,
        );
      }
    }

    if (
      !Number.isNaN(
        patientId,
      )
    ) {
      loadData();
    }

  }, [patientId]);


  const latestBloodPressure =
    useMemo(() => {
      if (
        !patient ||
        patient
          .blood_pressure_measurements
          .length === 0
      ) {
        return null;
      }

      return [
        ...patient
          .blood_pressure_measurements,
      ].sort(
        (
          a,
          b,
        ) =>
          new Date(
            b.measured_at,
          ).getTime() -
          new Date(
            a.measured_at,
          ).getTime(),
      )[0];

    }, [patient]);


  const pendingExams =
    useMemo(
      () =>
        patient
          ?.lab_exams
          .filter(
            (exam) =>
              exam.status ===
              "pending",
          ) ??
        [],
      [patient],
    );


  const activeMedications =
    useMemo(
      () =>
        patient
          ?.medications
          .filter(
            (medication) =>
              medication.active,
          ) ??
        [],
      [patient],
    );


  async function handleAskAssistant() {
    if (
      !question.trim()
    ) {
      return;
    }

    try {
      setLoadingAssistant(
        true,
      );

      setError(null);

      const response =
        await askAssistant({
          patient_id:
            patientId,
          question:
            question.trim(),
        });

      setAssistantResponse(
        response,
      );

      const updatedLogs =
        await getPatientAuditLogs(
          patientId,
        );

      setAuditLogs(
        updatedLogs,
      );

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Erro ao consultar assistente.",
      );
    } finally {
      setLoadingAssistant(
        false,
      );
    }
  }


  if (
    loadingPatient
  ) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">

        <div className="flex flex-col items-center gap-4">

          <div className="flex size-12 items-center justify-center rounded-2xl bg-blue-600 shadow-lg shadow-blue-600/20">
            <LoaderCircle className="size-5 animate-spin text-white" />
          </div>

          <p className="text-sm font-medium text-slate-500">
            Carregando prontuário...
          </p>

        </div>

      </div>
    );
  }


  if (
    !patient
  ) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">

        <div className="section-card max-w-md p-8 text-center">

          <CircleUserRound className="mx-auto size-10 text-slate-400" />

          <h1 className="mt-4 text-lg font-semibold text-slate-900">
            Paciente não encontrado
          </h1>

          <Link
            href="/"
            className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-blue-600"
          >
            <ArrowLeft className="size-4" />
            Voltar para pacientes
          </Link>

        </div>

      </div>
    );
  }


  return (
    <div className="app-shell">

      <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-white/90 backdrop-blur-xl">

        <div className="page-container flex h-18 items-center justify-between">

          <Link
            href="/"
            className="flex items-center gap-3"
          >

            <div className="flex size-10 items-center justify-center rounded-xl bg-blue-600 shadow-sm shadow-blue-600/20">
              <HeartPulse className="size-5 text-white" />
            </div>


            <div className="hidden sm:block">

              <p className="text-[15px] font-semibold leading-none tracking-tight text-slate-900">
                Medical Assistant
              </p>

              <p className="mt-1 text-[11px] font-medium text-slate-400">
                Clinical Decision Support
              </p>

            </div>

          </Link>


          <Link
            href="/"
            className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs font-semibold text-slate-600 shadow-sm transition hover:bg-slate-50"
          >
            <ArrowLeft className="size-3.5" />
            Pacientes
          </Link>

        </div>

      </header>


      <main className="page-container py-8 md:py-10">

        <section className="section-card clinical-highlight overflow-hidden">

          <div className="relative bg-slate-950 px-6 py-7 md:px-8">

            <div className="absolute right-0 top-0 size-56 translate-x-16 -translate-y-20 rounded-full bg-blue-600/20 blur-3xl" />


            <div className="relative flex flex-col justify-between gap-6 md:flex-row md:items-center">

              <div className="flex items-center gap-4">

                <div className="flex size-15 shrink-0 items-center justify-center rounded-2xl border border-white/10 bg-white/10 text-lg font-semibold text-white">
                  {getInitials(
                    patient.name,
                  )}
                </div>


                <div>

                  <p className="text-xs font-medium text-blue-300">
                    Paciente #{patient.id}
                  </p>


                  <h1 className="mt-1 text-2xl font-semibold tracking-[-0.03em] text-white md:text-3xl">
                    {patient.name}
                  </h1>


                  <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-400">

                    <span>
                      {patient.sex}
                    </span>

                    <span>
                      Nascimento:{" "}
                      {formatDate(
                        patient.birth_date,
                      )}
                    </span>

                  </div>

                </div>

              </div>


              <div className="flex items-center gap-2 rounded-xl border border-emerald-400/20 bg-emerald-400/10 px-3.5 py-2 text-xs font-semibold text-emerald-300">

                <ShieldCheck className="size-4" />

                Assistência com validação humana

              </div>

            </div>

          </div>


          <div className="grid divide-y divide-slate-100 bg-white sm:grid-cols-3 sm:divide-x sm:divide-y-0">

            <div className="p-5">

              <div className="flex items-center justify-between">

                <p className="text-xs font-medium text-slate-400">
                  Última pressão
                </p>

                {latestBloodPressure && (
                  <BloodPressureBadge
                    systolic={
                      latestBloodPressure.systolic
                    }
                    diastolic={
                      latestBloodPressure.diastolic
                    }
                  />
                )}

              </div>


              <div className="mt-2 flex items-end gap-2">

                <span className="text-2xl font-semibold tracking-tight text-slate-900">
                  {latestBloodPressure
                    ? `${latestBloodPressure.systolic}/${latestBloodPressure.diastolic}`
                    : "—"}
                </span>

                {latestBloodPressure && (
                  <span className="pb-1 text-xs text-slate-400">
                    mmHg
                  </span>
                )}

              </div>

            </div>


            <div className="p-5">

              <p className="text-xs font-medium text-slate-400">
                Medicações ativas
              </p>

              <div className="mt-2 flex items-center gap-2">

                <p className="text-2xl font-semibold tracking-tight text-slate-900">
                  {activeMedications.length}
                </p>

                {activeMedications.length >
                  0 && (
                  <span className="rounded-full bg-emerald-50 px-2 py-1 text-[10px] font-semibold text-emerald-700">
                    Em prontuário
                  </span>
                )}

              </div>

            </div>


            <div className="p-5">

              <p className="text-xs font-medium text-slate-400">
                Exames pendentes
              </p>

              <div className="mt-2 flex items-center gap-2">

                <p
                  className={`
                    text-2xl
                    font-semibold
                    tracking-tight
                    ${
                      pendingExams.length >
                      0
                        ? "text-amber-600"
                        : "text-slate-900"
                    }
                  `}
                >
                  {pendingExams.length}
                </p>

                {pendingExams.length >
                  0 && (
                  <span className="rounded-full bg-amber-50 px-2 py-1 text-[10px] font-semibold text-amber-700">
                    Requer atenção
                  </span>
                )}

              </div>

            </div>

          </div>

        </section>


        <div className="mt-6 grid gap-6 xl:grid-cols-[1fr_390px]">

          <div className="space-y-6">

            <section className="grid gap-4 md:grid-cols-2">

              <div className="section-card p-5">

                <div className="mb-4 flex items-center gap-3">

                  <div className="flex size-9 items-center justify-center rounded-lg bg-violet-50">
                    <Stethoscope className="size-4 text-violet-600" />
                  </div>

                  <h2 className="section-title">
                    Histórico clínico
                  </h2>

                </div>


                <div className="space-y-3">

                  {patient.medical_history.length ===
                  0 ? (
                    <p className="text-sm text-slate-400">
                      Nenhuma condição registrada.
                    </p>
                  ) : (
                    patient.medical_history.map(
                      (
                        item,
                      ) => (
                        <div
                          key={
                            item.id
                          }
                          className="rounded-xl border border-slate-100 bg-slate-50 p-4"
                        >

                          <div className="flex items-start gap-3">

                            <div className="mt-0.5 flex size-6 shrink-0 items-center justify-center rounded-full bg-violet-100">
                              <Check className="size-3.5 text-violet-600" />
                            </div>


                            <div>

                              <p className="text-sm font-semibold text-slate-800">
                                {
                                  item.condition
                                }
                              </p>

                              {item.notes && (
                                <p className="mt-1 text-xs leading-5 text-slate-500">
                                  {
                                    item.notes
                                  }
                                </p>
                              )}

                            </div>

                          </div>

                        </div>
                      ),
                    )
                  )}

                </div>

              </div>


              <div className="section-card p-5">

                <div className="mb-4 flex items-center gap-3">

                  <div className="flex size-9 items-center justify-center rounded-lg bg-blue-50">
                    <Activity className="size-4 text-blue-600" />
                  </div>

                  <h2 className="section-title">
                    Pressão arterial
                  </h2>

                </div>


                <div className="space-y-2.5">

                  {patient.blood_pressure_measurements.map(
                    (
                      measurement,
                    ) => (
                      <div
                        key={
                          measurement.id
                        }
                        className="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50 px-4 py-3"
                      >

                        <div className="flex items-center gap-2 text-xs text-slate-500">

                          <CalendarDays className="size-3.5" />

                          {formatDate(
                            measurement.measured_at,
                          )}

                        </div>


                        <div className="flex items-center gap-3">

                          <div className="flex items-baseline gap-1">

                            <span className="text-sm font-semibold text-slate-800">
                              {
                                measurement.systolic
                              }
                              /
                              {
                                measurement.diastolic
                              }
                            </span>

                            <span className="text-[10px] text-slate-400">
                              mmHg
                            </span>

                          </div>


                          <BloodPressureBadge
                            systolic={
                              measurement.systolic
                            }
                            diastolic={
                              measurement.diastolic
                            }
                          />

                        </div>

                      </div>
                    ),
                  )}

                </div>

              </div>


              <div className="section-card p-5">

                <div className="mb-4 flex items-center gap-3">

                  <div className="flex size-9 items-center justify-center rounded-lg bg-emerald-50">
                    <Pill className="size-4 text-emerald-600" />
                  </div>

                  <h2 className="section-title">
                    Medicamentos
                  </h2>

                </div>


                <div className="space-y-3">

                  {patient.medications.map(
                    (
                      medication,
                    ) => (
                      <div
                        key={
                          medication.id
                        }
                        className="rounded-xl border border-slate-100 bg-slate-50 p-4"
                      >

                        <div className="flex items-start justify-between gap-3">

                          <div>

                            <p className="text-sm font-semibold text-slate-800">
                              {
                                medication.name
                              }
                            </p>

                            <p className="mt-1 text-xs text-slate-500">
                              {
                                medication.dosage
                              }
                              {" · "}
                              {
                                medication.frequency
                              }
                            </p>

                          </div>


                          <span
                            className={`
                              rounded-full
                              px-2
                              py-1
                              text-[10px]
                              font-semibold
                              ${
                                medication.active
                                  ? "bg-emerald-100 text-emerald-700"
                                  : "bg-slate-200 text-slate-500"
                              }
                            `}
                          >
                            {medication.active
                              ? "Ativo"
                              : "Inativo"}
                          </span>

                        </div>

                      </div>
                    ),
                  )}

                </div>

              </div>


              <div className="section-card p-5">

                <div className="mb-4 flex items-center gap-3">

                  <div className="flex size-9 items-center justify-center rounded-lg bg-amber-50">
                    <TestTube2 className="size-4 text-amber-600" />
                  </div>

                  <h2 className="section-title">
                    Exames laboratoriais
                  </h2>

                </div>


                <div className="space-y-3">

                  {patient.lab_exams.map(
                    (
                      exam,
                    ) => (
                      <div
                        key={
                          exam.id
                        }
                        className="rounded-xl border border-slate-100 bg-slate-50 p-4"
                      >

                        <div className="flex items-start justify-between gap-3">

                          <div>

                            <p className="text-sm font-semibold text-slate-800">
                              {
                                exam.exam_type
                              }
                            </p>

                            {exam.result && (
                              <p className="mt-1 text-xs text-slate-500">
                                Resultado:{" "}
                                {
                                  exam.result
                                }
                              </p>
                            )}

                            {exam.reference_range && (
                              <p className="mt-1 text-[11px] text-slate-400">
                                Referência:{" "}
                                {
                                  exam.reference_range
                                }
                              </p>
                            )}

                          </div>


                          <span
                            className={`
                              rounded-full
                              px-2
                              py-1
                              text-[10px]
                              font-semibold
                              ${
                                exam.status ===
                                "pending"
                                  ? "bg-amber-100 text-amber-700"
                                  : "bg-emerald-100 text-emerald-700"
                              }
                            `}
                          >
                            {exam.status ===
                            "pending"
                              ? "Pendente"
                              : exam.status}
                          </span>

                        </div>

                      </div>
                    ),
                  )}

                </div>

              </div>

            </section>


            <section className="section-card clinical-highlight overflow-hidden">

              <div className="border-b border-slate-100 bg-gradient-to-r from-blue-50/80 to-violet-50/70 px-6 py-5">

                <div className="flex items-center gap-3">

                  <div className="flex size-10 items-center justify-center rounded-xl bg-blue-600 shadow-md shadow-blue-600/15">
                    <Bot className="size-5 text-white" />
                  </div>


                  <div>

                    <div className="flex items-center gap-2">

                      <h2 className="text-base font-semibold text-slate-900">
                        Assistente clínico
                      </h2>

                      <span className="rounded-full border border-blue-200 bg-blue-100/70 px-2 py-0.5 text-[10px] font-semibold text-blue-700">
                        AI
                      </span>

                    </div>


                    <p className="mt-0.5 text-xs text-slate-500">
                      Prontuário + RAG + modelo customizado + guardrails.
                    </p>

                  </div>

                </div>

              </div>


              <div className="p-6">

                <textarea
                  value={
                    question
                  }
                  onChange={(
                    event,
                  ) =>
                    setQuestion(
                      event.target.value,
                    )
                  }
                  placeholder="Ex.: Analise a situação atual deste paciente e destaque os principais pontos de atenção."
                  className="min-h-32 w-full resize-none rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-blue-300 focus:bg-white focus:ring-4 focus:ring-blue-50"
                />


                <div className="mt-3 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">

                  <div className="flex items-center gap-2 text-[11px] text-slate-400">

                    <ShieldCheck className="size-3.5" />

                    Nenhuma decisão clínica é aplicada automaticamente.

                  </div>


                  <button
                    onClick={
                      handleAskAssistant
                    }
                    disabled={
                      loadingAssistant ||
                      !question.trim()
                    }
                    className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm shadow-blue-600/20 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                  >

                    {loadingAssistant ? (
                      <>
                        <LoaderCircle className="size-4 animate-spin" />
                        Analisando
                      </>
                    ) : (
                      <>
                        <Send className="size-4" />
                        Consultar assistente
                      </>
                    )}

                  </button>

                </div>


                {loadingAssistant && (
                  <div className="fade-up mt-6 rounded-2xl border border-blue-100 bg-blue-50/50 p-5">

                    <div className="flex items-center gap-3">

                      <div className="flex size-9 items-center justify-center rounded-xl bg-blue-100">
                        <Sparkles className="loading-dot size-4 text-blue-600" />
                      </div>


                      <div>

                        <p className="text-sm font-medium text-slate-700">
                          Processando contexto clínico
                        </p>

                        <p className="mt-0.5 text-xs text-slate-400">
                          Consultando dados, protocolos e validações de segurança...
                        </p>

                      </div>

                    </div>

                  </div>
                )}


                {assistantResponse &&
                  !loadingAssistant && (
                    <div className="fade-up mt-6 overflow-hidden rounded-2xl border border-slate-200">

                      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 bg-slate-50 px-5 py-3.5">

                        <div className="flex items-center gap-2">

                          <MessageSquareText className="size-4 text-blue-600" />

                          <span className="text-xs font-semibold text-slate-700">
                            Análise clínica
                          </span>

                        </div>


                        <div className="flex flex-wrap items-center gap-2">

                          <SafetyBadge
                            status={
                              assistantResponse.safety_status
                            }
                          />

                          <span className="rounded-full border border-slate-200 bg-white px-2.5 py-1 text-xs font-medium text-slate-500">
                            Audit #
                            {
                              assistantResponse.audit_log_id
                            }
                          </span>

                        </div>

                      </div>


                      <div className="markdown-response bg-white p-5">

                        <ReactMarkdown>
                          {
                            assistantResponse.response
                          }
                        </ReactMarkdown>

                      </div>


                      {assistantResponse.sources.length >
                        0 && (
                        <div className="border-t border-slate-100 bg-slate-50/60 px-5 py-4">

                          <div className="flex items-start gap-3">

                            <FileText className="mt-0.5 size-4 shrink-0 text-slate-400" />


                            <div>

                              <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-400">
                                Evidências recuperadas
                              </p>


                              <div className="mt-2 flex flex-wrap gap-2">

                                {assistantResponse.sources.map(
                                  (
                                    source,
                                  ) => (
                                    <span
                                      key={
                                        source
                                      }
                                      className="rounded-md border border-slate-200 bg-white px-2.5 py-1 font-mono text-[10px] text-slate-600"
                                    >
                                      {
                                        source
                                      }
                                    </span>
                                  ),
                                )}

                              </div>

                            </div>

                          </div>

                        </div>
                      )}

                    </div>
                  )}


                {error && (
                  <div className="mt-5 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">

                    <AlertCircle className="mt-0.5 size-4 shrink-0" />

                    {error}

                  </div>
                )}

              </div>

            </section>


            <section className="section-card p-6">

              <div className="mb-5 flex items-start justify-between">

                <div>

                  <div className="flex items-center gap-2">

                    <ClipboardCheck className="size-4.5 text-slate-500" />

                    <h2 className="text-base font-semibold text-slate-900">
                      Histórico de auditoria
                    </h2>

                  </div>


                  <p className="mt-1.5 text-xs text-slate-500">
                    Rastreabilidade das consultas realizadas pelo assistente.
                  </p>

                </div>


                <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-500">
                  {auditLogs.length}
                </span>

              </div>


              {auditLogs.length ===
              0 ? (
                <div className="rounded-2xl border border-dashed border-slate-200 py-10 text-center">

                  <FileClock className="mx-auto size-7 text-slate-300" />

                  <p className="mt-3 text-sm font-medium text-slate-500">
                    Nenhum registro de auditoria
                  </p>

                  <p className="mt-1 text-xs text-slate-400">
                    As consultas ao assistente aparecerão aqui.
                  </p>

                </div>
              ) : (
                <div className="space-y-3">

                  {auditLogs.map(
                    (
                      log,
                    ) => (
                      <AuditItem
                        key={
                          log.id
                        }
                        log={
                          log
                        }
                      />
                    ),
                  )}

                </div>
              )}

            </section>

          </div>


          <aside className="space-y-5">

            <section className="section-card p-5">

              <div className="flex items-center gap-3">

                <div className="flex size-9 items-center justify-center rounded-lg bg-blue-50">
                  <UserRound className="size-4 text-blue-600" />
                </div>

                <h2 className="section-title">
                  Dados do paciente
                </h2>

              </div>


              <div className="mt-5 divide-y divide-slate-100">

                <div className="flex justify-between gap-3 py-3 text-sm">

                  <span className="text-slate-400">
                    ID
                  </span>

                  <span className="font-medium text-slate-700">
                    #{patient.id}
                  </span>

                </div>


                <div className="flex justify-between gap-3 py-3 text-sm">

                  <span className="text-slate-400">
                    Sexo
                  </span>

                  <span className="font-medium text-slate-700">
                    {patient.sex}
                  </span>

                </div>


                <div className="flex justify-between gap-3 py-3 text-sm">

                  <span className="text-slate-400">
                    Peso
                  </span>

                  <span className="font-medium text-slate-700">
                    {patient.weight_kg ??
                      "—"}{" "}
                    {patient.weight_kg
                      ? "kg"
                      : ""}
                  </span>

                </div>


                <div className="flex justify-between gap-3 py-3 text-sm">

                  <span className="text-slate-400">
                    Altura
                  </span>

                  <span className="font-medium text-slate-700">
                    {patient.height_cm ??
                      "—"}{" "}
                    {patient.height_cm
                      ? "cm"
                      : ""}
                  </span>

                </div>

              </div>

            </section>


            <section className="overflow-hidden rounded-2xl border border-blue-100 bg-blue-50/70 p-5">

              <div className="flex items-center gap-2 text-blue-700">

                <ShieldCheck className="size-4" />

                <p className="text-sm font-semibold">
                  Segurança clínica
                </p>

              </div>


              <p className="mt-3 text-xs leading-5 text-blue-800/70">
                O sistema utiliza guardrails,
                fontes recuperadas e validação
                humana. Nenhuma sugestão
                substitui a decisão do
                profissional responsável.
              </p>


              <div className="mt-4 space-y-2">

                <div className="flex items-center gap-2 text-xs text-blue-800/70">
                  <Check className="size-3.5 text-blue-600" />
                  Prescrição automática bloqueada
                </div>

                <div className="flex items-center gap-2 text-xs text-blue-800/70">
                  <Check className="size-3.5 text-blue-600" />
                  Fontes rastreáveis
                </div>

                <div className="flex items-center gap-2 text-xs text-blue-800/70">
                  <Check className="size-3.5 text-blue-600" />
                  Auditoria de cada consulta
                </div>

              </div>

            </section>

          </aside>

        </div>

      </main>

    </div>
  );
}