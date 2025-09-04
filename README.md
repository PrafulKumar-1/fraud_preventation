# Project Suraksha: AI-Powered Investor Protection Toolkit

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/your-username/project-suraksha/main.yml?branch=main)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

[cite_start]**Project Suraksha** is an AI-powered, multi-modal fraud intelligence platform designed to enhance investor trust and market integrity in the Indian securities market[cite: 1, 175]. [cite_start]Its mission is to empower every retail investor with institutional-grade verification tools and provide regulators with a panoramic view of digital market risks[cite: 76].

[cite_start]The platform is built on a core principle of **"Verify, Then Trust"**—shifting the burden of verification from the individual investor to an automated, intelligent system that provides clear, actionable insights at the moment of decision-making[cite: 79, 80].

> [cite_start]**Note:** This project is designed to be fully developed and deployed on the cloud at **zero cost** by strategically leveraging the "always free" tiers of multiple cloud providers[cite: 178, 179].

---

## The Challenge: Asymmetric Risk in a Digital Market

[cite_start]The Indian securities market has seen a massive surge in retail investor participation, largely thanks to accessible digital platforms[cite: 4, 5]. [cite_start]However, these same channels are exploited by malicious actors using sophisticated technology to perpetrate scams at scale[cite: 7]. [cite_start]This creates an environment of **asymmetric risk**, where the complexity of fraudulent tactics often overwhelms the defenses of the average investor, leading to significant financial loss and an erosion of market trust[cite: 8].

[cite_start]Project Suraksha directly addresses this challenge with a suite of proactive, real-time prevention tools[cite: 172].

---

## Core Features

[cite_start]The platform's architecture is modular, consisting of two primary engines: the investor-facing **Authenticity Engine** and the regulator-focused **Market Intelligence Hub**[cite: 83].

### 🕵️ Authenticity Engine (For Investors)

[cite_start]This module is designed to combat impersonation and misinformation by providing on-demand verification services[cite: 85].

* [cite_start]**Advisor & Intermediary Verification**: Instantly verify the credentials of any individual or entity claiming to be a SEBI-Registered Investment Advisor (RIA), Research Analyst (RA), or other market intermediary against official SEBI databases[cite: 86, 87].
* [cite_start]**Media Authenticity Scanner**: Upload a suspicious video or audio file (or paste a URL) to scan it for tell-tale signs of AI-based manipulation and deepfakes[cite: 89, 90].
* [cite_start]**Document Integrity Check**: Upload a document (e.g., an IPO allotment letter or regulatory approval) to perform a forensic analysis, checking for metadata tampering, digital alterations, and other indicators of forgery[cite: 91, 92].

### 📈 Market Intelligence Hub (For Regulators)

[cite_start]This module is designed to detect coordinated manipulation and assess the credibility of market-moving information in real-time[cite: 94].

* [cite_start]**Social Media Anomaly Detection**: Correlates "social chatter" from platforms like Telegram and Twitter with real-time trading data (price and volume) to automatically flag patterns indicative of "pump-and-dump" schemes[cite: 96, 97].
* [cite_start]**Corporate Announcement Credibility Scoring**: Ingests all corporate announcements filed with the BSE/NSE and assigns a dynamic "Credibility Score" based on linguistic analysis, checks for promotional language, and cross-verification of claims against historical financial data[cite: 99, 101].

---

## 🛠️ Tech Stack & Architecture

[cite_start]The entire platform is architected around a **serverless-first, multi-cloud amalgamation strategy** to operate entirely within the free tiers of leading cloud providers[cite: 183, 193]. [cite_start]This "scale-to-zero" capability is the cornerstone of the no-cost deployment[cite: 186].

