# Emerald ITR Pro - AI Integration Guide

## Overview

This guide explains how to integrate the AI-powered features into the Emerald ITR Pro application. The AI system uses a local **Phi-4-mini** model running via llama-cpp-python to extract data from Form 16/26AS/AIS PDFs, provide tax advisory, and audit tax return data.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup](#setup)
3. [Architecture](#architecture)
4. [Integrating AI into GUI](#integrating-ai-into-gui)
5. [Code Examples](#code-examples)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Dependencies

```bash
pip install llama-cpp-python>=0.3.1 psutil>=5.9.0
```

### Hardware Requirements

| RAM | AI Mode | Context | GPU Layers |
|-----|---------|---------|------------|
| < 4GB | Eco | 1024 | 0 |
| 4-12GB | Standard | 2048 | 0 |
| > 12GB | Pro | 4096 | Dynamic (min(35, cpu_count * 4)) |

### Required Directories

```
emerald_itr_pro/
    data/
    settings.json
    ai_audit_log.json
models/
    Phi-4-mini-instruct-Q8_0.gguf
```

---

## Setup

### 1. Download the Model

Download the **Phi-4-mini** GGUF model from HuggingFace and place it in the `models/` directory.

**Recommended Model:**
- **Name**: `Phi-4-mini-instruct-Q8_0.gguf`
- **Link**: [LM Studio Community Phi-4 on HuggingFace](https://huggingface.co/lmstudio-community/Phi-4-mini-instruct-GGUF)

**Automatic Discovery Logic:**
- The app first checks the `ai_model_path` in `settings.json`.
- If missing or invalid, it scans the `models/` folder for any `.gguf` file.
- It prioritizes files with **"phi"** in the name for best prompt compatibility.
- If no "phi" model exists, it falls back to the first `.gguf` file it finds.

### 2. Configure Settings

The AI settings are already in `settings.json`:

```json
{
  "ai_enabled": true,
  "ai_model_path": "models/Phi-4-mini-instruct-Q8_0.gguf",
  "ai_confidence_threshold": 0.85,
  "ai_max_tokens": 2048,
  "ai_temperature": 0.1,
  "ai_thread_pool_size": 1
}
```

Users can toggle AI in Settings → General → AI Assistant.

---

## Architecture

### Key Components

```
GUI Layer
├── AI Panel (src/gui/components/ai_panel.py)
│   └── Displays AI suggestions with Accept/Reject buttons
└── Settings Toggle (src/gui/dialogs/settings/pages/general_page.py)
    └── Enables/disables AI extraction

Service Layer
├── AIManager (src/services/ai/ai_manager.py)
│   └── Singleton managing LLM instance
├── ImportService (src/services/io/import_service.py)
│   └── extract_with_ai() - Entry point for GUI
└── Hardware Utils (src/services/ai/hardware_utils.py)
    └── Detects RAM/CPU and adjusts parameters

Core AI Layer
├── Prompts (src/services/ai/prompts.py)
│   └── Extraction prompts for Form 16, 26AS, AIS, and Tax Advisory
├── Schemas (src/services/ai/schemas.py)
│   └── JSON validation schemas for all AI outputs
└── PII Sanitization
    └── Masks PAN/Aadhaar before sending to LLM
```

### Data Flow

```
1. User imports PDF
   ↓
2. PDF text extracted
   ↓
3. ImportService.extract_with_ai(text, root, callback)
   ↓
4. AIManager (background thread)
   - Sanitizes PII
   - Sends to LLM
   - Validates JSON
   ↓
5. Callback via root.after() (thread-safe)
   ↓
6. AI Panel displays suggestions
   ↓
7. User Accepts/Rejects
   ↓
8. VarDict updated + Audit log written
```

---

## Integrating AI into GUI

### Step 1: Add AI Panel to Your View

```python
from src.gui.components.ai_panel import AIPanel

class YourView(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.ai_panel = AIPanel(self, root_window=self.master)
        self.ai_panel.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.ai_panel.set_callback(self._handle_ai_decision)
    
    def _handle_ai_decision(self, field: str, value: Any, action: str):
        if action == "accept":
            if field in self.form_vars:
                self.form_vars[field].set(value)
            self._recalculate_tax()
        elif action == "reject":
            pass
```

### Step 2: Connect PDF Import to AI

```python
from src.services.io.import_service import ImportService

def on_pdf_import_clicked(self):
    path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
    if not path:
        return
    
    with open(path, "rb") as f:
        reader = pypdf.PdfReader(f)
        text = "\n".join(p.extract_text() for p in reader.pages)
    
    ImportService.extract_with_ai(
        text=text,
        root_window=self,
        on_result=self._handle_ai_result
    )

def _handle_ai_result(self, result: dict):
    if result.get("status") == "success":
        ai_data = result.get("data", {})
        
        self.ai_panel.add_suggestion(
            field_name="Gross Salary",
            current_value=self.form_vars["sal_gross"].get(),
            ai_value=ai_data.get("sal_gross"),
            confidence=ai_data.get("confidence", 0),
            source_snippet="Form 16 PDF"
        )
    else:
        messagebox.showerror("AI Error", "Failed to extract data with AI")
```

### Step 3: Run Audit on Current State

```python
def run_background_audit(self):
    vardict = self._get_current_vardict()
    
    ImportService.run_ai_audit(
        vardict=vardict,
        root_window=self,
        on_result=self._handle_audit_result
    )

def _handle_audit_result(self, result: dict):
    if result.get("status") == "success":
        warnings = result.get("data", {}).get("warnings", [])
        
        for warning in warnings:
            if warning["severity"] == "High":
                messagebox.showwarning(
                    f"Audit Warning: {warning['section']}",
                    warning["message"]
                )
```

### Step 4: Specialized Extraction (Form 26AS, AIS, Advisory)

```python
ImportService.extract_form26as_with_ai(text, self, self._handle_26as_result)

ImportService.get_tax_advisory(vardict, self, self._handle_advisory_result)

ImportService.classify_document(text, self, self._handle_classification)
```

---

## AI Features & Capabilities

### 1. Form 16/26AS/AIS Extraction
Extracts complex nested data (TDS, Salary Breakdowns, Interest) into structured JSON.

### 2. Tax Advisory
Reviews the current `VarDict` (app state) and provides contextual advice on optimization and compliance.

### 3. Document Classification
Detects if a piece of text belongs to a Form 16, 26AS, AIS, or TIS.

### 4. Background Auditing
Silently scans for high-risk data entry errors or statutory mismatches.

---

## Code Examples

### Example 1: Simple AI Extraction

```python
from src.services.io.import_service import ImportService

def extract_form16_data(pdf_text: str):
    results = []
    
    def on_result(result):
        results.append(result)
    
    ImportService.extract_with_ai(
        text=pdf_text,
        root_window=root,
        on_result=on_result
    )
    
    return results[0] if results else None
```

### Example 2: Check AI Status

```python
from src.services.ai.ai_manager import get_ai_manager

def check_ai_status():
    ai_manager = get_ai_manager()
    
    print(f"AI Enabled: {ai_manager.is_enabled()}")
    print(f"Hardware Profile: {ai_manager.get_profile()}")
    print(f"Confidence Threshold: {ai_manager.get_confidence_threshold()}")
```

### Example 3: Manual PII Sanitization

```python
from src.services.ai.hardware_utils import sanitize_pii

text = "PAN: ABCDE1234F, Aadhaar: 1234 5678 9012"
sanitized = sanitize_pii(text)
```

---

## Testing

### Run Unit Tests

```bash
python -m pytest tests/test_ai_services.py -v
```

### Test PII Sanitization

```python
from src.services.ai.hardware_utils import sanitize_pii

assert "XXXXX1234X" in sanitize_pii("ABCDE1234F")

assert "XXXX XXXX 9012" in sanitize_pii("1234 5678 9012")
```

### Test with Mocked AI

The test suite uses mocked Llama instances, so no model is required for testing:

```bash
python -m pytest tests/test_ai_services.py
```

All 22 tests should pass.

---

## Troubleshooting

### Issue: "Model not found"

**Solution:**
- Ensure the **Phi-4-mini** `.gguf` file is in the `models/` directory.
- The app will automatically discover it even if the filename is slightly different.
- Check that the `models/` folder itself exists (it should be auto-created on first run).

### Issue: "AI is disabled"

**Solution:**
- Check RAM (must be >= 8GB for Standard mode)
- Enable AI in Settings → General → AI Assistant
- Check `ai_enabled` in settings.json

### Issue: "psutil not available"

**Solution:**
```bash
pip install psutil>=5.9.0
```

The system will default to Eco profile if psutil is missing.

### Issue: GUI freezes during AI processing

**Solution:**
- Ensure all callbacks use `root.after()` for thread safety
- The AIManager uses ThreadPoolExecutor for background processing
- Check that the callback is properly scheduled

### Issue: Low confidence results

**Solution:**
- AI confidence < 0.85 is flagged for manual review
- This is expected behavior - user should verify
- Check if PDF text is clear and readable

### Issue: JSON parsing errors

**Solution:**
- The AIManager retries once with lower temperature
- Check the prompt templates in `prompts.py`
- Ensure the model is responding with valid JSON

---

## Performance Tips

1. **Model Placement**: Keep the GGUF file on SSD for faster loading
2. **Context Size**: Adjust `n_ctx` in hardware_utils.py if needed
3. **Thread Pool**: Keep `max_workers=1` to prevent KV cache corruption
4. **Background Loading**: Model loads on first use (lazy loading)

---

## Security Notes

- **No Cloud Calls**: All AI processing is local
- **PII Sanitization**: PAN and Aadhaar are masked before sending to LLM
- **Audit Trail**: All AI decisions are logged to `data/ai_audit_log.json`
- **Model Control**: Only the specified GGUF model is used

---

## Support

For issues or questions:
1. Check `docs/AI_DEVELOPMENT_SPEC.md` for technical details
2. Review `src/services/ai/` module documentation
3. Run tests to verify installation

---

## Version History

- **v1.0** (2026-04-22): Initial AI integration
  - Phi-4-mini model support
  - Form 16 extraction
  - Background audit
  - PII sanitization
  - Hardware-aware scaling
