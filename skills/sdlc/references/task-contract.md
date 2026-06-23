# Task contract - the work-unit backlog

gear:pm emits a backlog: an ordered list of work units. gear:sdlc consumes it and fans
independent units out across agents. Each work unit conforms to `task-contract.schema.json`;
`task-contract.example.json` is a worked 2-unit example.

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | unique unit id |
| `goal` | string | one-sentence desired result |
| `inputs` | string[] | files/context the unit needs |
| `output_schema` | object | shape of the unit's result (structured output) |
| `acceptance` | string[] | checkable accept criteria |
| `deps` | string[] | ids of units that must finish first |
| `isolation` | "none" or "worktree" | whether it mutates files and needs a git worktree |
| `verify` | object {strategy, votes?} | how the result is verified before accept |

A schema-bound backlog is what makes results predictable: gear:sdlc runs each unit against
its contract instead of guessing the shape of the result.