| Component | Primary Service | Key Function |
| --- | --- | --- |
| **Backend API** | [cite_start]**Render** (Web Service) [cite: 198] | [cite_start]Hosting the FastAPI Python application [cite: 198] |
| **Frontend App** | [cite_start]**Vercel** [cite: 202, 203] | [cite_start]Hosting the SvelteKit investor-facing UI [cite: 313] |
| **NoSQL Database** | [cite_start]**Google Firebase Firestore** [cite: 209] | [cite_start]Storing structured metadata (e.g., advisor details, alerts) [cite: 210, 262] |
| **Data Warehouse** | [cite_start]**Google BigQuery** [cite: 284] | [cite_start]Storing and querying market and social media data [cite: 284] |
| **Object Storage** | [cite_start]**Google Cloud Storage** [cite: 211] | [cite_start]Storing unstructured data (e.g., scraped files, text announcements) [cite: 212, 262, 294] |
| **Serverless Compute**| [cite_start]**Google Cloud Functions** [cite: 264] | [cite_start]Running automated data ingestion and ML scripts [cite: 264, 297] |
| **CI/CD Pipeline** | [cite_start]**GitHub Actions** [cite: 235] | [cite_start]Automating testing, building, and deployment [cite: 235] |
| **AI/ML Models** | [cite_start]**Hugging Face Transformers**, **TensorFlow** [cite: 359, 377] | [cite_start]Powering sentiment analysis and anomaly detection [cite: 359, 377] |

---

## 🚀 Getting Started (Local Development)

Follow these steps to set up and run the project on your local machine.

### Prerequisites

* [cite_start]**Git**: For version control[cite: 540].
* [cite_start]**Python 3.8+**: For the backend, scripts, and ML models[cite: 537].
* [cite_start]**Node.js (LTS)**: For the SvelteKit frontend[cite: 538].
* [cite_start]**Docker Desktop**: For containerizing the backend application[cite: 539].

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/project-suraksha.git](https://github.com/your-username/project-suraksha.git)
    cd project-suraksha
    ```

2.  **Configure Environment Variables:**
    The backend and scripts rely on environment variables. You will need to create `.env` files in the relevant directories (`backend/`, `scripts/`) and populate them with your API keys and configuration settings (e.g., `GCP_PROJECT_ID`, `ALPHA_VANTAGE_API_KEY`).

3.  **Set up the Backend:**
    ```bash
    cd backend
    pip install -r requirements.txt
    uvicorn app.main:app --reload
    ```
    The API will be running at `http://127.0.0.1:8000`.

4.  **Set up the Frontend:**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```
    The investor application will be available at `http://127.0.0.1:5173`.

---

## ☁️ Deployment

[cite_start]Deployment is fully automated using **GitHub Actions**[cite: 235]. [cite_start]The workflow defined in `.github/workflows/main.yml` is triggered on every push to the `main` branch[cite: 1658, 1659, 1660, 1661]. It performs the following actions:

1.  [cite_start]**Builds** a Docker container for the FastAPI backend and pushes it to a container registry[cite: 1676, 1677].
2.  [cite_start]**Triggers** a deploy hook on Render to pull the new backend image[cite: 1686].
3.  [cite_start]**Builds** the SvelteKit frontend application[cite: 1703].
4.  [cite_start]**Deploys** the static frontend assets to Vercel[cite: 1706].

---

## 📈 Phased Scaling Roadmap

[cite_start]While the platform is designed to be free, this blueprint includes a strategic path to scale it into a production-grade system as resources become available[cite: 493]. [cite_start]This roadmap prioritizes removing the most critical free-tier limitations first[cite: 496].

| Phase | Component to Upgrade | Reason for Upgrade / Risk Mitigated | Estimated Monthly Cost |
| :---: | --- | --- | :---: |
| **1** | **Relational Database** | [cite_start]Eliminates the 30-day data expiration risk, ensuring data persistence[cite: 1737]. | [cite_start]~$7 USD [cite: 1737] |
| **2** | **Backend API Compute** | [cite_start]Eliminates API cold starts, dramatically improves responsiveness[cite: 1737]. | [cite_start]~$7 USD [cite: 1737] |
| **3** | **Market & Social Data APIs** | [cite_start]Enables true near-real-time analysis by removing API call limits[cite: 1737]. | [cite_start]~$100 - $200+ USD [cite: 1737] |
| **4** | **Forensic Scanner APIs** | [cite_start]Increases capacity for deepfake/document analysis beyond free limits[cite: 1737]. | [cite_start]~$50 - $100+ USD [cite: 1737] |

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
