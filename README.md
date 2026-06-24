# ❄️ Customer Support Ticket Intelligence System

### Snowflake Cortex + Streamlit in Snowflake

An end-to-end AI-powered customer support ticket intelligence platform built using Snowflake Cortex and Streamlit in Snowflake.

The system ingests raw customer support tickets, cleans and enriches the data, performs LLM-powered analysis using Snowflake Cortex, and surfaces actionable business insights through an interactive enterprise dashboard.

---

## 🎯 Project Overview

Traditional ticket analyzers focus primarily on sentiment detection and ticket categorization.

This project extends beyond basic analysis by leveraging Snowflake Cortex LLM capabilities to generate:

* Ticket Categorization
* Sentiment Analysis
* Business Impact Assessment
* Escalation Risk Detection
* Customer Churn Risk Prediction
* Resolution Complexity Estimation
* Team Routing Recommendations
* AI-Generated Ticket Summaries
* Suggested Agent Responses
* Manager Alert Scoring

The result is an intelligent support operations platform designed to help support managers prioritize critical issues, reduce customer churn, and improve operational efficiency.

---

# 🏗️ Pipeline Architecture

```text
Raw CSV Dataset
        ↓
RAW_TICKETS
(Raw Snowflake Table)
        ↓
RAW_TICKETS_CLEANED
(Data Cleaning & Placeholder Replacement)
        ↓
TICKET_SENTIMENT
(Cortex SENTIMENT())
        ↓
TICKET_CLASSIFICATION
(Cortex CLASSIFY_TEXT())
        ↓
TICKET_COMPLETE_RAW
(Cortex COMPLETE())
        ↓
TICKET_ANALYSIS_FINAL
(Fully Parsed Analytics Table)
        ↓
Streamlit in Snowflake Dashboard
```

---

# 📁 Project Structure

```text
snowflake-cortex-support-analyzer/
│
├── README.md
├── Snowflake_Setup.sql
├── Ticket_Analysis.sql
├── streamlit_app.py
├── pyproject.toml
├── snowflake.yml
│
└── .streamlit/
    └── config.toml
```

---

# 🤖 Snowflake Cortex Functions Used

| Function                           | Purpose                                             |
| ---------------------------------- | --------------------------------------------------- |
| `SNOWFLAKE.CORTEX.SENTIMENT()`     | Scores ticket sentiment from -1 to 1                |
| `SNOWFLAKE.CORTEX.CLASSIFY_TEXT()` | Classifies tickets into support categories          |
| `SNOWFLAKE.CORTEX.COMPLETE()`      | Generates structured AI-powered ticket intelligence |

---

# 📊 AI Ticket Intelligence Output

Each support ticket is analyzed and transformed into the following structured insights:

| Field                      | Description                                          |
| -------------------------- | ---------------------------------------------------- |
| Category                   | Billing, Technical Issue, Refund, Login, etc.        |
| Sentiment                  | Positive, Neutral, Negative                          |
| Urgency                    | Low, Medium, High, Critical                          |
| Business Impact Score      | Score between 0 and 100                              |
| Escalation Risk            | Low, Medium, High                                    |
| Churn Risk                 | Low, Medium, High                                    |
| Resolution Complexity      | Low, Medium, High                                    |
| Recommended Team           | Billing, Engineering, Tier 1, Tier 2, Security, etc. |
| AI Summary                 | One-sentence issue summary                           |
| Root Cause                 | Most likely root cause                               |
| Customer Frustration Level | Low, Medium, High                                    |
| Suggested Response         | AI-generated support response                        |
| Manager Alert Score        | Score between 0 and 100                              |

---

# 🚨 Unique Features

Unlike traditional support ticket analyzers, this project introduces business-focused intelligence metrics.

## Business Impact Score

Measures the potential operational and financial impact of a ticket.

Factors considered:

* Revenue impact
* Service disruption
* Security concerns
* Number of affected users
* Account access issues

---

## Churn Risk Prediction

Identifies customers who may discontinue product usage based on:

* Frustration level
* Repeated complaints
* Cancellation language
* Severity of issues

---

## Escalation Risk Detection

Predicts whether management or senior support intervention is likely required.

---

## Manager Alert Score

A composite score designed for support managers.

Calculated using:

* Business Impact
* Churn Risk
* Escalation Risk
* Ticket Urgency

Tickets scoring above 80 are automatically flagged for immediate attention.

---

# 📊 Dashboard Pages

## 📈 Overview

Provides a high-level operational view of support performance.

Features:

* Total Tickets
* Critical Tickets
* High Churn Risk Tickets
* Average Business Impact Score
* Average Manager Alert Score
* Sentiment Distribution
* Urgency Distribution
* Category Breakdown
* Team Routing Breakdown

---

## 🔍 Ticket Explorer

Interactive ticket investigation interface.

Features:

* Filter by Sentiment
* Filter by Urgency
* Filter by Churn Risk
* Filter by Recommended Team
* Color-Coded Ticket Cards
* AI Summary Display
* Root Cause Display
* Suggested Response Display

---

## 🚨 Manager Alerts

Displays only high-priority tickets.

Features:

* Manager Alert Score > 80
* Sorted by Alert Score
* Churn Risk Indicators
* Escalation Risk Indicators
* Critical Ticket Queue

---

# 🚀 How to Replicate

## Prerequisites

* Snowflake Account
* Snowflake Cortex Enabled
* Access to Cortex LLM Models
* Streamlit in Snowflake Enabled

Recommended model:

```sql
mistral-large2
```

---

## Step 1 — Setup Database

Run:

```sql
Snowflake_Setup.sql
```

This script:

* Creates database and schema
* Creates raw ticket tables
* Loads dataset
* Cleans placeholder values
* Creates intermediate tables

---

## Step 2 — Run AI Analysis

Run:

```sql
Ticket_Analysis.sql
```

This script:

* Performs sentiment analysis
* Performs ticket classification
* Executes Cortex COMPLETE()
* Parses JSON outputs
* Builds final analytics table

---

## Step 3 — Deploy Streamlit App

In Snowflake:

```text
Projects & Streams
    → Streamlit
        → Create App
```

Configuration:

```text
App Name:
CUSTOMER_SUPPORT_ANALYZER

Database:
CUSTOMER_SUPPORT_AI

Schema:
SUPPORT_ANALYZER
```

Paste:

```python
streamlit_app.py
```

Click:

```text
Run
```

---

# ⚠️ Cost Considerations

The original dataset contains:

```text
8,469 support tickets
```

For demonstration purposes, a subset of approximately:

```text
500 tickets
```

was processed through Cortex COMPLETE() to manage Snowflake credit consumption.

The architecture is fully scalable and capable of processing the complete dataset by increasing batch ranges in the analysis pipeline.

---

# 📦 Dataset

**Source:** Customer Support Ticket Dataset (Kaggle)

Dataset Size:

```text
8,469 tickets
```

Key Fields:

* Ticket ID
* Customer Name
* Customer Email
* Product Purchased
* Ticket Subject
* Ticket Description
* Ticket Status
* Ticket Priority
* Resolution
* Customer Satisfaction Rating

---

# 🛠️ Technology Stack

| Technology             | Purpose             |
| ---------------------- | ------------------- |
| Snowflake              | Data Warehouse      |
| Snowflake Cortex       | AI & LLM Inference  |
| SQL                    | Data Processing     |
| Streamlit in Snowflake | Dashboard UI        |
| Python                 | Application Logic   |
| Altair                 | Data Visualizations |


Built as a Snowflake Cortex portfolio project demonstrating the use of LLM-powered business intelligence directly within the Snowflake ecosystem.
