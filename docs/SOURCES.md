# Papers and implementations

Each directory contains a complete ARE Python source tree, with research changes
assembled from public code and paper appendices. The table links each method to
its implementation notes.

| Directory | Paper | Implementation details |
| --- | --- | --- |
| [autosaddler](../autosaddler/) | [AutoSaddler](https://arxiv.org/abs/2608.23041) | [Policy and public tool algorithms](../autosaddler/CHANGES.md) |
| [activesaddler](../activesaddler/) | [ActiveSaddler](https://arxiv.org/abs/2610.00906) | [Signature and calendar repair cases](../activesaddler/CHANGES.md) |
| [paretosaddler-i23](../paretosaddler-i23/) | [ParetoSaddler](https://arxiv.org/abs/2611.02079) | [I-23 policy reconstruction](../paretosaddler-i23/CHANGES.md) |
| [paretosaddler-i22](../paretosaddler-i22/) | [ParetoSaddler](https://arxiv.org/abs/2611.02079) | [I-22 policy and terminal conversion](../paretosaddler-i22/CHANGES.md) |
| [harnessmm](../harnessmm/) | [HarnessMM](https://arxiv.org/abs/2610.32813) | [Public continuation controller](../harnessmm/CHANGES.md) |

The two ParetoSaddler directories represent different searches. HarnessMM ports
the earlier public deterministic continuation controller. Each `SOURCE.json`
records source provenance; each `CHANGES.md` describes the implementation and its
differences from the paper.

ARE originates from Meta's MIT-licensed source. HarnessMM's extracted controller
retains its Apache-2.0 license. Paper links are listed above.
