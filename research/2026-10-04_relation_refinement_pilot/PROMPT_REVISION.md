# One permitted global prompt revision, before D0 check outputs

D0 dev v1: 0/16 schema-valid parses. Direct reading found nested arrays, malformed
objects, invented constants/dates, reused answer variables, reversed relations,
and unresolved answer_var. The raw attempts remain in local/d0_parse_dev.jsonl.
Synthetic extraction also sometimes emitted variables/relation text as entity spans.

The single global revision adds a short invented two-hop parser example and one
source-span extraction example, explicitly forbidding nested lists and variable
entity values. Neither uses a dataset question, answer, query ID or Gold. Model,
decoding, token limits, threshold candidates and D1 remain unchanged. Dev v2 is
stored separately. The check half has not been generated or used for this revision.
No further prompt revision is permitted in this pilot.
