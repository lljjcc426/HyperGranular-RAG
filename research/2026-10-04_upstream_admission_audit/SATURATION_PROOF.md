# Lexical saturation: a limitation of this proxy

Let U be the fixed candidate universe, D its Dense Top-K, and r(u) the
within-query empirical rank, monotonically nondecreasing with the original score.
Let T(u) be fixed title-plus-sentence question terms and
Cov(S)=|union(T(u), u in S)|/max(1,|Tq|). Suppose
union(T(u),u in D)=union(T(u),u in U).

For any set S of K distinct candidates, the sum of ranks in D is at least the
sum in S: D contains K largest scores, hence K largest ranks; score ties do not
invalidate the weak inequality. Cov(S)<=Cov(D), because D already covers the
whole observable union. For 0<=lambda<=1, multiplying the two weak inequalities
by their nonnegative weights and adding yields

Phi(S)=lambda sum(r(u),u in S)/K+(1-lambda)Cov(S) <= Phi(D).

Empty Tq gives Cov=0 under the fixed denominator rule. K=min(20,|U|)>0.
If lambda=0 or1, or ties exist, D need not be a unique optimizer. Without
observable saturation the second inequality need not hold; the synthetic test
explicitly exhibits such a counterexample. Numeric checks use absolute tolerance
1e-12 only for this property; no selection tie rule is modified.

This standard consequence of two coordinate-wise inequalities is not a new
theoretical contribution, an answer-quality guarantee, or an ordering theorem.
R1 may improve relative to H0 while remaining no better than Dense for Phi.
Reordering the same set may change generated answers without changing Phi.
Covering every term observable in U differs from covering every term in Tq;
neither establishes a complete reasoning chain. Historical full and pilot
saturation counts are reported separately in GROUPING_AND_SATURATION.csv.
