"use client";

import { useEffect, useState } from "react";

const modules = [
  {
    title: "AI Agent",
    description: "Understand intent and propose purchases",
    href: "/chat",
    icon: "✦",
  },
  {
    title: "Products",
    description: "Search and discover merchant products",
    href: "/products",
    icon: "◈",
  },
  {
    title: "Policies",
    description: "Control spending with deterministic rules",
    href: "/policies",
    icon: "◉",
  },
  {
    title: "Approvals",
    description: "Review actions requiring authorization",
    href: "/approval",
    icon: "✓",
  },
  {
    title: "Checkout",
    description: "Execute authorized commerce securely",
    href: "/checkout",
    icon: "↗",
  },
  {
    title: "Audit",
    description: "Track decisions and payment activity",
    href: "/audit",
    icon: "≡",
  },
];

export default function Home() {
  const [backendStatus, setBackendStatus] = useState("Checking...");
  const [currentTime, setCurrentTime] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/health")
      .then((response) => response.json())
      .then((data) => {
        setBackendStatus(data.status === "ok" ? "Operational" : data.status);
      })
      .catch(() => {
        setBackendStatus("Offline");
      });

    setCurrentTime(
      new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      })
    );
  }, []);

  return (
    <main className="min-h-screen bg-[#f7f8fa] text-[#171717]">
      {/* Top navigation */}
      <header className="border-b border-black/10 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-black text-lg font-bold text-white">
              M
            </div>

            <div>
              <p className="text-sm font-semibold tracking-tight">
                Merchant-to-Agent
              </p>
              <p className="text-xs text-black/50">Commerce Gateway</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden items-center gap-2 rounded-full border border-black/10 bg-[#fafafa] px-3 py-1.5 text-xs sm:flex">
              <span
                className={`h-2 w-2 rounded-full ${
                  backendStatus === "Operational"
                    ? "bg-green-500"
                    : "bg-red-500"
                }`}
              />
              Backend {backendStatus}
            </div>

            <a
              href="http://127.0.0.1:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="rounded-lg border border-black/10 px-3 py-2 text-xs font-medium transition hover:bg-black hover:text-white"
            >
              API Docs
            </a>
          </div>
        </div>
      </header>

      {/* Main */}
      <div className="mx-auto max-w-7xl px-6 py-8 lg:px-8">
        {/* Hero */}
        <section className="relative overflow-hidden rounded-3xl bg-black px-7 py-10 text-white shadow-sm md:px-10 md:py-14">
          <div className="relative z-10 max-w-3xl">
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-xs text-white/80 backdrop-blur">
              <span className="h-1.5 w-1.5 rounded-full bg-green-400" />
              Permissioned Agentic Commerce
            </div>

            <h1 className="text-4xl font-semibold tracking-tight md:text-6xl">
              AI can propose.
              <br />
              <span className="text-white/45">You stay in control.</span>
            </h1>

            <p className="mt-5 max-w-2xl text-sm leading-6 text-white/65 md:text-base">
              A secure commerce gateway where AI discovers products and
              proposes purchases, while policies and authorization control
              every payment action.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <a
                href="/chat"
                className="rounded-xl bg-white px-5 py-3 text-sm font-semibold text-black transition hover:bg-white/85"
              >
                Start AI Shopping →
              </a>

              <a
                href="/policies"
                className="rounded-xl border border-white/20 bg-white/5 px-5 py-3 text-sm font-medium text-white transition hover:bg-white/10"
              >
                View Policies
              </a>
            </div>
          </div>

          {/* Decorative element */}
          <div className="absolute -right-20 -top-20 h-72 w-72 rounded-full border border-white/10" />
          <div className="absolute -right-8 -top-8 h-48 w-48 rounded-full border border-white/10" />
          <div className="absolute bottom-0 right-10 hidden text-[120px] font-black leading-none text-white/[0.035] lg:block">
            AI
          </div>
        </section>

        {/* System status */}
        <section className="mt-6 grid gap-4 md:grid-cols-3">
          <StatusCard
            label="Gateway"
            value="Operational"
            detail="Commerce layer ready"
            active
          />

          <StatusCard
            label="Policy Engine"
            value="Enforced"
            detail="Authorization before payment"
            active
          />

          <StatusCard
            label="Backend"
            value={backendStatus}
            detail={
              currentTime
                ? `Last checked ${currentTime}`
                : "Checking connection..."
            }
            active={backendStatus === "Operational"}
          />
        </section>

        {/* Architecture */}
        <section className="mt-10">
          <div className="mb-5">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-black/40">
              Core architecture
            </p>
            <h2 className="mt-1 text-2xl font-semibold tracking-tight">
              AI proposes. Policy validates. Authorization controls.
            </h2>
          </div>

          <div className="grid gap-3 md:grid-cols-5">
            <FlowStep number="01" title="Intent" text="Understand request" />
            <FlowArrow />
            <FlowStep number="02" title="Recommend" text="Find products" />
            <FlowArrow />
            <FlowStep number="03" title="Policy" text="Validate spend" />
          </div>

          <div className="mt-3 grid gap-3 md:grid-cols-5">
            <FlowStep number="04" title="Authorize" text="Control payment" />
            <FlowArrow />
            <FlowStep number="05" title="Execute" text="Process payment" />
            <FlowArrow />
            <FlowStep number="06" title="Audit" text="Record outcome" />
          </div>
        </section>

        {/* Modules */}
        <section className="mt-12">
          <div className="mb-5 flex items-end justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-black/40">
                Gateway modules
              </p>
              <h2 className="mt-1 text-2xl font-semibold tracking-tight">
                Control center
              </h2>
            </div>

            <span className="hidden text-xs text-black/40 md:block">
              6 active modules
            </span>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {modules.map((module) => (
              <a
                key={module.title}
                href={module.href}
                className="group rounded-2xl border border-black/10 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-black/20 hover:shadow-md"
              >
                <div className="flex items-start justify-between">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-black text-sm text-white">
                    {module.icon}
                  </div>

                  <span className="text-black/25 transition group-hover:text-black">
                    ↗
                  </span>
                </div>

                <h3 className="mt-5 text-base font-semibold">
                  {module.title}
                </h3>

                <p className="mt-1 text-sm leading-5 text-black/50">
                  {module.description}
                </p>
              </a>
            ))}
          </div>
        </section>

        {/* Security principle */}
        <section className="mt-12 rounded-2xl border border-black/10 bg-white p-6 md:p-8">
          <div className="grid gap-8 md:grid-cols-[1fr_auto] md:items-center">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-black/40">
                Security principle
              </p>

              <h2 className="mt-2 text-xl font-semibold tracking-tight">
                AI never gets unrestricted payment authority.
              </h2>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-black/50">
                The agent can recommend an action, but deterministic policy
                checks and explicit authorization sit between the AI decision
                and payment execution.
              </p>
            </div>

            <div className="rounded-xl bg-[#f5f5f5] px-5 py-4 text-center">
              <p className="text-xs text-black/40">Design principle</p>
              <p className="mt-1 text-sm font-semibold">
                AI ≠ Payment Authority
              </p>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="flex flex-col gap-2 py-8 text-xs text-black/35 md:flex-row md:items-center md:justify-between">
          <p>Merchant-to-Agent Commerce Gateway</p>
          <p>Razorpay AI Buildathon • Local Development</p>
        </footer>
      </div>
    </main>
  );
}

function StatusCard({
  label,
  value,
  detail,
  active,
}: {
  label: string;
  value: string;
  detail: string;
  active: boolean;
}) {
  return (
    <div className="rounded-2xl border border-black/10 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium uppercase tracking-wider text-black/40">
          {label}
        </p>

        <span
          className={`h-2.5 w-2.5 rounded-full ${
            active ? "bg-green-500" : "bg-red-500"
          }`}
        />
      </div>

      <p className="mt-3 text-xl font-semibold">{value}</p>
      <p className="mt-1 text-xs text-black/45">{detail}</p>
    </div>
  );
}

function FlowStep({
  number,
  title,
  text,
}: {
  number: string;
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-2xl border border-black/10 bg-white p-5">
      <p className="text-xs font-semibold text-black/25">{number}</p>
      <p className="mt-3 text-sm font-semibold">{title}</p>
      <p className="mt-1 text-xs text-black/45">{text}</p>
    </div>
  );
}

function FlowArrow() {
  return (
    <div className="hidden items-center justify-center text-black/20 md:flex">
      →
    </div>
  );
}