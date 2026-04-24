# Emerald ITR Pro 💎: The Honest Taxpayer's ERP

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GPLv3-green.svg)](LICENSE)
[![Compliance](https://img.shields.io/badge/Compliance-AY_2026--27-orange.svg)]()
[![AI](https://img.shields.io/badge/AI-Local_LLM-purple.svg)]()

> "Because tax filing shouldn't feel like a punishment for being honest."

Hey there! If you're reading this, you probably know the pain of filing taxes in India. Every year, it feels like a toss-up between paying hefty fees for commercial tax software that treats your data like a product, or fighting with the government's official offline utility that feels like it was built in 1998 and is just waiting for an excuse to crash.

I got tired of it. So I built **Emerald ITR Pro**.

This isn't a corporate project. It's a personal mission to build a desktop tax utility for the **Assessment Year 2026-27 (FY 2025-26)** that is actually pleasant to use, heavily automated, and most importantly, respects your privacy. It gives you the smooth, modern experience of web-based platforms but keeps all your sensitive financial data locked away safely on your own hard drive.

## 🚀 Pro Features (Why use this instead of the official utility?)

If you've ever tried to figure out exactly how the 234A/B/C interest penalties are calculated, or felt the panic of accidentally selecting the wrong ITR form, you'll know why I made this. Here is what I focused on fixing:

### 🪄 The ITR Wizard
Don't know if you need ITR-1, 2, 3, or 4? Just answer a few plain-English questions about your income for the year. The app figures out the right form and configures the dashboard automatically. No more guessing.

### 📑 Multi-Source Ingestion
Stop manual entry. Emerald features a modernized parsing engine that handles:
- **Form 16**: Direct extraction of Salary, TAN, and TDS details.
- **Form 26AS**: Annual TDS statement reconciliation.
- **AIS/TIS**: Automatic ingestion of the Annual Information Statement (AIS).

### 🔍 Side-by-Side AIS Auditor
One of the biggest headaches is matching your records with the Annual Information Statement (AIS). Drop your AIS JSON into Emerald, and it will give you a side-by-side comparison with what you've entered. If the government thinks you made ₹50,000 in interest and you only reported ₹48,000, it flags the mismatch instantly.

### 🔢 FY 2025-26 / AY 2026-27 Calculation Engine
Emerald is fully updated for the latest tax regime changes:
- **Standard Deduction**: ₹75,000 under the new tax regime.
- **Rebate (Sec 87A)**: ₹60,000 maximum rebate for income up to ₹12L.
- **New Tax Slabs**: 0-4L (0%), 4-8L (5%), 8-12L (10%), 12-16L (15%), 16-20L (20%), 20-24L (25%), above 24L (30%).
- **Capital Gains**: 12.5% LTCG rate (Sec 112A/112) and 20% STCG rate on equity.
- **VDA Tax**: 30% flat rate on Virtual Digital Assets (crypto).

### 📉 Automatic Statutory Interest Engine
Doing the math for advance tax installments and interest under sections 234A/234B/234C is brutal. This app buckets your payments and handles the entire calculation engine automatically:
- **Section 234A**: 1% per month for delayed filing.
- **Section 234B**: 1% per month for advance tax shortfall.
- **Section 234C**: 1% per month for deferred advance tax installments.

## 🤖 AI-Powered Intelligence (New!)

Emerald now features a local AI assistant that acts as your personal tax consultant and data entry clerk:

- **Smart Document Extraction**: Upload your Form 16, 26AS, or AIS, and let the AI extract complex data points automatically.
- **Tax Advisory**: The AI reviews your tax return and provides proactive suggestions to avoid common errors or optimize disclosures.
- **Document Classification**: Simply drop a file, and the AI automatically detects its type.
- **100% Local & Private**: All AI processing happens on your machine using the **Phi-4-mini** model. Your financial data never leaves your computer.
- **Hardware Adaptive**: Automatically scales performance (Eco, Standard, and Pro modes) based on your system RAM.

## 💎 Production Hardening (v1.0 Update)

The codebase has undergone a comprehensive production-grade hardening process for the AY 2026-27 filing cycle:
- **Tax Engine Verification**: All rates, slabs, and thresholds verified against authoritative sources.
- **Architectural Hardening**: Decoupled core tax logic from the UI using the `StateRegistry` for absolute visual consistency.
- **Navigation & UX**: Finalized the dynamic sidebar stepper and real-time validation feedback.

## 📅 New Tax Regime Compliance (AY 2026-27)

To keep things clean and idiot-proof, this engine is built exclusively for the **New Tax Regime (Section 115BAC)** for FY 2025-26. 

**Deductions NOT Allowed (Correctly Flagged):**
- Section 80C (PF, ELSS, LIC) | Section 80D (Health Insurance)
- HRA Exemption | LTA (Leave Travel Allowance)
- Section 24(b) home loan interest on self-occupied property.

## 🧩 Comprehensive ITR Support
Emerald supports a wide range of filing scenarios:
- **ITR-1 (Sahaj)**: For individuals with salary and single house property.
- **ITR-2**: For capital gains, multiple house properties, and foreign assets.
- **ITR-3**: For individuals/HUFs with business or professional income.
- **ITR-4 (Sugam)**: For presumptive income under Section 44AD/44ADA.

## 🛡️ Privacy & Offline Architecture
- **Zero Cloud**: 100% offline. No accounts. No tracking. No telemetry.

## 🛠 Tech Stack & Architecture
- **CustomTkinter**: Modern, high-DPI UI framework.
- **llama-cpp-python**: Local LLM inference engine.
- **TaxService**: ~300 lines of hardened tax calculation logic.
- **DeductionService**: Real-time rule checking against New Tax Regime constraints.

## 📋 Installation

1. **Clone the Repo**:
   ```bash
   git clone https://github.com/your-username/emerald-itr-pro.git
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **(Optional) AI Setup**: Download Phi-4-mini GGUF to the `models/` folder and enable AI in Settings.
4. **Launch**: `python main.py` or double-click `run_app.bat`.

---
*Built with ❤️ for the Indian Tax Community.*
