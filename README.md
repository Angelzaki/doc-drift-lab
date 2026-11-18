<div align="center">

# doc-drift-lab

**Drift de corpus → impacto en retrieval** · Angel Salazar

`docs_a vs docs_b → hit_rate delta + regressions`

</div>

---

### `$ whoami`

```text
pregunta: si agrego 100 PDFs, ¿se rompe el retrieval actual?
método: misma batería de queries antes/después
```

---

### `$ ./drift.sh`

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
pytest
python -m doc_drift
```

---

Hecho en Lima · Angel Salazar · CIP 404730
