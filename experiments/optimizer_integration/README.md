# Optimizer integration: evidence-bound rewrite prototype

The groupmate's optimizer experiments are directly relevant to the proposal's optional constrained LLM rewrite and manual factuality review. The supplied workspace includes methods coupled to a local baseline, generated outputs, a vendor fact-checker, an NLI model cache, and Ollama. Those artifacts and dependencies are not copied as if they were a standalone application.

This directory incorporates a portable first-step validator: `evidence_bound_edit.py`. It operates on one preselected source sentence and proposed replacement, checks exact source/evidence quoting and conservative text-preservation rules, and returns a draft pending human review or keeps the original. It does not make LLM calls and does not prove truth or semantic equivalence.

## Usage

```python
from evidence_bound_edit import validate_edit

result = validate_edit(
    original_resume="Objective: Experienced analyst seeking a role. Skills: SQL",
    start=11,
    end=43,
    payload={
        "source": "Experienced analyst seeking a role.",
        "replacement": "Experienced analyst pursuing a role.",
        "evidence_quote": "Experienced analyst seeking a role.",
    },
)
print(result.status, result.effective_text)
```

The offsets must identify exactly the selected sentence in the original resume. Production use requires manual comparison with the complete resume and source evidence. The checks can reject valid paraphrases and miss unsupported changes. No green/pass result means factuality verified. Tests:

```bash
python -m unittest discover -s experiments/optimizer_integration -p 'test_*.py'
```

## Not integrated into the live API yet

The current `/api/rewrite` accepts full-resume drafts, whereas this prototype requires explicit source offsets and a structured response. Do not silently use it on an entire resume. A future integration should first add reliable sentence/span selection, show draft/effective text and rejection reasons, keep originals unchanged on rejection, and require human review. The provided whole-resume and NLI guard experiments are valuable design/evaluation references, but their omitted support modules and local artifacts must be restored and reviewed before their reported outcomes can be reproduced.
