# Fixed source-text case review

POST_HOC_DESCRIPTIVE_ANALYSIS_OF_EXISTING_RUNS. Assistant-assisted, not independent expert annotation. Sixteen distinct development questions; no new reader or scorer. All selected source paragraphs were read before the saved outputs. Private source text, questions, answers and mappings remain local.

Selection: H4, seed1729 first; dataset × full-support transition × F1 gain/harm cells. Within each nonempty cell select the first SHA256(`NC-case-v1|dataset|query_id`). Add previously unselected questions from seed2026, then unchanged cells only if necessary, stopping at 16. The realized sample has ten primary-seed and six second-seed questions. No case was replaced because its story was inconvenient. Outcome stratification precludes prevalence estimation.

All 32 paired outputs reached EOS; none reached the output cap. A changed score does not establish evidence sufficiency. These entries do not alter canonical scores or add aliases.

| Case / anonymous key | Dataset / seed | Full | Saved F1 static → aligned | Source-text observation, then output interpretation |
|---|---|---|---|---|
| C01 / q024 | Hotpot / 1729 | 00 | 0 → .6667 | City visible, county bridge absent. Output changes to a county-like short form; better lexical overlap does not establish a supported chain. |
| C02 / q060 | Hotpot / 1729 | 00 | 1 → 0 | Producer identity retained, requested nationality not explicitly supplied. Other musicians’ nationalities occur; output changes nationality. Causal distraction remains untested. |
| C03 / q058 | Hotpot / 1729 | 01 | 0 → .6667 | Added team paragraph supplies a missing conference bridge. Abstention changes to the conference short name; EM remains zero. |
| C04 / q011 | Hotpot / 1729 | 11 | 0 → .4 | Both birth years remain visible. Output switches to the older person; lexical score is still partial. No loss of necessary date text observed. |
| C05 / q012 | Hotpot / 1729 | 11 | 1 → 0 | Both breakup/continued-activity facts remain explicit. Output switches to the other band despite retention of the comparison evidence. |
| C06 / q100 | MuSiQue / 1729 | 00 | 0 → .5 | Birthplace link absent; law passages mix jurisdictions and open/concealed carry. Output date changes, but a complete correct chain is not established. |
| C07 / q098 | MuSiQue / 1729 | 00 | .5 → 0 | Added relative biography gives nationality and partial family information; identity link remains incomplete. Country phrase changes to an adjectival nationality. Correctness cannot be inferred from the lexical difference. |
| C08 / q093 | MuSiQue / 1729 | 01 | 0 → 1 | Added territorial paragraph gives organization/statehood dates among similarly named places. Exact saved match improves; the wording still leaves acquisition versus statehood scope ambiguous. |
| C09 / q082 | MuSiQue / 1729 | 11 | 0 → .6667 | Two same-named villages with distinct departments remain. Output changes department; supplied country constraint does not resolve the text ambiguity by itself. |
| C10 / q075 | MuSiQue / 1729 | 11 | 1 → 0 | Creator and production-date range retained. Output switches from production endpoint to rights-transfer date present in the same source; role/date-selection error. |
| C11 / q009 | Hotpot / 2026 | 00 | 1 → 0 | Sponsor full name and its acronym remain explicit. Output changes full name to acronym; saved canonical mismatch is not missing entity evidence. No favorable alias normalization applied. |
| C12 / q027 | Hotpot / 2026 | 01 | 0 → 1 | Added company paragraph resolves city for the precise founder/chairman/CEO role. Output changes from a nearby family-related location to that city. |
| C13 / q015 | Hotpot / 2026 | 11 | .5 → 1 | Publication cities and largest-city fact remain. Output becomes the requested publication instead of the city; answer target/form changes. |
| C14 / q056 | Hotpot / 2026 | 11 | 1 → 0 | Both musical roles remain explicit. Yes/no reverses with changed surrounding context; internal mechanism undetermined. |
| C15 / q071 | MuSiQue / 2026 | 00 | 0 → .5 | Similar names and county-bearing passages without a secure target link. Partial lexical improvement does not establish the right identity. |
| C16 / q108 | MuSiQue / 2026 | 00 | .2857 → 0 | Parent-company country link incomplete; retained appointment passage names a monarch. Output switches jurisdictional role. Annotation/identity interpretation remains unresolved. |

Main-text illustrations C03/C12 show added bridges, C10 distinguishes a date role error despite complete support, and C11 separates lexical form from evidence membership. The complete selected set above includes favorable, unfavorable, and unresolved interpretations. No statistics are extrapolated from it.
