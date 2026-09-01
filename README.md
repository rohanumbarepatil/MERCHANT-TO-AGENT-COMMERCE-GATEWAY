# Merchant-to-Agent Commerce Gateway

> **A permissioned commerce gateway that enables AI agents to discover products, reason over merchant data, and execute bounded payment actions safely.**

![Status](https://img.shields.io/badge/Status-In%20Development-yellow)
![Razorpay](https://img.shields.io/badge/Razorpay-AI%20Buildathon%202026-red)
![License](https://img.shields.io/badge/License-MIT-blue)

---

## Overview

**Merchant-to-Agent Commerce Gateway** is an agentic commerce platform designed for a future where AI agents can act as buyers on behalf of users.

Instead of requiring users to manually search products, compare merchants, evaluate policies, and complete every step of checkout, the system allows a user to express their requirements in natural language.

The AI Buyer Agent then:

1. Understands the user's intent.
2. Extracts purchase constraints.
3. Discovers relevant products.
4. Retrieves product and merchant information.
5. Compares eligible products.
6. Recommends the best match.
7. Generates a purchase proposal.
8. Validates the proposal against deterministic authorization policies.
9. Requests human approval when required.
10. Initiates a Razorpay Test Mode payment when authorized.
11. Verifies the payment through webhook events.
12. Records the complete transaction and decision trail.

The central principle is:

```text
AI proposes.
Policy validates.
Authorization gates.
Razorpay executes.
Webhook verifies.
Audit records.
```

---

# Problem Statement

## The Rise of Agentic Commerce

Traditional online commerce follows a familiar flow:

```text
Human
  ↓
Website
  ↓
Search
  ↓
Compare
  ↓
Checkout
  ↓
Payment
```

With AI agents, the interaction model is changing:

```text
Human
  ↓
AI Agent
  ↓
Product Discovery
  ↓
Decision
  ↓
Payment
```

This introduces a new financial and security problem.

If an AI agent is allowed to act on behalf of a user:

* How does the system understand what the user actually wants?
* How does it select the correct product?
* How does it verify price, inventory, delivery, and merchant policies?
* How much money should the agent be allowed to spend?
* Which categories or merchants should be permitted?
* When should human approval be required?
* What happens when the AI proposes an unsafe transaction?
* How can payment completion be independently verified?
* How can every important agent and financial decision be audited?

A normal chatbot does not solve these problems.

A recommendation engine does not solve these problems.

A traditional checkout system does not solve these problems.

What is needed is a **permissioned commerce layer between the AI agent and payment infrastructure.**

---

# Core Problem

> **How can AI agents perform useful commerce actions on behalf of users while ensuring that every financial action is explainable, bounded, authorized, verifiable, and auditable?**

Merchant-to-Agent Commerce Gateway addresses this problem by separating **AI reasoning** from **financial authorization**.

---

# Solution

The project introduces a controlled layer between an AI Buyer Agent and payment infrastructure.

The system combines:

* AI-powered intent understanding
* Agentic product discovery
* Semantic product retrieval
* Merchant information retrieval
* Product recommendation
* Deterministic policy enforcement
* Spending limits
* Human approval gates
* Razorpay Test Mode payments
* Payment webhook verification
* Transaction state management
* Audit logging
* Failure handling

The complete flow is:

```text
User Intent
    ↓
AI Buyer Agent
    ↓
Intent Extraction
    ↓
Product Discovery
    ↓
RAG / Semantic Retrieval
    ↓
Recommendation
    ↓
Purchase Proposal
    ↓
Policy Engine
    ↓
Authorization
    ↓
Razorpay Test Payment
    ↓
Webhook Verification
    ↓
Order Confirmation
    ↓
Audit Trail
```

This makes the system more than an AI shopping assistant.

It becomes a **permissioned agentic commerce gateway**.

---

# Example User Journey

A user says:

> "Find me black running shoes under ₹3,000, size 9, and delivery within 3 days."

The AI converts this natural-language request into structured constraints:

```json
{
  "category": "running shoes",
  "max_price": 3000,
  "color": "black",
  "size": "9",
  "max_delivery_days": 3
}
```

The system searches the merchant catalog and evaluates eligible products.

Example:

```text
Product A
Price: ₹2,499
Color: Black
Size: 9
Delivery: 2 days
Rating: 4.5

Product B
Price: ₹2,199
Color: Black
Size: 9
Delivery: 3 days
Rating: 4.2

Product C
Price: ₹2,799
Color: Blue
Size: 9
Delivery: 2 days
Rating: 4.6
```

Product C is rejected because the requested color is not satisfied.

The agent can recommend Product A based on overall constraint satisfaction.

Before payment, the purchase proposal is evaluated by the Policy Engine.

Example policy:

```json
{
  "max_transaction_amount": 3000,
  "require_confirmation_above": 2000,
  "max_transactions_per_session": 1,
  "allowed_categories": [
    "shoes",
    "electronics",
    "fashion"
  ]
}
```

Since the purchase amount is ₹2,499, the system can require explicit user approval.

After approval:

```text
Purchase Authorized
       ↓
Razorpay Test Mode
       ↓
Payment
       ↓
Webhook
       ↓
Verification
       ↓
Order Completed
       ↓
Audit Recorded
```

---

# Unsafe Purchase Scenario

Suppose the user requests a ₹7,500 product while the authorized spending limit is ₹3,000.

The AI may consider the product relevant, but the Policy Engine remains the final authority.

```text
AI Recommendation
       ↓
Purchase Proposal
       ↓
Policy Engine
       ↓
₹7,500 > ₹3,000
       ↓
BLOCKED
```

The system displays:

```text
Purchase blocked.

Reason:
The requested amount exceeds the authorized spending limit.

Authorized limit: ₹3,000
Requested amount: ₹7,500
```

The transaction is not sent to the payment layer.

The system records:

```text
Action: Purchase
Amount: ₹7,500
Decision: BLOCKED
Reason: POLICY_LIMIT
```

This demonstrates the core principle:

> **The AI can propose an action, but it cannot override financial policy.**

---

# Architecture Principle

The project follows:

```text
DETECT
   ↓
REASON
   ↓
DECIDE
   ↓
ACT SAFELY
   ↓
VERIFY
   ↓
MEASURE
```

The AI handles reasoning.

The deterministic policy layer handles financial authorization.

The payment provider handles payment execution.

The webhook layer verifies the payment state.

The audit system records the complete journey.

---

# AI Buyer Agent

The AI Buyer Agent is responsible for:

* Natural-language understanding
* Intent extraction
* Constraint extraction
* Product comparison
* Tool selection
* Product recommendation
* Purchase proposal generation
* Decision explanation

The agent does not receive unrestricted database or payment access.

Instead, it interacts through controlled tools.

Example tools:

```text
search_products()
get_product_details()
check_inventory()
search_merchant_policy()
recommend_products()
check_purchase_policy()
create_purchase_proposal()
request_human_approval()
create_payment()
get_payment_status()
record_audit_event()
```

Architecture:

```text
AI Agent
   ↓
Tool
   ↓
Permission Check
   ↓
Service
   ↓
Database / External API
```

---

# Product Discovery and RAG

The system combines deterministic filtering with semantic retrieval.

## Structured Filtering

Critical constraints such as:

```text
price <= ₹3,000
size = 9
color = black
delivery_days <= 3
inventory > 0
```

are validated using structured data.

## RAG

Semantic retrieval is used for questions such as:

> "Which headphones are better for workouts?"

or:

> "Which product has the better return policy?"

The RAG pipeline is:

```text
Product / Merchant Data
          ↓
      Text Creation
          ↓
       Embedding
          ↓
      pgvector
          ↓
     User Question
          ↓
       Embedding
          ↓
   Similarity Search
          ↓
Relevant Information
          ↓
      AI Agent
          ↓
       Response
```

Critical financial values such as price, inventory, spending limits, authorization state, and payment state are validated deterministically.

---

# Recommendation Engine

Eligible products are ranked using factors such as:

* Constraint satisfaction
* Price
* Feature match
* Delivery time
* Availability
* Rating
* Return policy
* Merchant reliability

Example:

```text
Product A

Constraint Match: 96%
Price: ₹2,499
Delivery: 2 days
Rating: 4.5
```

The system provides a concise decision rationale:

```text
Why this product?

✓ Within budget
✓ Correct size available
✓ Required color available
✓ Delivery requirement satisfied
✓ Return policy compatible
✓ Inventory available
```

The system exposes decision rationale without exposing private model chain-of-thought.

---

# Policy and Authorization Engine

The Policy Engine is the main financial safety layer.

Example:

```json
{
  "max_transaction_amount": 3000,
  "require_confirmation_above": 2000,
  "max_transactions_per_session": 1,
  "allowed_categories": [
    "electronics",
    "fashion",
    "shoes"
  ],
  "refund_permission": false
}
```

Possible policy decisions:

```text
ALLOW
BLOCK
REQUIRE_APPROVAL
```

### Example: Allowed

```text
Requested Amount = ₹1,200
Maximum Amount = ₹3,000

Decision = ALLOW
```

### Example: Blocked

```text
Requested Amount = ₹7,000
Maximum Amount = ₹3,000

Decision = BLOCK
```

### Example: Human Approval

```text
Requested Amount = ₹2,700
Auto Approval Limit = ₹2,000

Decision = REQUIRE_APPROVAL
```

---

# Human Approval

Higher-risk purchases can require explicit user approval.

Example:

```text
Purchase Request

Product:
Premium Running Shoes

Amount:
₹2,700

Policy:
Human approval required above ₹2,000
```

The user can choose:

```text
[ APPROVE PURCHASE ]

[ REJECT PURCHASE ]
```

Only after authorization can the payment workflow continue.

---

# Razorpay Payment Layer

Razorpay is used as the payment execution layer for the prototype.

The project uses **Razorpay Test Mode** so the complete payment lifecycle can be demonstrated without using real money.

Flow:

```text
Purchase Proposal
       ↓
Policy Validation
       ↓
Authorization
       ↓
Payment Request
       ↓
Razorpay Test Mode
       ↓
Payment Processing
       ↓
Webhook
       ↓
Backend Verification
       ↓
Order Confirmation
```

The implementation will follow the current official Razorpay API and webhook documentation available during development.

The project will not represent custom mock endpoints as official Razorpay APIs.

---

# Webhook Verification

A frontend payment-success message should not be treated as the only source of truth for payment completion.

Instead:

```text
Razorpay
   ↓
Webhook
   ↓
Backend
   ↓
Event Validation
   ↓
Payment State Update
   ↓
Order State Update
```

The system can maintain payment states such as:

```text
CREATED
AUTHORIZED
CAPTURED
FAILED
PENDING
UNKNOWN
```

The exact supported payment events and states will follow the Razorpay documentation used during implementation.

---

# Failure Handling

Agentic payment systems must be designed for failure.

## 1. Incorrect AI Price

AI:

```text
Product price = ₹2,499
```

Catalog:

```text
Actual price = ₹3,499
```

The deterministic catalog validation wins.

```text
LLM Proposal
     ↓
Catalog Validation
     ↓
Price Mismatch
     ↓
Reject Proposal
     ↓
No Payment
```

---

## 2. Delayed Webhook

If payment is initiated but confirmation has not arrived:

```text
Payment Initiated
      ↓
Webhook Pending
      ↓
Payment Status Check
      ↓
Confirmed?
   /       \
 YES       NO
 ↓          ↓
Complete   Pending / Review
```

The system does not blindly create a duplicate payment.

---

## 3. Policy Violation

```text
AI proposes ₹7,500
       ↓
Policy limit ₹3,000
       ↓
BLOCK
       ↓
Audit Event
```

No payment is initiated.

---

## 4. Inventory Change

A product may become unavailable between recommendation and payment.

The backend re-validates inventory before payment.

```text
Recommendation
      ↓
Inventory Validation
      ↓
Available?
 /       \
YES       NO
 ↓         ↓
Continue  Re-plan
```

---

# Audit Trail

Every important agent and financial action should be recorded.

Example:

```text
Session ID
Timestamp
User ID
Agent Action
Tool Used
Input
Output
Product
Amount
Policy Result
Authorization Result
Payment State
Webhook State
Final Result
```

Example timeline:

```text
22:10:02
USER_INTENT_RECEIVED

22:10:03
INTENT_PARSED

22:10:04
PRODUCT_SEARCH_COMPLETED

22:10:05
PRODUCT_RECOMMENDED

22:10:06
PURCHASE_PROPOSAL_CREATED

22:10:06
POLICY_CHECK = REQUIRE_APPROVAL

22:10:12
USER_APPROVED

22:10:14
PAYMENT_CREATED

22:10:25
WEBHOOK_RECEIVED

22:10:25
PAYMENT_VERIFIED

22:10:26
ORDER_COMPLETED
```

This provides a complete audit trail from user intent to payment outcome.

---

# Security Model

The system follows a least-privilege architecture.

## AI Permissions

| Action                       | Permission  |
| ---------------------------- | ----------- |
| Search products              | Allowed     |
| Read product details         | Allowed     |
| Compare products             | Allowed     |
| Read merchant policy         | Allowed     |
| Generate recommendation      | Allowed     |
| Generate purchase proposal   | Allowed     |
| Check purchase policy        | Allowed     |
| Execute unrestricted payment | Not Allowed |
| Override policy              | Not Allowed |
| Modify spending limit        | Not Allowed |
| Modify authorization rules   | Not Allowed |
| Execute unauthorized refund  | Not Allowed |

The AI cannot modify its own permissions.

---

# Critical Data Validation

Any value that can directly affect money should be validated outside the LLM.

Examples:

```text
Price
Inventory
Transaction Amount
Spending Limit
Allowed Category
Authorization State
Payment State
Order State
```

Therefore:

```text
LLM
 ↓
Proposal
 ↓
Deterministic Validation
 ↓
Policy
 ↓
Authorization
 ↓
Payment
```

---

# Environment and Secrets

Sensitive credentials must never be committed to GitHub.

Environment variables include:

```text
DATABASE_URL
RAZORPAY_KEY_ID
RAZORPAY_KEY_SECRET
RAZORPAY_WEBHOOK_SECRET
LLM_API_KEY
```

Secrets should remain inside:

```text
.env
```

The repository should only contain:

```text
.env.example
```

with empty placeholders.

Example:

```text
DATABASE_URL=
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
RAZORPAY_WEBHOOK_SECRET=
LLM_API_KEY=
```

---

# User Interface

The application will contain the following major views.

## AI Shopping Chat

```text
┌─────────────────────────────────┐
│       AI Shopping Agent         │
├─────────────────────────────────┤
│                                 │
│ You:                            │
│ Need shoes under ₹3000          │
│                                 │
│ AI: Searching products...       │
│                                 │
│ Recommended products            │
│                                 │
└─────────────────────────────────┘
```

## Product Comparison

```text
------------------------------------------------
Product       Price    Delivery    Match
------------------------------------------------
Product A     ₹2,499   2 days      96%
Product B     ₹2,199   3 days      91%
Product C     ₹2,799   2 days      84%
------------------------------------------------
```

## Authorization

```text
Agent Authorization

Maximum Spend:
₹3,000

Auto Approval Limit:
₹2,000

Allowed Categories:
✓ Shoes
✓ Electronics
✓ Fashion

Refund Authority:
Disabled
```

## Audit Dashboard

```text
Agent Activity

Total Sessions          128
Recommendations          94
Purchase Proposals       14
Approved                 11
Blocked                   2
Human Review              1
Unauthorized Actions      0
```

Actual metrics shown in the final application will be generated from real test/demo activity.

---

# End-to-End Architecture

```text
                         USER
                           │
                           ▼
                ┌─────────────────────┐
                │  Next.js Frontend   │
                │      Web App        │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   FastAPI Backend   │
                └──────────┬──────────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
       ┌──────────┐  ┌───────────┐  ┌───────────┐
       │ AI Agent │  │  Policy   │  │ Commerce  │
       │          │  │  Engine   │  │  Services │
       └────┬─────┘  └─────┬─────┘  └─────┬─────┘
            │              │              │
            └──────────────┼──────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │    Supabase     │
                  │ PostgreSQL      │
                  │ + pgvector      │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Razorpay Test   │
                  │     Mode        │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │    Webhooks     │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Audit & Events  │
                  └─────────────────┘
```

---

# End-to-End Transaction Flow

```text
1. User enters natural-language request
              ↓
2. AI extracts purchase constraints
              ↓
3. Catalog search
              ↓
4. Semantic / RAG retrieval
              ↓
5. Product filtering
              ↓
6. Product ranking
              ↓
7. AI recommendation
              ↓
8. Purchase proposal
              ↓
9. Deterministic policy validation
              ↓
10. Authorization decision
              ↓
      ┌───────┼────────┐
      ↓       ↓        ↓
    ALLOW   APPROVAL   BLOCK
      │       │        │
      │       ↓        └──→ Audit
      │    Human
      │    Decision
      │       │
      └───────┘
              ↓
11. Razorpay Test Payment
              ↓
12. Payment Event
              ↓
13. Webhook Received
              ↓
14. Backend Verification
              ↓
15. Order State Updated
              ↓
16. Audit Trail Finalized
              ↓
17. User Receives Final Result
```

---

# Technology Stack

| Layer               | Technology                       |
| ------------------- | -------------------------------- |
| Frontend            | Next.js + TypeScript             |
| UI                  | Tailwind CSS                     |
| Backend             | FastAPI + Python                 |
| AI                  | Free-tier LLM / Local fallback   |
| Agent               | Custom Python Agent Orchestrator |
| Embeddings          | sentence-transformers            |
| Vector Search       | PostgreSQL + pgvector            |
| Database            | Supabase PostgreSQL              |
| Payment             | Razorpay Test Mode               |
| Events              | Razorpay Webhooks                |
| Authentication      | Supabase Auth                    |
| Version Control     | GitHub                           |
| Frontend Deployment | Vercel                           |
| Backend Deployment  | Free-tier hosting / local demo   |
| Containerization    | Docker                           |
| Monitoring          | Logs + Audit Dashboard           |

---

# ₹0 Development Strategy

The MVP is designed to avoid mandatory infrastructure spending.

Potential free components:

```text
Next.js
    → Open Source

FastAPI
    → Open Source

Supabase
    → Free Tier

PostgreSQL + pgvector
    → Open Source

sentence-transformers
    → Local / Open Source

LLM
    → Free-tier Provider / Local Model

Razorpay
    → Test Mode

GitHub
    → Free Repository

Vercel
    → Free Deployment Tier
```

Free-tier limits and provider availability can change, so final deployment choices should be verified during implementation.

---

# Data Strategy

The prototype does not require a paid commercial product dataset.

Synthetic product and merchant data can be used.

Example product:

```json
{
  "product_id": "P001",
  "merchant_id": "M001",
  "name": "AeroRun X1",
  "category": "running shoes",
  "price": 2499,
  "color": "black",
  "sizes": [
    "8",
    "9",
    "10"
  ],
  "features": [
    "lightweight",
    "breathable",
    "running"
  ],
  "inventory": 24,
  "delivery_days": 2,
  "rating": 4.5
}
```

Example merchant:

```json
{
  "merchant_id": "M001",
  "name": "Demo Sports Store",
  "return_days": 7,
  "refund_available": true,
  "delivery_regions": [
    "India"
  ]
}
```

---

# Database Model

Core tables:

```text
users
merchants
products
product_embeddings
policies
agent_sessions
agent_actions
orders
payments
webhook_events
audit_logs
```

Relationship:

```text
User
 │
 ├── Policies
 │
 └── Agent Sessions
        │
        ├── Agent Actions
        │
        └── Order
             │
             └── Payment
                   │
                   └── Webhook Events

Merchant
 │
 └── Products
```

---

# Repository Structure

```text
merchant-to-agent-commerce-gateway/
│
├── frontend/
│   ├── app/
│   │   ├── chat/
│   │   ├── products/
│   │   ├── checkout/
│   │   ├── approval/
│   │   ├── policies/
│   │   ├── audit/
│   │   └── dashboard/
│   │
│   ├── components/
│   ├── lib/
│   ├── hooks/
│   ├── types/
│   └── styles/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── agents/
│   │   ├── ai/
│   │   ├── commerce/
│   │   ├── policy/
│   │   ├── payments/
│   │   ├── audit/
│   │   ├── database/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── utils/
│   │   └── config/
│   │
│   └── tests/
│       ├── unit/
│       ├── integration/
│       └── scenarios/
│
├── database/
│   ├── migrations/
│   ├── schema/
│   ├── seeds/
│   └── functions/
│
├── data/
│   ├── products/
│   ├── merchants/
│   ├── policies/
│   └── scenarios/
│
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── product/
│   ├── security/
│   └── demo/
│
├── scripts/
│   ├── data/
│   ├── development/
│   └── deployment/
│
├── .github/
│   └── workflows/
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── LICENSE
└── README.md
```

---

# API Concept

The backend will expose APIs around:

```text
POST /agent/chat
POST /agent/search
POST /agent/recommend
POST /agent/purchase

POST /policy/check

POST /payment/create
POST /webhooks/razorpay

GET /orders/{id}
GET /payments/{id}
GET /audit/{session_id}

GET /products
GET /merchants
GET /policies
```

The final API contract will be documented as implementation progresses.

---

# Testing Strategy

Testing covers normal, boundary, and failure scenarios.

## Unit Tests

```text
test_policy_allows_valid_transaction
test_policy_blocks_over_limit
test_policy_requires_approval
test_category_restriction
test_transaction_limit
```

## Integration Tests

```text
agent → catalog
agent → policy
policy → payment
payment → webhook
webhook → order
order → audit
```

## Scenario Tests

* Valid purchase
* Amount exceeds spending limit
* Human approval required
* Product unavailable
* Price changed after recommendation
* Payment failure
* Webhook delay
* Duplicate payment event
* Invalid policy request
* Unauthorized action attempt

---

# Buildathon Demo

## Demo 1: Successful Agentic Purchase

User:

> "Find me running shoes under ₹3,000, size 9, black, delivery within 3 days."

The system demonstrates:

```text
Intent understood
       ↓
Products discovered
       ↓
Products ranked
       ↓
Best product selected
       ↓
Decision explained
       ↓
Policy validated
       ↓
Authorization
       ↓
Razorpay Test Payment
       ↓
Webhook Confirmation
       ↓
Order Completed
       ↓
Audit Recorded
```

---

# Demo 2: Unsafe Purchase

User:

> "Buy this ₹7,500 premium shoe."

Policy:

```text
Maximum authorized amount = ₹3,000
```

System:

```text
Purchase Proposal
       ↓
Policy Check
       ↓
₹7,500 > ₹3,000
       ↓
BLOCKED
```

The system records the decision in the audit trail.

This demonstrates:

```text
Agentic AI
     +
Commerce
     +
Payments
     +
Authorization
     +
Safety
     +
Auditability
```

---

# Demo 3: Human Approval

Policy:

```text
Maximum Spend = ₹3,000
Auto Approval Limit = ₹2,000
```

AI proposes:

```text
₹2,700
```

Result:

```text
Within maximum spend
        +
Above auto-approval threshold
        ↓
Human Approval Required
```

The user explicitly approves or rejects the purchase.

---

# Demo 4: AI Hallucination Protection

AI proposes:

```text
Product Price = ₹2,499
```

Catalog service returns:

```text
Actual Price = ₹3,499
```

System:

```text
Price mismatch detected
        ↓
Purchase Proposal Rejected
        ↓
No Payment Created
        ↓
Audit Recorded
```

This demonstrates that:

> **The AI is useful, but it is not blindly trusted.**

---

# Demo 5: Payment Uncertainty

Payment is initiated, but the webhook is delayed.

The system does not blindly create another payment.

Instead:

```text
Payment Pending
      ↓
Verify Payment State
      ↓
Webhook / Provider Status
      ↓
Confirmed?
```

If confirmed:

```text
Order = COMPLETED
```

Otherwise:

```text
Order = PENDING / REVIEW
```

---

# Observability

The system tracks:

```text
Total Sessions
Product Searches
Recommendations
Purchase Proposals
Approved Transactions
Blocked Transactions
Human Approval Requests
Payment Success Rate
Payment Failure Rate
Webhook Processing
Policy Violations
```

Example dashboard:

```text
Agent Activity

Sessions                  128
Recommendations            94
Purchase Proposals         14
Approved                   11
Blocked                     2
Human Review                1
Unauthorized Actions        0
```

Final values will be generated from actual application activity.

---

# Project Goals

1. Demonstrate practical agentic AI.
2. Connect AI reasoning with commerce actions.
3. Introduce deterministic financial authorization.
4. Integrate Razorpay Test Mode.
5. Verify payment outcomes through webhooks.
6. Maintain an auditable decision trail.
7. Demonstrate graceful handling of unsafe actions.
8. Build the prototype with minimal infrastructure cost.
9. Provide a clear end-to-end user experience.
10. Demonstrate a safer model for agentic commerce.

---

# What Makes This Different?

A traditional AI chatbot:

```text
User
 ↓
LLM
 ↓
Response
```

A traditional recommendation engine:

```text
User
 ↓
Filters
 ↓
Recommendation
```

Merchant-to-Agent Commerce Gateway:

```text
User
 ↓
Intent
 ↓
AI Agent
 ↓
Product Discovery
 ↓
RAG
 ↓
Recommendation
 ↓
Purchase Proposal
 ↓
Policy Engine
 ↓
Authorization
 ↓
Payment
 ↓
Webhook Verification
 ↓
Audit
 ↓
Outcome
```

The system is therefore:

* Agentic
* Action-oriented
* Permissioned
* Payment-aware
* Auditable
* Failure-aware

---

# Why AI Is Necessary

AI is used where natural-language reasoning provides genuine value.

### Natural-Language Intent

Users can express requirements naturally instead of filling complex forms.

### Semantic Product Discovery

RAG can retrieve relevant information beyond simple keyword matching.

### Product Comparison

The agent can reason across multiple user constraints.

### Recommendation Explanation

The system can generate a concise explanation of why a product matches the user's request.

### Tool Orchestration

The agent can coordinate catalog, policy, payment, and verification tools.

However:

> **Financial authorization is not delegated to the LLM.**

---

# Fintech Relevance

The central fintech question is:

> **How should an AI agent be allowed to initiate financial actions on behalf of a user?**

The project addresses this through:

* Spending boundaries
* Transaction authorization
* Human approval
* Payment execution
* Payment verification
* Auditability
* Failure recovery
* Least-privilege permissions

The payment layer is therefore a core part of the system rather than an add-on.

---

# Razorpay Relevance

The project focuses on the intersection of:

```text
AI Agents
     +
Commerce
     +
Payments
```

The Growth-track direction identified for this project emphasizes enabling merchants to become accessible to AI buyers and exploring agentic commerce.

This project focuses on the controlled transaction layer required when AI agents move from recommendation to actual commerce actions.

The centerpiece is therefore an end-to-end transaction:

```text
Human Intent
      ↓
AI Buyer
      ↓
Merchant Discovery
      ↓
AI Reasoning
      ↓
Bounded Authorization
      ↓
Razorpay Payment
      ↓
Webhook Confirmation
      ↓
Audit Trail
```

---

# Value Proposition

## For Users

AI simplifies product discovery while preserving spending control.

## For Merchants

Products can become discoverable and actionable through AI-driven commerce experiences.

## For Payment Infrastructure

The system demonstrates how AI actions can be connected to payment infrastructure through explicit authorization boundaries.

## For Developers

The architecture provides a reusable pattern for building permissioned AI agents that interact with financial systems.

---

# Development Roadmap

## Phase 1: Repository Foundation

* Project skeleton
* GitHub repository
* Environment structure
* Frontend/backend separation

## Phase 2: Database

* Supabase setup
* Database schema
* Product tables
* Merchant tables
* Policy tables
* Audit tables

## Phase 3: Product Catalog

* Synthetic product dataset
* Merchant dataset
* Product search
* Filtering
* Inventory validation

## Phase 4: AI Layer

* LLM adapter
* Intent extraction
* Structured constraints
* Agent orchestrator

## Phase 5: RAG

* Embedding pipeline
* pgvector
* Product retrieval
* Merchant policy retrieval

## Phase 6: Recommendation

* Product ranking
* Constraint matching
* Recommendation explanation

## Phase 7: Policy Engine

* Spending limits
* Category restrictions
* Transaction limits
* Human approval
* Authorization states

## Phase 8: Payment

* Razorpay Test Mode
* Payment creation
* Payment state handling
* Payment verification

## Phase 9: Webhooks

* Webhook endpoint
* Event validation
* Order state updates
* Duplicate event handling

## Phase 10: Audit

* Agent actions
* Policy decisions
* Payment events
* Transaction timeline

## Phase 11: Frontend

* AI chat
* Product comparison
* Recommendation view
* Approval screen
* Policy screen
* Audit dashboard

## Phase 12: Testing

* Unit tests
* Integration tests
* Failure scenarios
* Security checks
* End-to-end transaction tests

## Phase 13: Deployment

* Frontend deployment
* Backend deployment
* Supabase configuration
* Razorpay webhook configuration
* Environment variables

## Phase 14: Buildathon Submission

* Final README
* Architecture diagram
* Demo video
* Screenshots
* Problem statement
* Solution explanation
* Technical documentation
* Testing results
* Final presentation

---

# Success Criteria

The MVP should demonstrate:

```text
Natural Language Request
        ↓
AI Understands Intent
        ↓
Relevant Products Found
        ↓
Best Product Recommended
        ↓
Decision Explained
        ↓
Policy Checked
        ↓
Transaction Authorized
        ↓
Razorpay Test Payment
        ↓
Webhook Confirmation
        ↓
Order Completed
        ↓
Audit Trail Generated
```

And:

```text
Unsafe Transaction
        ↓
Policy Violation
        ↓
Transaction Blocked
        ↓
No Unauthorized Payment
        ↓
Audit Recorded
```

---

# Definition of Done

* [ ] User can enter a natural-language shopping request.
* [ ] AI can extract structured requirements.
* [ ] Products can be searched.
* [ ] Product constraints can be validated.
* [ ] Relevant products can be ranked.
* [ ] AI can recommend a product.
* [ ] Recommendation rationale can be displayed.
* [ ] Purchase proposals can be generated.
* [ ] Policy rules can be evaluated.
* [ ] Spending limits are enforced.
* [ ] Human approval can be requested.
* [ ] Unauthorized purchases are blocked.
* [ ] Razorpay Test Mode payment can be initiated.
* [ ] Payment state can be verified.
* [ ] Razorpay webhook events can be processed.
* [ ] Orders can be updated from payment events.
* [ ] Audit events are recorded.
* [ ] Failure scenarios are handled.
* [ ] Secrets are protected.
* [ ] Project can run locally.
* [ ] Project can be deployed.
* [ ] End-to-end demo works.

---

# Future Extensions

The architecture can later support:

* Multiple merchant integrations
* Real merchant catalogs
* Merchant onboarding
* Merchant-specific policies
* User-specific spending policies
* Multi-agent purchasing
* Subscription management
* Recurring payment controls
* Refund authorization
* Fraud and risk scoring
* Identity verification
* Transaction anomaly detection
* Multi-currency support
* Cross-border commerce
* Agent reputation
* Merchant reputation
* Enterprise approval workflows
* Agent-to-agent commerce

---

# Project Philosophy

The project follows one core principle:

> **AI should have enough autonomy to be useful, but not enough unchecked authority to be dangerous.**

Therefore:

```text
AI
 ↓
Reason
 ↓
Propose
 ↓
Policy
 ↓
Authorize
 ↓
Execute
 ↓
Verify
 ↓
Audit
```

---

# One-Line Pitch

> **Merchant-to-Agent Commerce Gateway is a permissioned agentic commerce layer that lets AI buyers discover products and execute bounded Razorpay payments with deterministic authorization, webhook verification, and complete auditability.**

---

# Short Pitch

> **What if an AI agent could shop and pay on your behalf, but could never spend beyond the authority you gave it?**
>
> Merchant-to-Agent Commerce Gateway enables AI-driven product discovery and purchase execution while enforcing deterministic spending limits, approval gates, payment verification, and audit trails.

---

# Final Architecture Principle

```text
                  USER
                    │
                    ▼
             NATURAL LANGUAGE
                    │
                    ▼
              AI BUYER AGENT
                    │
                    ▼
            PRODUCT DISCOVERY
                    │
                    ▼
             RAG + RETRIEVAL
                    │
                    ▼
            RECOMMENDATION
                    │
                    ▼
          PURCHASE PROPOSAL
                    │
                    ▼
          ┌─────────────────┐
          │  POLICY ENGINE  │
          └────────┬────────┘
                   │
          ┌────────┼────────┐
          │        │        │
          ▼        ▼        ▼
       ALLOW    APPROVAL   BLOCK
          │        │
          │     HUMAN
          │     DECISION
          │        │
          └────────┘
                   │
                   ▼
          RAZORPAY TEST MODE
                   │
                   ▼
              WEBHOOK
                   │
                   ▼
             VERIFICATION
                   │
                   ▼
                 ORDER
                   │
                   ▼
              AUDIT TRAIL
```

---

# Conclusion

Merchant-to-Agent Commerce Gateway is built around a simple idea:

> **AI agents should be able to act, but financial actions must remain bounded, authorized, verifiable, and auditable.**

The project combines:

```text
AI
+
Agents
+
Commerce
+
RAG
+
Policy
+
Authorization
+
Razorpay
+
Webhooks
+
Auditability
```

Instead of building another AI chatbot, the project demonstrates a complete agentic commerce transaction from **human intent to verified payment outcome**.

The goal is not simply to make an AI that can purchase a product.

The goal is to build an AI commerce system that can:

```text
UNDERSTAND
    ↓
REASON
    ↓
PROPOSE
    ↓
BE BOUNDED
    ↓
GET AUTHORIZED
    ↓
PAY
    ↓
BE VERIFIED
    ↓
BE AUDITED
```

This forms the foundation for a safer and more controllable model of agentic commerce.
