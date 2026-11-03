# Papers and implementations

Each directory contains its own complete ARE Python source tree. These are
non-faithful research implementations assembled from public code and appendix
descriptions, not verified copies of the authors' final evolved agents.

| Directory | Paper | Implementation details |
| --- | --- | --- |
| [autosaddler](../autosaddler/) | [AutoSaddler](https://arxiv.org/abs/2608.23041) | [Policy and public tool algorithms](../autosaddler/CHANGES.md) |
| [activesaddler](../activesaddler/) | [ActiveSaddler](https://arxiv.org/abs/2610.00906) | [Signature and calendar repair cases](../activesaddler/CHANGES.md) |
| [paretosaddler-i23](../paretosaddler-i23/) | [ParetoSaddler](https://arxiv.org/abs/2611.02079) | [I-23 policy reconstruction](../paretosaddler-i23/CHANGES.md) |
| [paretosaddler-i22](../paretosaddler-i22/) | [ParetoSaddler](https://arxiv.org/abs/2611.02079) | [I-22 policy and terminal conversion](../paretosaddler-i22/CHANGES.md) |
| [harnessmm](../harnessmm/) | [HarnessMM](https://arxiv.org/abs/2610.32813) | [Public continuation controller](../harnessmm/CHANGES.md) |

The two ParetoSaddler directories represent different searches. HarnessMM contains
an earlier public deterministic component, not the later frozen configuration
behind the paper's complete result. Each `SOURCE.json` records source provenance;
each `CHANGES.md` distinguishes implemented components from missing behavior.

ARE originates from Meta's MIT-licensed source. HarnessMM's extracted controller
retains its Apache-2.0 license. Full papers are linked rather than bundled.
