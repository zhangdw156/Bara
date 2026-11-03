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
| Constructive email reply reminder | Email reply policy reconstruction |
| Crime-rate batch | Agent-owned native-call adaptation of I-08 → I-11; per-ZIP quota retained |
| Folder addresses and both messaging participant algorithms | Agent-owned native-call adaptations of I-13 → I-14; V2 requires public self-identity |
| Ride-history search | Agent-owned native-call adaptation of I-24 → I-25 |
| Expanded contact-field matching | Agent-owned search replacement from I-06 → I-08 |
| Automatic inter-turn wait of up to 300 seconds | Not implemented; native waits remain actor-selected |
| Automatic mkdir/move parent resolution | Policy guidance; the agent supplies parent-path arguments |

The table covers representative patches from the published evolution trajectory.
The project page provides code for the six algorithms above; source revisions and
diff hashes are recorded in
`are/simulation/agents/default_agent/tool_sources.json`.

The adapter exposes these algorithms according to available public prerequisites.
The published patches leave task/universe routing unspecified. Pagination, event
counts, representation, atomicity and elapsed time can differ from the original
app-level implementations. Other app-description changes and non-tool hooks are
outside this implementation's scope.

## Native source layout

The full `are/` Python package is included locally. The standard factory remains
`are.simulation.agents.default_agent.agent_factory.are_simulation_react_json_agent`.
Research behavior lives in `are/simulation/agents/default_agent/`.
`SOURCE.json` records upstream provenance.

Common runtime updates cover pending-step persistence and success-aware terminal
tool handling, using the native JSON executor, log memory and model-call contract.
