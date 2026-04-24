# Emerald ITR Pro - AI Integration Guide

## Overview

This guide explains how to integrate the AI-powered data extraction features into the Emerald ITR Pro application. The AI system uses a local Phi-4-mini model running via llama-cpp-python to extract data from Form 16 PDFs and audit tax return data.

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
    data/              # Created automatically
    settings.json  # AI configuration
    ai_audit_log.json  # Audit trail
models/            # Download model here
    Phi-4-mini-instruct-Q8_0.gguf
```

---

## Setup

### 1. Download the Model

Download the Phi-4-mini GGUF model from HuggingFace:

- **Model**: `Phi-4-mini-instruct-Q8_0.gguf` (recommended) or similar variant
- **Size**: ~4GB
- **Location**: Place in `models/` directory
- **Source**: [LM Studio Community Phi-4 on HuggingFace](https://huggingface.co/lmstudio-community/Phi-4-mini-instruct-GGUF)

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
│   └── Form 16 extraction prompts
├── Schemas (src/services/ai/schemas.py)
│   └── JSON validation schemas
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

# In your view class
class YourView(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Create AI panel
        self.ai_panel = AIPanel(self, root_window=self.master)
        self.ai_panel.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Set callback for accept/reject
        self.ai_panel.set_callback(self._handle_ai_decision)
    
    def _handle_ai_decision(self, field: str, value: Any, action: str):
        """Handle user's decision on AI suggestion."""
        if action == "accept":
            # Update your form_vars
            if field in self.form_vars:
                self.form_vars[field].set(value)
            # Trigger recalculation
            self._recalculate_tax()
        elif action == "reject":
            # User rejected suggestion - no action needed
            pass
```

### Step 2: Connect PDF Import to AI

```python
from src.services.io.import_service import ImportService

def on_pdf_import_clicked(self):
    """Handle PDF import button click."""
    # First, extract text from PDF (existing code)
    path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
    if not path:
        return
    
    # Extract text using pypdf
    with open(path, "rb") as f:
        reader = pypdf.PdfReader(f)
        text = "\n".join(p.extract_text() for p in reader.pages)
    
    # Send to AI for extraction
    ImportService.extract_with_ai(
        text=text,
        root_window=self,
        on_result=self._handle_ai_result
    )

def _handle_ai_result(self, result: dict):
    """Handle AI extraction result."""
    if result.get("status") == "success":
        ai_data = result.get("data", {})
        
        # Add suggestions to AI panel
        self.ai_panel.add_suggestion(
            field_name="Gross Salary",
            current_value=self.form_vars["sal_gross"].get(),
            ai_value=ai_data.get("sal_gross"),
            confidence=ai_data.get("confidence", 0),
            source_snippet="Form 16 PDF"
        )
        
        # Add other fields similarly
        # ...
    else:
        messagebox.showerror("AI Error", "Failed to extract data with AI")
```

### Step 3: Run Audit on Current State

```python
def run_background_audit(self):
    """Run AI audit on current tax return data."""
    vardict = self._get_current_vardict()
    
    ImportService.run_ai_audit(
        vardict=vardict,
        root_window=self,
        on_result=self._handle_audit_result
    )

def _handle_audit_result(self, result: dict):
    """Handle audit warnings."""
    if result.get("status") == "success":
        warnings = result.get("data", {}).get("warnings", [])
        
        for warning in warnings:
            if warning["severity"] == "High":
                messagebox.showwarning(
                    f"Audit Warning: {warning['section']}",
                    warning["message"]
                )
```

---

## Code Examples

### Example 1: Simple AI Extraction

```python
from src.services.io.import_service import ImportService

def extract_form16_data(pdf_text: str):
    """Extract Form 16 data using AI."""
    
    results = []
    
    def on_result(result):
        results.append(result)
    
    ImportService.extract_with_ai(
        text=pdf_text,
        root_window=root,
        on_result=on_result
    )
    
    # Wait for result (in real app, use callback)
    # This is just for demonstration
    return results[0] if results else None
```

### Example 2: Check AI Status

```python
from src.services.ai.ai_manager import get_ai_manager

def check_ai_status():
    """Check if AI is available and enabled."""
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
# Output: "PAN: XXXXX1234X, Aadhaar: XXXX XXXX 9012"
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

# Test PAN masking
assert "XXXXX1234X" in sanitize_pii("ABCDE1234F")

# Test Aadhaar masking
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
- Ensure the GGUF file is in `models/` directory
- Check `ai_model_path` in settings.json
- Verify filename matches (tolerates minor suffix variations)

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
