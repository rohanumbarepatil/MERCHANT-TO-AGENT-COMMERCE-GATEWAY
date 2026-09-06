"use client";

import Script from "next/script";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

const API_BASE = "http://127.0.0.1:8000";

type Transaction = {
  id: string;
  amount: number;
  currency: string;
  status: string;
  product_id: string;
};

type RazorpayOptions = {
  key: string;
  amount: number;
  currency: string;
  name: string;
  description: string;
  order_id: string;

  handler: (response: {
    razorpay_payment_id: string;
    razorpay_order_id: string;
    razorpay_signature: string;
  }) => void;

  prefill?: {
    name?: string;
    email?: string;
  };

  theme?: {
    color?: string;
  };
};

type RazorpayInstance = {
  open: () => void;
};

declare global {
  interface Window {
    Razorpay: new (
      options: RazorpayOptions
    ) => RazorpayInstance;
  }
}

type PaymentResponse = {
  success?: boolean;

  payment?: {
    payment_id?: string;
    order_id?: string;
    provider?: string;
    status?: string;
    amount?: number;
    currency?: string;
    key_id?: string;
    signature?: string;
  };

  transaction?: Transaction;
  message?: string;
};

export default function ApprovalPage() {
  const searchParams = useSearchParams();
  const transactionId = searchParams.get("transaction_id");

  const [transaction, setTransaction] =
    useState<Transaction | null>(null);

  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState("");

  const [payment, setPayment] =
    useState<PaymentResponse | null>(null);

  const [razorpayLoaded, setRazorpayLoaded] =
    useState(false);

  /*
   * Load transaction
   */
  useEffect(() => {
    if (!transactionId) {
      setError("Transaction ID is missing.");
      setLoading(false);
      return;
    }

    async function loadTransaction() {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(
          `${API_BASE}/api/transactions/${transactionId}`
        );

        if (!response.ok) {
          throw new Error("Transaction not found.");
        }

        const data = await response.json();

        setTransaction(data.transaction);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to load transaction."
        );
      } finally {
        setLoading(false);
      }
    }

    loadTransaction();
  }, [transactionId]);

  /*
   * Approve transaction
   */
  async function approveTransaction() {
    if (!transactionId) {
      setError("Transaction ID is missing.");
      return;
    }

    try {
      setActionLoading(true);
      setError("");

      const response = await fetch(
        `${API_BASE}/api/approvals/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            transaction_id: transactionId,
            approved_by: "user",
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Approval failed."
        );
      }

      setTransaction(data.transaction);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Approval failed."
      );
    } finally {
      setActionLoading(false);
    }
  }

  /*
   * Process Razorpay payment
   */
  async function processPayment() {
    if (!transactionId) {
      setError("Transaction ID is missing.");
      return;
    }

    if (!razorpayLoaded || !window.Razorpay) {
      setError(
        "Razorpay Checkout is still loading. Please try again."
      );
      return;
    }

    setActionLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API_BASE}/api/payments/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            transaction_id: transactionId,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Payment order creation failed."
        );
      }

      const paymentData = data.payment;

      if (
        !paymentData?.order_id ||
        !paymentData?.key_id
      ) {
        throw new Error(
          "Razorpay order information is incomplete."
        );
      }

      const options: RazorpayOptions = {
        key: paymentData.key_id,

        /*
         * Backend amount is in INR.
         * Razorpay Checkout expects paise.
         */
        amount: Math.round(
          Number(paymentData.amount) * 100
        ),

        currency:
          paymentData.currency || "INR",

        name:
          "Merchant-to-Agent Commerce Gateway",

        description:
          "AI Agent Purchase",

        order_id:
          paymentData.order_id,

        handler: async function (razorpayResponse) {
  try {
    setActionLoading(true);
    setError("");

    const verifyResponse = await fetch(
      `${API_BASE}/api/payments/verify`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          transaction_id: transactionId,
          razorpay_order_id:
            razorpayResponse.razorpay_order_id,
          razorpay_payment_id:
            razorpayResponse.razorpay_payment_id,
          razorpay_signature:
            razorpayResponse.razorpay_signature,
        }),
      }
    );

    const verifyData = await verifyResponse.json();

    if (!verifyResponse.ok) {
      throw new Error(
        verifyData.detail ||
          "Payment verification failed."
      );
    }

    // Update transaction state from backend
    setTransaction(
      verifyData.transaction
    );

    // Show verified payment
    setPayment({
      ...verifyData,
      payment: {
        ...verifyData.payment,
        payment_id:
          razorpayResponse.razorpay_payment_id,
        order_id:
          razorpayResponse.razorpay_order_id,
        signature:
          razorpayResponse.razorpay_signature,
        status: "verified",
      },
    });
  } catch (err) {
    setError(
      err instanceof Error
        ? err.message
        : "Payment verification failed."
    );
  } finally {
    setActionLoading(false);
  }
},

        prefill: {
          name: "Buildathon User",
          email: "user@example.com",
        },

        theme: {
          color: "#111111",
        },
      };

      const razorpay =
        new window.Razorpay(options);

      razorpay.open();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Payment initialization failed."
      );
    } finally {
      setActionLoading(false);
    }
  }

  /*
   * Loading state
   */
  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#f6f7f9]">
        <div className="text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-gray-300 border-t-black" />

          <p className="mt-4 text-sm text-gray-500">
            Loading transaction...
          </p>
        </div>
      </main>
    );
  }

  /*
   * Error without transaction
   */
  if (error && !transaction) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#f6f7f9] p-6">
        <div className="w-full max-w-lg rounded-2xl border border-red-200 bg-red-50 p-6">
          <h1 className="text-xl font-semibold text-red-700">
            Transaction Error
          </h1>

          <p className="mt-2 text-sm leading-6 text-red-600">
            {error}
          </p>

          <a
            href="/chat"
            className="mt-5 inline-flex rounded-xl bg-black px-5 py-3 text-sm font-semibold text-white transition hover:bg-gray-800"
          >
            ← Back to Agent
          </a>
        </div>
      </main>
    );
  }

  if (!transaction) {
    return null;
  }

  const amount = Number(
    transaction.amount
  );

  const status =
    transaction.status.toLowerCase();

  const isApprovalRequired =
    status === "approval_required";

  const isApproved =
    status === "approved";

  const isPaid =
    status === "paid";

  return (
    <>
      {/* =====================================================
          RAZORPAY CHECKOUT SCRIPT
      ====================================================== */}
      <Script
        src="https://checkout.razorpay.com/v1/checkout.js"
        strategy="afterInteractive"
        onLoad={() =>
          setRazorpayLoaded(true)
        }
        onError={() =>
          setError(
            "Failed to load Razorpay Checkout."
          )
        }
      />

      <main className="min-h-screen bg-[#f6f7f9]">
        {/* =====================================================
            HEADER
        ====================================================== */}
        <header className="border-b border-gray-200 bg-white">
          <div className="mx-auto max-w-6xl px-6 py-5">
            <a
              href="/chat"
              className="text-sm font-medium text-gray-500 transition hover:text-black"
            >
              ← Back to Agent
            </a>

            <div className="mt-5">
              {/* Approval Badge */}
              {isApprovalRequired && (
                <div className="inline-flex rounded-full border border-yellow-200 bg-yellow-50 px-3 py-1 text-xs font-semibold text-yellow-700">
                  HUMAN AUTHORIZATION REQUIRED
                </div>
              )}

              {/* Approved Badge */}
              {isApproved && (
                <div className="inline-flex rounded-full border border-green-200 bg-green-50 px-3 py-1 text-xs font-semibold text-green-700">
                  APPROVED — PAYMENT READY
                </div>
              )}

              {/* Paid Badge */}
              {isPaid && (
                <div className="inline-flex rounded-full border border-green-200 bg-green-50 px-3 py-1 text-xs font-semibold text-green-700">
                  PAYMENT COMPLETED
                </div>
              )}

              <h1 className="mt-3 text-3xl font-semibold tracking-tight text-black">
                Purchase Approval
              </h1>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-gray-500">
                The AI agent has proposed a purchase.
                Policy controls determine whether human
                authorization is required before payment
                execution.
              </p>
            </div>
          </div>
        </header>

        {/* =====================================================
            MAIN CONTENT
        ====================================================== */}
        <div className="mx-auto grid max-w-6xl gap-6 px-6 py-8 lg:grid-cols-[1.4fr_0.8fr]">
          {/* ===================================================
              LEFT — PURCHASE DETAILS
          ==================================================== */}
          <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
            {/* Transaction Header */}
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-wider text-gray-400">
                  Transaction
                </p>

                <p className="mt-1 break-all font-mono text-xs text-gray-500">
                  {transaction.id}
                </p>
              </div>

              {/* Status */}
              <span
                className={`shrink-0 rounded-full border px-3 py-1 text-xs font-semibold ${
                  isPaid
                    ? "border-green-200 bg-green-50 text-green-700"
                    : isApproved
                      ? "border-green-200 bg-green-50 text-green-700"
                      : "border-yellow-200 bg-yellow-50 text-yellow-700"
                }`}
              >
                {transaction.status.toUpperCase()}
              </span>
            </div>

            {/* AI Purchase Proposal */}
            <div className="mt-6 rounded-xl bg-gray-50 p-6">
              <p className="text-xs uppercase tracking-wider text-gray-400">
                AI Purchase Proposal
              </p>

              <h2 className="mt-2 text-2xl font-semibold text-black">
                Premium Laptop
              </h2>

              <p className="mt-1 text-sm leading-6 text-gray-500">
                Selected by the AI agent based on the
                purchase request.
              </p>

              <div className="mt-6 flex items-end justify-between">
                <div>
                  <p className="text-sm text-gray-500">
                    Purchase amount
                  </p>

                  <p className="mt-1 text-4xl font-bold tracking-tight text-black">
                    ₹{amount.toLocaleString("en-IN")}
                  </p>
                </div>

                <span className="text-sm font-medium text-gray-500">
                  {transaction.currency}
                </span>
              </div>
            </div>

            {/* =================================================
                VALIDATION
            ================================================== */}
            <div className="mt-6">
              <p className="text-sm font-semibold text-gray-800">
                Transaction Validation
              </p>

              <div className="mt-3 space-y-3">
                {/* Product */}
                <div className="flex items-center gap-3 rounded-xl border border-gray-100 bg-white p-4">
                  <span className="flex h-7 w-7 items-center justify-center rounded-full bg-green-100 text-sm font-bold text-green-700">
                    ✓
                  </span>

                  <div>
                    <p className="text-sm font-medium text-gray-800">
                      Product selected
                    </p>

                    <p className="text-xs text-gray-500">
                      AI agent selected the product for the
                      request.
                    </p>
                  </div>
                </div>

                {/* Policy */}
                <div className="flex items-center gap-3 rounded-xl border border-gray-100 bg-white p-4">
                  <span className="flex h-7 w-7 items-center justify-center rounded-full bg-green-100 text-sm font-bold text-green-700">
                    ✓
                  </span>

                  <div>
                    <p className="text-sm font-medium text-gray-800">
                      Spending policy evaluated
                    </p>

                    <p className="text-xs text-gray-500">
                      The purchase was evaluated by the
                      policy engine.
                    </p>
                  </div>
                </div>

                {/* Human Authorization */}
                <div
                  className={`flex items-center gap-3 rounded-xl border p-4 ${
                    isApprovalRequired
                      ? "border-yellow-100 bg-yellow-50"
                      : "border-green-100 bg-green-50"
                  }`}
                >
                  <span
                    className={`flex h-7 w-7 items-center justify-center rounded-full text-sm font-bold ${
                      isApprovalRequired
                        ? "bg-yellow-100 text-yellow-700"
                        : "bg-green-100 text-green-700"
                    }`}
                  >
                    {isApprovalRequired
                      ? "!"
                      : "✓"}
                  </span>

                  <div>
                    <p className="text-sm font-medium text-gray-800">
                      {isApprovalRequired
                        ? "Human approval required"
                        : "Human authorization recorded"}
                    </p>

                    <p className="text-xs text-gray-500">
                      {isApprovalRequired
                        ? "The AI agent cannot authorize this purchase."
                        : "The authorization step has been completed."}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* ===================================================
              RIGHT — AUTHORIZATION
          ==================================================== */}
          <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
            <p className="text-xs uppercase tracking-wider text-gray-400">
              Authorization
            </p>

            <h2 className="mt-2 text-2xl font-semibold text-black">
              {isApprovalRequired
                ? "You are in control"
                : isApproved
                  ? "Authorization complete"
                  : "Payment complete"}
            </h2>

            <p className="mt-3 text-sm leading-6 text-gray-500">
              {isApprovalRequired
                ? "The AI agent has proposed this transaction, but cannot authorize it. Your explicit approval is required."
                : isApproved
                  ? "Human authorization has been recorded. The transaction is now ready for payment execution."
                  : "The transaction has been successfully processed through the payment layer."}
            </p>

            {/* =================================================
                APPROVAL REQUIRED
            ================================================== */}
            {isApprovalRequired && (
              <div className="mt-8">
                <div className="rounded-xl border border-yellow-200 bg-yellow-50 p-4">
                  <p className="font-semibold text-yellow-800">
                    Approval Required
                  </p>

                  <p className="mt-1 text-sm leading-6 text-yellow-700">
                    This purchase is above the automatic
                    spending threshold and requires explicit
                    human authorization.
                  </p>
                </div>

                <button
                  onClick={approveTransaction}
                  disabled={actionLoading}
                  className="mt-4 w-full rounded-xl bg-black px-5 py-3 text-sm font-semibold text-white transition hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {actionLoading
                    ? "Recording Authorization..."
                    : "Approve Purchase"}
                </button>
              </div>
            )}

            {/* =================================================
                APPROVED — PAYMENT READY
            ================================================== */}
            {isApproved && !payment && (
              <div className="mt-8">
                <div className="rounded-xl border border-green-200 bg-green-50 p-4">
                  <p className="font-semibold text-green-700">
                    ✓ Transaction Approved
                  </p>

                  <p className="mt-1 text-sm leading-6 text-green-600">
                    Human authorization has been securely
                    recorded.
                  </p>
                </div>

                <button
                  onClick={processPayment}
                  disabled={
                    actionLoading ||
                    !razorpayLoaded
                  }
                  className="mt-4 w-full rounded-xl bg-green-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {actionLoading
                    ? "Creating Secure Checkout..."
                    : razorpayLoaded
                      ? "Proceed to Razorpay Payment"
                      : "Loading Razorpay..."}
                </button>
              </div>
            )}

            {/* =================================================
                PAYMENT SUBMITTED
            ================================================== */}
            {payment && (
              <div className="mt-8 rounded-xl border border-green-200 bg-green-50 p-5">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-600 text-white">
                    ✓
                  </div>

                  <div>
                    <p className="font-semibold text-green-700">
                      Payment Submitted
                    </p>

                    <p className="text-sm text-green-600">
                      Razorpay Checkout completed. Payment
                      verification is pending.
                    </p>
                  </div>
                </div>

                {/* Payment ID */}
                {payment.payment?.payment_id && (
                  <div className="mt-5 border-t border-green-200 pt-4">
                    <p className="text-xs uppercase tracking-wider text-green-600">
                      Payment ID
                    </p>

                    <p className="mt-1 break-all font-mono text-xs text-gray-700">
                      {payment.payment.payment_id}
                    </p>
                  </div>
                )}

                {/* Order ID */}
                {payment.payment?.order_id && (
                  <div className="mt-4">
                    <p className="text-xs uppercase tracking-wider text-green-600">
                      Razorpay Order ID
                    </p>

                    <p className="mt-1 break-all font-mono text-xs text-gray-700">
                      {payment.payment.order_id}
                    </p>
                  </div>
                )}

                {/* Provider */}
                {payment.payment?.provider && (
                  <div className="mt-4">
                    <p className="text-xs uppercase tracking-wider text-green-600">
                      Payment Provider
                    </p>

                    <p className="mt-1 text-sm font-medium text-gray-700">
                      {payment.payment.provider}
                    </p>
                  </div>
                )}

                {/* Payment Status */}
                {payment.payment?.status && (
                  <div className="mt-4">
                    <p className="text-xs uppercase tracking-wider text-green-600">
                      Payment Status
                    </p>

                    <p className="mt-1 text-sm font-medium text-green-700">
                      {payment.payment.status.toUpperCase()}
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* =================================================
                ERROR
            ================================================== */}
            {error && (
              <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4">
                <p className="text-sm leading-6 text-red-700">
                  {error}
                </p>
              </div>
            )}
          </section>
        </div>

        {/* =====================================================
            SECURITY PRINCIPLE
        ====================================================== */}
        <div className="mx-auto max-w-6xl px-6 pb-10">
          <section className="rounded-2xl bg-black p-6 text-white">
            <p className="text-xs uppercase tracking-[0.18em] text-gray-400">
              Security Principle
            </p>

            <h3 className="mt-3 text-xl font-semibold">
              AI proposes. Policy validates. Human authorizes.
              Payment executes.
            </h3>

            <div className="mt-5 grid gap-3 text-sm text-gray-400 md:grid-cols-4">
              <div>
                01 — AI Proposal
              </div>

              <div>
                02 — Policy Validation
              </div>

              <div>
                03 — Human Authorization
              </div>

              <div>
                04 — Payment Execution
              </div>
            </div>
          </section>
        </div>
      </main>
    </>
  );
}