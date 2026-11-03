# Implementation and source notes

## AutoSaddler

[Paper](https://arxiv.org/abs/2608.23041), Appendix N, Table 16;
[official optimization repository](https://github.com/microsoft/AutoSaddler);
[published evolution patches](https://github.com/autosaddler-projectpage/autosaddler-projectpage.github.io/blob/afd493fa47cdbced1c1a829285836b88d8cdbf70/src/components/EvolutionDemo/evo-data.ts).

| Published component | This variant |
| --- | --- |
| Direct factual responses | Reconstructed policy |
| Ties, singular/multiple matches, per-group ambiguity | Reconstructed policy |
| Ordered-subtask dependency boundaries | Reconstructed policy |
| Constructive email reply reminder | Reconstructed policy, not the original hook |
| Crime-rate batch | Agent-owned native-call adaptation of I-08 → I-11; per-ZIP quota retained |
| Folder addresses and both messaging participant algorithms | Agent-owned native-call adaptations of I-13 → I-14; V2 requires public self-identity |
| Ride-history search | Agent-owned native-call adaptation of I-24 → I-25 |
| Expanded contact-field matching | Agent-owned search replacement from I-06 → I-08; no app patch |
| Automatic inter-turn wait of up to 300 seconds | Not implemented; native waits remain actor-selected |
| Automatic mkdir/move parent resolution | Policy guidance only; no automatic argument rewrite |

The published table is explicitly a representative patch catalogue. Neither that
table nor the optimizer repository establishes an exact complete final snapshot.
The project page exposes concrete code for the six algorithms above; its source
revision and diff hashes are pinned in `are/simulation/agents/default_agent/tool_sources.json`. These are selected
patches from an evolution trajectory, not a verified complete final snapshot.
The published patches do not specify task/universe routing. The adapter exposes
capabilities according to available public prerequisites only. Pagination, event
counts, representation, atomicity, and elapsed time can differ from the original
app-level implementations. This variant does not inherit the paper's 53% to 62%
result. Other app-description changes and non-tool hooks in those patches are not
claimed as implemented.

## Native source layout

The full `are/` Python package is included locally. The standard factory remains
`are.simulation.agents.default_agent.agent_factory.are_simulation_react_json_agent`.
Research behavior is implemented in this directory, without importing the
collection CLI or a sibling agent. `SOURCE.json` records upstream provenance.

All directories include native pending-step persistence and success-aware terminal
tool handling. These common runtime fixes are separate from the paper-inspired
changes. They retain the native JSON executor, log memory and model-call contract.
