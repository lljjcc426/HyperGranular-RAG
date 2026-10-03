# Execution notes

- Created the isolated relation-refinement branch/directory. Existing dirty files
  were not staged. No historical file was deleted or overwritten.
- Exact native Hotpot type and MuSiQue hop metadata were available in the already
  opened E/F channels. The fixed sample has 32 D0 and 64 D1 records without deficits.
- The first window-preparation attempt exposed the existing MuSiQue schema's
  `paragraph_index/sentence_index`, rather than Hotpot's `doc_id/sentence_id`.
  The local adapter now uses the original paragraph ID prefix. No prepared output
  existed at that failed point; no scientific ranking was rerun or changed.
- Before natural model calls, code inspection found that a feedback compatibility
  check could accept an entirely unanchored later slot as an extension of the empty
  binding. It now requires a question literal or already bound endpoint. The original
  synthetic CSV remains; v2 is the corrected implementation's full 32-instance
  comparison. Token-count bundle tie-breaking and 16-probe rerun support were also
  completed before natural outcomes. No claim that synthetic v1 was final.
- Qwen 3B official public snapshot aa8e72537993ba99e69dfaafa59ed015b17504d1
  uses the research license, not Apache. Noncommercial research/evaluation is
  permitted; no account gate, payment or separate commercial agreement was used.
- The Xet download stalled before writing the first weight shard: repeated checks
  showed zero shard bytes and unchanged CPU/memory. A 1-KB HTTP range request
  succeeded. Only the identified `get_model.py` process was stopped, preserving
  its partial file; the same frozen files resumed through Hugging Face's HTTP path.
  This was download recovery, not an interrupted experiment or model change.
  Observed download CPU before stopping: 25.078125 seconds; network wait is not
  GPU process time. Small tokenizer retrieval ran separately and reused identical
  destination files, without another weight copy. Its CPU was not measured.
- New model and raw D0 text/labels/output remain local. No old generation, old
  scoring, old bootstrap, Stage6 confirmation, reservation or Stage3B was accessed.

On-demand conditional BGE encoding is CPU-only while the reader occupies the GPU;
the encoder object is discarded after each new query encoding. This operational
choice prevents simultaneous GPU residency and charges load/forward costs. Natural
D1 use still requires the capability/resource gate and complete final code freeze.

The resumed HTTP transfer also remained at 706,616,154 partial weight bytes across
checks. Its identified downloader was stopped, retaining all partial files. The
authorized availability fallback was fixed globally to the existing 1.5B snapshot
before any natural model output; see MODEL_RESOLUTION.json. The 3B model has not
been evaluated and no relative capability claim is made. Tokenizers share the
existing Qwen vocabulary; D0 windows will be rebuilt in memory with the actual
selected tokenizer during model calibration, rather than assuming identity.

Correction after handle closure: total partial-download bytes were 1,598,952,515,
larger than the observed 706-MB shard snapshot. The observation did NOT establish
complete transfer inactivity. Treating the preferred model as unavailable was
premature. The identical HTTP transfer was therefore resumed without deleting any
file. The 1.5B D0 records remain an attempted fallback, not a selected winner.
The preferred 3B will be used if retrieval completes, as specified before all
outcomes; no D1 model output exists. No new prompt revision is introduced for 3B.

Subsequent process I/O inspection showed 1.342 GB written by the resumed downloader
while directory metadata still showed the old length. Open-file metadata was an
inadequate progress indicator in this environment. The resumed transfer is allowed
to finish normally; no further premature download termination. This correction
invalidates the earlier claim of demonstrated inactivity, not any scientific output.

Source offset clarification before D1: offsets are now explicitly relative to each
frozen sentence text, with original sentence/source IDs retained. The first D0
packets used offsets into a space-joined reconstruction; those are not claimed as
raw-document byte offsets. Source text is unchanged. Renderer quote visibility
ignores inserted display-number markers but still requires the quoted original
text sequence to survive; this prevents marker formatting from falsely rejecting
a multi-sentence quote.

Before any D0 model output, Transformers returned a tokenization object instead of
the expected list from `apply_chat_template(tokenize=True)`. The adapter now renders
the exact chat template then calls `encode(add_special_tokens=False)`. The failed
attempt made no generation calls. The first completed synthetic model batch used
explicit eager attention and produced nonfinite binary logits/repeated token0;
its calls and RESOURCE_CALIBRATION.json remain diagnostic failures. Returning to
the historical default attention implementation yielded finite scores and normal
text; RESOURCE_CALIBRATION_v2.json is the valid timing batch. Both batches count
towards resource/call totals; eight distinct windows were each attempted twice.

Final: the preferred 3B download completed and D0 finished without another prompt
revision. MODEL_RESOLUTION.json is the preserved premature fallback record, not
the final selected-model record; CALIBRATION_DECISION.json states the final 3B
identity and D stop. No D1 execution occurred. The two stopped-download CPU
observations (25.078125 and 31.53125 seconds) are conservatively both reported
alongside the successful transfer ledger; small download/shell/document CPU is
still unmetered. No exact all-work CPU accounting is claimed.

New files contain the prototype, synthetic records, calibration summaries and
reports. README receives only a new top status section; its unrelated local body
edits are not included in this round's commit. No file was deleted, and no paper,
historical result, image or plotting script was changed in this task.

Final read-only delivery reconciliation returned:
`DELIVERY_RECONCILIATION_PASS: calls, 32 parse reviews, 2 extraction calls, 64 reader records, 224 synthetic rows, D1 gated`.
It compared actual call logs to ledger counts, parse-review schema flags to raw
outputs, extraction call/fact counts, support visibility and synthetic row counts.
This was a single summary consistency check, not a repeat model experiment or
an independent semantic annotation claim.
