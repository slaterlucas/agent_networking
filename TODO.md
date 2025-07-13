## Project TODO

### Andrej – Event Selector
- [ ] Build *Event Selector* agent mirroring Restaurant Selector:
  - [ ] Define `event_selector/main.py` agent that uses Exa + Gemini to pick events.
  - [ ] Create FastAPI / python-a2a wrapper (`adk.event_selector.A2A:app`).
  - [ ] Support `/tasks/send` and `/invoke` endpoints for direct + A2A access.
  - [ ] Publish typed `AgentCard` with `Inputs`/`Outputs` schemas.
  - [ ] Auto-register with discovery registry on startup.

### Harsh – Orchestrator
- [ ] Implement *Orchestrator* service that coordinates between personal agents and selectors.
  - [ ] POST endpoint `/meet` that accepts `{from: "alice", to: "bob", context?: {...}}`.
  - [ ] Fetch / receive preference JSON from both personal agents (or accept pre-merged prefs).
  - [ ] Decide whether to consult **Restaurant Selector** or **Event Selector** (or both).
  - [ ] Forward combined preferences, await reply, return final recommendation.
  - [ ] Expose `/tasks/send` + `/invoke` for A2A compatibility.
  - [ ] Register its `AgentCard` with the discovery registry.

### W&B Integration (Open)
- [ ] Add Weights & Biases logging to all agents and orchestrator:
  - [ ] Initialise one W&B run per recommendation request.
  - [ ] Log latency, tool calls, chosen recommendation, and user feedback (when available).
  - [ ] Ensure `WANDB_API_KEY` is optional but honoured when present.

### Stretch Goals
- [ ] End-to-end smoke-test script exercising Alice → Orchestrator → Selector → Alice flow.
- [ ] Maybe docker?
