# Algebra and scope

The ANOVA recurrence and maximum-inner-product ball bound are existing techniques (primary sources in LITERATURE_AND_DESIGN.md). They are not claimed as new theory.

For distinct items S, e_0(S)=1 and e_h(S)=sum over h-element subsets of the coordinate-wise product. Partition the subsets of S+{i} into those containing i and those not containing i. Thus e_h(S+i)=e_h(S)+v_i e_(h-1)(S). Descending-order in-place recurrence preserves the preceding prefix; the PyTorch implementation creates new tensors to preserve gradients. With fixed denominators r*choose(K,h), the specified F gives delta_i=delta b+[1; sum_h w_h e_(h-1)(S)/(r choose(K,h))]^T [a_i/K;v_i]. This formula does not hold unchanged for a set-size-dependent denominator. Cardinality bias remains in comparisons across depths.

For c=mean(z_i) and rho=max_i ||z_i-c||, Cauchy–Schwarz gives theta^T z_i <= theta^T c+||theta||rho. This remains valid with signed weights. Mean radius fails: points {0,0,9}, center3, mean radius4 give upper bound7 for direction1, below9; maximum radius6 gives9. Float64 and conservative outward radius / pruning slack mitigate numerical errors but are not a formal floating-point certification.

Exact expansion parity requires the same feasible candidates, full members, stable ties and exhaustive traversal of any node able to match or improve the current top4. It proves agreement with the specified beam, not the global best subset. A width1 beam with singleton scores5,4,0,0 and pair {third,fourth} score100 misses the global best pair. Negative immediate gains cannot justify stopping when signed higher-order interactions exist.

A nonzero third mixed finite difference of x*y*z cannot be represented by a degree<=2 multilinear polynomial on those binary coordinates. This narrow fact says nothing about arbitrary pairwise neural networks, cardinality biases or general DeepSets; it does not establish that H4 is necessary for QA. In particular, cardinality alone can solve some AND examples.

Initial actual test run: 8 tests passed; 2,016 synthetic parent-state comparisons across H1/H2/H4, signed/random and degenerate vectors. Tests include DP and autograd vs enumeration, direct-score vs marginal, maximum-bound coverage, duplicate rejection, same-ball unrestricted selection, mean-radius and beam counterexamples, annotation granularity/deduplication. Natural parity and learned high-order gradients will be reported separately after execution.

Neither this proxy score nor beam/tree search gives factual truth, evidence semantic sufficiency, answer-F1 improvement, submodularity, 1-1/e approximation or end-to-end speed guarantees.
