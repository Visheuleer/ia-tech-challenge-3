"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import {
  Activity,
  ArrowRight,
  BrainCircuit,
  ChevronRight,
  ClipboardCheck,
  Database,
  HeartPulse,
  ShieldCheck,
  Sparkles,
  UserRound,
} from "lucide-react";

import { getPatients } from "@/lib/api";
import type { Patient } from "@/types/api";


function formatDate(
  value: string,
): string {
  return new Intl.DateTimeFormat(
    "pt-BR",
  ).format(
    new Date(
      `${value}T00:00:00`,
    ),
  );
}


export default function Home() {
  const [
    patients,
    setPatients,
  ] = useState<Patient[]>([]);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState<string | null>(null);


  useEffect(() => {
    async function loadPatients() {
      try {
        const data =
          await getPatients();

        setPatients(data);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Erro ao carregar pacientes.",
        );
      } finally {
        setLoading(false);
      }
    }

    loadPatients();
  }, []);


  return (
    <div className="app-shell">

      <header className="border-b border-slate-200/80 bg-white/85 backdrop-blur-xl">
        <div className="page-container flex h-18 items-center justify-between">

          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-xl bg-blue-600 shadow-sm shadow-blue-600/20">
              <HeartPulse
                className="size-5 text-white"
                strokeWidth={2.2}
              />
            </div>

            <div>
              <p className="leading-none text-[15px] font-semibold tracking-tight text-slate-900">
                Medical Assistant
              </p>

              <p className="mt-1 text-[11px] font-medium text-slate-400">
                Clinical Decision Support
              </p>
            </div>
          </div>


          <div className="hidden items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-700 sm:flex">
            <span className="size-1.5 rounded-full bg-emerald-500" />

            Sistema operacional
          </div>

        </div>
      </header>


      <main className="page-container pb-16 pt-10">

        <section className="relative overflow-hidden rounded-[28px] border border-slate-200 bg-slate-950 px-7 py-10 shadow-xl shadow-slate-900/5 md:px-11 md:py-12">

          <div className="absolute -right-24 -top-24 size-80 rounded-full bg-blue-600/20 blur-3xl" />

          <div className="absolute -bottom-32 left-1/3 size-72 rounded-full bg-cyan-500/10 blur-3xl" />


          <div className="relative max-w-3xl">

            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-blue-200">
              <Sparkles className="size-3.5" />

              Assistência clínica com IA
            </div>


            <h1 className="max-w-2xl text-3xl font-semibold tracking-[-0.04em] text-white md:text-5xl">
              Informação clínica estruturada,
              segura e rastreável.
            </h1>


            <p className="mt-5 max-w-2xl text-sm leading-7 text-slate-300 md:text-base">
              Apoio inteligente ao acompanhamento
              de pacientes com hipertensão,
              combinando dados clínicos,
              protocolos institucionais,
              fine-tuning e validação de segurança.
            </p>


            <div className="mt-8 flex flex-wrap gap-3">

              <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3.5 py-2 text-xs text-slate-200">
                <BrainCircuit className="size-4 text-blue-300" />

                QLoRA
              </div>

              <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3.5 py-2 text-xs text-slate-200">
                <Database className="size-4 text-cyan-300" />

                RAG clínico
              </div>

              <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3.5 py-2 text-xs text-slate-200">
                <ShieldCheck className="size-4 text-emerald-300" />

                Guardrails
              </div>

              <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3.5 py-2 text-xs text-slate-200">
                <ClipboardCheck className="size-4 text-violet-300" />

                Auditável
              </div>

            </div>

          </div>
        </section>


        <section className="mt-8 grid gap-4 md:grid-cols-3">

          <div className="section-card flex items-center gap-4 p-5">
            <div className="flex size-11 items-center justify-center rounded-xl bg-blue-50">
              <UserRound className="size-5 text-blue-600" />
            </div>

            <div>
              <p className="text-2xl font-semibold tracking-tight text-slate-900">
                {patients.length}
              </p>

              <p className="text-xs text-slate-500">
                Pacientes disponíveis
              </p>
            </div>
          </div>


          <div className="section-card flex items-center gap-4 p-5">
            <div className="flex size-11 items-center justify-center rounded-xl bg-emerald-50">
              <ShieldCheck className="size-5 text-emerald-600" />
            </div>

            <div>
              <p className="text-2xl font-semibold tracking-tight text-slate-900">
                Human-in-loop
              </p>

              <p className="text-xs text-slate-500">
                Validação profissional obrigatória
              </p>
            </div>
          </div>


          <div className="section-card flex items-center gap-4 p-5">
            <div className="flex size-11 items-center justify-center rounded-xl bg-violet-50">
              <Activity className="size-5 text-violet-600" />
            </div>

            <div>
              <p className="text-2xl font-semibold tracking-tight text-slate-900">
                Qwen + LoRA
              </p>

              <p className="text-xs text-slate-500">
                Modelo customizado
              </p>
            </div>
          </div>

        </section>


        <section className="mt-10">

          <div className="mb-5 flex items-end justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.15em] text-blue-600">
                Prontuários
              </p>

              <h2 className="mt-1 text-2xl font-semibold tracking-tight text-slate-900">
                Pacientes
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Selecione um paciente para visualizar
                o prontuário e acessar o assistente clínico.
              </p>
            </div>

            {!loading && (
              <span className="hidden text-xs text-slate-400 md:inline">
                {patients.length} registros
              </span>
            )}
          </div>


          {loading && (
            <div className="grid gap-4 md:grid-cols-3">
              {[1, 2, 3].map(
                (item) => (
                  <div
                    key={item}
                    className="section-card h-52 animate-pulse bg-white p-6"
                  >
                    <div className="size-11 rounded-xl bg-slate-100" />

                    <div className="mt-5 h-4 w-1/2 rounded bg-slate-100" />

                    <div className="mt-3 h-3 w-3/4 rounded bg-slate-100" />

                    <div className="mt-8 h-9 rounded-lg bg-slate-100" />
                  </div>
                ),
              )}
            </div>
          )}


          {error && (
            <div className="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">
              {error}
            </div>
          )}


          {!loading && !error && (
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">

              {patients.map(
                (patient) => (
                  <Link
                    key={patient.id}
                    href={`/patients/${patient.id}`}
                    className="group"
                  >
                    <article className="section-card relative h-full overflow-hidden p-6 transition-all duration-200 hover:-translate-y-1 hover:border-blue-200 hover:shadow-xl hover:shadow-slate-900/5">

                      <div className="absolute right-0 top-0 h-24 w-24 translate-x-8 -translate-y-8 rounded-full bg-blue-50 transition-transform duration-300 group-hover:scale-125" />


                      <div className="relative">

                        <div className="flex items-start justify-between">

                          <div className="flex size-11 items-center justify-center rounded-xl bg-slate-100 text-sm font-semibold text-slate-700">
                            {patient.name
                              .split(" ")
                              .slice(0, 2)
                              .map(
                                (name) =>
                                  name[0],
                              )
                              .join("")
                              .toUpperCase()}
                          </div>


                          <div className="flex size-9 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-400 transition group-hover:border-blue-200 group-hover:text-blue-600">
                            <ChevronRight className="size-4" />
                          </div>

                        </div>


                        <p className="mt-5 text-xs font-medium text-blue-600">
                          Paciente #{patient.id}
                        </p>


                        <h3 className="mt-1 text-lg font-semibold tracking-tight text-slate-900">
                          {patient.name}
                        </h3>


                        <div className="mt-5 space-y-2 text-sm text-slate-500">

                          <div className="flex justify-between border-b border-slate-100 pb-2">
                            <span>Sexo</span>

                            <span className="font-medium text-slate-700">
                              {patient.sex}
                            </span>
                          </div>


                          <div className="flex justify-between">
                            <span>Nascimento</span>

                            <span className="font-medium text-slate-700">
                              {formatDate(
                                patient.birth_date,
                              )}
                            </span>
                          </div>

                        </div>


                        <div className="mt-6 flex items-center gap-2 text-xs font-semibold text-blue-600">
                          Abrir prontuário

                          <ArrowRight className="size-3.5 transition-transform group-hover:translate-x-1" />
                        </div>

                      </div>
                    </article>
                  </Link>
                ),
              )}

            </div>
          )}

        </section>

      </main>
    </div>
  );
}