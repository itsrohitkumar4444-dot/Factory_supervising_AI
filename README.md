# 🏭 Shadow Floor Engineer

The **Shadow Floor Engineer** is an AI agent running locally for a specific manufacturing facility. It functions as a conversational interface for factory floor shift leads and technicians to troubleshoot complex machinery errors using hyper-specific "Tribal Knowledge" rather than blindly relying on generic manual diagnostic sheets. 

It leverages **Groq** (for fast `gpt-oss-120b-cloud` inference) and **Hindsight Cloud (Vectorize.io)** to maintain a continuous, evolving long-term memory graph in the cloud.

---

## 🛠️ Tech Stack
- **Backend**: Flask (Python) with CORS
- **LLM Engine**: Groq Cloud API
- **Memory/Vector DB**: Hindsight Global Memory API (`factory1` bank)
- **Frontend**: Lightweight HTML/Vanilla JS with CSS Glassmorphism 

---

## 🚀 Setup & Execution

### 1. Requirements
Ensure you have Python 3.9+ installed.
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Secrets
Create a `.env` file in the root directory mirroring the following setup:
```
HINDSIGHT_API_KEY="hsk_...your_hindsight_key..."
GROQ_API_KEY="gsk_...your_groq_key..."
```

*(Note: Never push your `.env` to GitHub! It is ignored by the `.gitignore` setup.)*

### 3. Initialize Hindsight Graph (First-Time Only)
If you have just stood up the `factory1` memory bank, run the ingestion script to populate it with critical operational data (e.g., Robot Arms, Paint Sprayers).
```bash
python seed_hindsight_memory.py
```

### 4. Boot up the Engineer!
Start the Flask python server.
```bash
python backend.py
```
Then, double-click `ui/index.html` in your web browser and start sending queries about your machines!

---

## 🧠 How It Works

* **Cold Starts**: If you ask it about an unfamiliar piece of equipment, it will deliver a standard textbook diagnostic based on the model's base training, but actively prompt the technician to provide their real-world actions in the chat.
* **Perpetual Retention**: Every response the technician provides in the web chat automatically triggers a `hindsight.retain()` call in `backend.py`. The AI organically incorporates the newly documented fixes into its cloud memory structure for future shifts!
