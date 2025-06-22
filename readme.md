# 🧾 Intelligent PDF Summarizer (Mock Version)

**Author:** Meet Prajapati  
**Project Type:** Serverless | Event-driven | Azure-based  
**Technology Stack:** Azure Durable Functions, Form Recognizer, Python

---

## 📝 Introduction

This project simulates a PDF summarization pipeline using Azure Durable Functions. In this version, Azure OpenAI is mocked due to quota restrictions in student accounts.

---

## ⚙️ Workflow Overview

1. **Upload PDF** → Blob Trigger starts the orchestration.
2. **Text Extraction** → Azure Form Recognizer extracts text.
3. **Summarization** → Mock function returns sample summary.
4. **Output** → Summary is saved as `.txt` in an output container.

---

## 📂 Project Layout

```plaintext
📦 Intelligent-PDF-Summarizer
├── 📄 function_app.py        # Main Durable Function logic
├── ⚙️ local.settings.json    # Local Azure Functions config
├── 📜 requirements.txt       # List of dependencies
├── 🧠 mock_summary.py        # Mock summarizer function
├── 🛠️ host.json              # Host-level settings
```

---

## 🧪 Mocked Summary Output

```
This is a mock summary of the uploaded PDF document.
Replace this placeholder once Azure OpenAI is available.
```

---

## 🎥 Demo Video Link

🔗 [Watch Demo on YouTube](https://www.youtube.com/watch?v=NUdGRoZW7ks)

---

## 📬 Contact

- GitHub: [@praj0080](https://github.com/praj0080)
