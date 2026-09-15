# _demo — synthetic client

**Every file here is synthetic.** It was generated to exercise the extract and
canonical layers end to end before any real export exists, and it is committed
deliberately so the pipeline is runnable on a fresh clone.

No real client data belongs in this repository — see `.gitignore`.

Run it:

```
python -m bootcamp extract --client _demo --adapter generic_csv \
    --input clients/_demo/raw/ops/hours.csv
```
