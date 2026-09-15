# _template — copy this to start a client

```
cp -r clients/_template clients/<client-name>
```

| Folder | Layer | What goes here |
|---|---|---|
| `raw/accounting/` | 0 | QBO exports, exactly as downloaded. Never edited |
| `raw/ops/` | 0 | LMN (or other) time exports, exactly as downloaded |
| `config/client-config.xlsx` | 3 | Every judgment call for this client |
| `output/` | 2 | `inputs.xlsx`, written by the extract step |

`raw/`, `output/` and a real `config/client-config.xlsx` are gitignored. Client
financial data does not belong in this repository.
