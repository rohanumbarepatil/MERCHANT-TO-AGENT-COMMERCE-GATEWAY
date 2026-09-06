"use client";

import { FormEvent, useState } from "react";

type Product = {
  id: string;
  name: string;
  price: number;
  currency?: string;
  category?: string;
  description?: string;
};

type AgentResponse = {
  success: boolean;
  intent?: string;
  query?: string;
  max_price?: number | null;
  count?: number;
  products?: Product[];
  selected_product?: Product;
  transaction?: {
    id: string;
    amount: number;
    status: string;
  };
  policy?: {
    name: string;
    requires_approval: boolean;
  };
  decision?: {
    decision: string;
    reason?: string;
    message?: string;
  };
  message?: string;
  response?: string;
};

export default function ChatPage() {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AgentResponse | null>(null);
  const [error, setError] = useState("");

  async function sendMessage(event: FormEvent) {
    event.preventDefault();

    if (!message.trim()) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/agent/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: message.trim(),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Something went wrong."
        );
      }

      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to connect to backend."
      );
    } finally {
      setLoading(false);
    }
  }

  const decision = result?.decision?.decision;

  const requiresApproval =
    decision === "APPROVAL_REQUIRED" &&
    Boolean(result?.transaction?.id);

  const isApproved = decision === "APPROVED";

  const isBlocked = decision === "BLOCKED";

  function openApprovalPage() {
    if (!result?.transaction?.id) return;

    window.location.href =
      `/approval?transaction_id=${result.transaction.id}`;
  }

  return (
    <main className="min-h-screen bg-[#f6f7f9]">

      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">

          <div>
            <a
              href="/"
              className="text-sm font-medium text-gray-500 transition hover:text-black"
            >
              ← Back to Gateway
            </a>

            <h1 className="mt-2 text-2xl font-semibold tracking-tight text-black">
              AI Shopping Agent
            </h1>

            <p className="mt-1 text-sm text-gray-500">
              Describe what you want. The agent will search,
              evaluate and validate the purchase.
            </p>
          </div>

          <div className="rounded-full border border-gray-200 bg-white px-4 py-2 text-sm">
            <span className="mr-2 inline-block h-2 w-2 rounded-full bg-green-500" />
            Agent Online
          </div>

        </div>
      </header>

      {/* Main */}
      <div className="mx-auto grid max-w-6xl gap-6 px-6 py-8 lg:grid-cols-[1fr_360px]">

        {/* Chat */}
        <section className="rounded-2xl border border-gray-200 bg-white shadow-sm">

          <div className="border-b border-gray-100 px-6 py-5">
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-gray-400">
              Natural Language Commerce
            </p>

            <h2 className="mt-2 text-lg font-semibold text-black">
              What are you looking for?
            </h2>
          </div>

          <div className="p-6">

            {/* Example */}
            <div className="rounded-xl bg-gray-50 p-5">
              <p className="text-xs font-medium uppercase tracking-wider text-gray-400">
                Try this
              </p>

              <button
                onClick={() =>
                  setMessage(
                    "Find me headphones under ₹3000 and buy the best one"
                  )
                }
                className="mt-3 text-left text-sm text-gray-700 transition hover:text-black"
              >
                “Find me headphones under ₹3000 and buy the best one”
              </button>

              <button
                onClick={() =>
                  setMessage("Buy me a laptop")
                }
                className="mt-2 block text-left text-sm text-gray-700 transition hover:text-black"
              >
                “Buy me a laptop”
              </button>
            </div>

            {/* Form */}
            <form
              onSubmit={sendMessage}
              className="mt-6"
            >
              <label className="mb-2 block text-sm font-medium text-gray-700">
                Your request
              </label>

              <textarea
                value={message}
                onChange={(event) =>
                  setMessage(event.target.value)
                }
                placeholder="Example: Buy me a laptop"
                rows={5}
                className="w-full resize-none rounded-xl border border-gray-300 px-4 py-3 text-sm outline-none transition focus:border-black focus:ring-2 focus:ring-black/10"
              />

              <button
                type="submit"
                disabled={
                  loading || !message.trim()
                }
                className="mt-4 w-full rounded-xl bg-black px-5 py-3 text-sm font-semibold text-white transition hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-40"
              >
                {loading
                  ? "Agent is thinking..."
                  : "Ask Agent →"}
              </button>
            </form>

            {/* Error */}
            {error && (
              <div className="mt-5 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                {error}
              </div>
            )}

            {/* Result */}
            {result && (
              <div className="mt-6">

                {/* Agent Response */}
                <div className="rounded-xl border border-gray-200 p-5">

                  <p className="text-xs font-medium uppercase tracking-wider text-gray-400">
                    Agent Response
                  </p>

                  <p className="mt-2 text-base font-medium text-gray-900">
                    {result.message ||
                      result.response ||
                      "Agent completed the request."}
                  </p>

                </div>

                {/* Selected Product */}
                {result.selected_product && (
                  <div className="mt-4 rounded-xl border border-gray-200 p-5">

                    <div className="flex items-start justify-between gap-4">

                      <div>
                        <p className="text-xs uppercase tracking-wider text-gray-400">
                          Recommended Product
                        </p>

                        <h3 className="mt-2 text-lg font-semibold text-black">
                          {result.selected_product.name}
                        </h3>

                        {result.selected_product.description && (
                          <p className="mt-1 text-sm leading-6 text-gray-500">
                            {result.selected_product.description}
                          </p>
                        )}
                      </div>

                      <p className="shrink-0 text-xl font-semibold text-black">
                        ₹
                        {Number(
                          result.selected_product.price
                        ).toLocaleString("en-IN")}
                      </p>

                    </div>

                  </div>
                )}

                {/* Policy */}
                {result.policy && (
                  <div className="mt-4 rounded-xl border border-gray-200 p-5">

                    <p className="text-xs uppercase tracking-wider text-gray-400">
                      Spending Policy
                    </p>

                    <div className="mt-3 flex items-center justify-between gap-4">

                      <p className="text-sm font-medium text-gray-800">
                        {result.policy.name}
                      </p>

                      <span
                        className={`rounded-full px-3 py-1 text-xs font-semibold ${
                          result.policy.requires_approval
                            ? "border border-yellow-200 bg-yellow-50 text-yellow-700"
                            : "border border-green-200 bg-green-50 text-green-700"
                        }`}
                      >
                        {result.policy.requires_approval
                          ? "Approval Required"
                          : "Auto Approved"}
                      </span>

                    </div>

                  </div>
                )}

                {/* Decision */}
                {decision && (
                  <div
                    className={`mt-4 rounded-xl border p-5 ${
                      isApproved
                        ? "border-green-200 bg-green-50"
                        : isBlocked
                          ? "border-red-200 bg-red-50"
                          : "border-yellow-200 bg-yellow-50"
                    }`}
                  >

                    <p className="text-xs font-medium uppercase tracking-wider opacity-60">
                      Policy Decision
                    </p>

                    <p className="mt-2 text-xl font-bold">
                      {isApproved
                        ? "✓ PURCHASE APPROVED"
                        : isBlocked
                          ? "✕ PURCHASE BLOCKED"
                          : "⚠ APPROVAL REQUIRED"}
                    </p>

                    {result.decision?.reason && (
                      <p className="mt-2 text-sm">
                        {result.decision.reason}
                      </p>
                    )}

                  </div>
                )}

                {/* Review & Approve */}
                {requiresApproval && (
                  <div className="mt-4 rounded-xl border border-yellow-200 bg-yellow-50 p-5">

                    <p className="text-sm font-semibold text-yellow-800">
                      Human authorization required
                    </p>

                    <p className="mt-1 text-sm leading-6 text-yellow-700">
                      This transaction cannot proceed to
                      payment until you explicitly authorize it.
                    </p>

                    <button
                      onClick={openApprovalPage}
                      className="mt-4 w-full rounded-xl bg-black px-5 py-3 text-sm font-semibold text-white transition hover:bg-gray-800"
                    >
                      Review & Approve →
                    </button>

                  </div>
                )}

              </div>
            )}

          </div>
        </section>

        {/* Agent Architecture */}
        <aside className="space-y-6">

          <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

            <p className="text-xs font-medium uppercase tracking-[0.18em] text-gray-400">
              Agent Pipeline
            </p>

            <div className="mt-5 space-y-3">

              {[
                "Understand Intent",
                "Search Products",
                "Recommend",
                "Validate Policy",
                "Authorize",
                "Execute Payment",
                "Audit",
              ].map((step, index) => (
                <div
                  key={step}
                  className="flex items-center gap-3 rounded-lg bg-gray-50 px-4 py-3"
                >

                  <span className="flex h-7 w-7 items-center justify-center rounded-full bg-black text-xs font-semibold text-white">
                    {index + 1}
                  </span>

                  <span className="text-sm font-medium text-gray-800">
                    {step}
                  </span>

                </div>
              ))}

            </div>
          </div>

          {/* Security */}
          <div className="rounded-2xl bg-black p-6 text-white">

            <p className="text-xs uppercase tracking-[0.18em] text-gray-400">
              Security Principle
            </p>

            <h3 className="mt-3 text-xl font-semibold leading-8">
              AI proposes.
              <br />
              Policy validates.
              <br />
              Human authorizes.
              <br />
              Payment executes.
            </h3>

            <p className="mt-4 text-sm leading-6 text-gray-400">
              The agent never receives unrestricted
              payment authority.
            </p>

          </div>

        </aside>

      </div>
    </main>
  );
}