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
