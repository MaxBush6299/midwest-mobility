---
target: trace UI (src\mmc_agents\trace_ui\static\index.html)
total_score: 21
p0_count: 2
p1_count: 5
timestamp: 2026-06-18T13-27-08Z
slug: src-mmc-agents-trace-ui-static-index-html
---
## MMC Demo Trace UI — Design Critique

### Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3 | Stats, elapsed, active agents work; no run-phase indicator, no cancel/no-data terminal state. |
| 2 | Match System / Real World | 2 | "Magentic," "hop," "ledger," `NO_DIRECT_ALT` assume technical translation the exec audience does not have. |
| 3 | User Control and Freedom | 2 | Modal has escape; a running scenario has no stop, and SSE close ends quietly. |
| 4 | Consistency and Standards | 3 | Strong visual system; the event-card side-stripe exception leaks into synthesis blockquotes and modal dependency edges. |
| 5 | Error Prevention | 2 | Dropdown prevents invalid input; hot-add and network states have weak guardrails. |
| 6 | Recognition Rather Than Recall | 3 | Three-pane geography is visible; event meanings and clickable rows still require inference. |
| 7 | Flexibility and Efficiency | 1 | One rigid path. No shortcuts, no stop, no jump-to-active, no jump-to-synthesis. |
| 8 | Aesthetic and Minimalist Design | 2 | Calm palette works; first viewport has ~25 equal-weight signals competing for attention. |
| 9 | Error Recovery | 2 | Toasts exist; failures lack next-step copy; SSE transport close can leave no visible terminal explanation. |
| 10 | Help and Documentation | 1 | No legend for event types, agent states, or colors. The audience cannot decode without narration. |
| **Total** | | **21 / 40** | **Acceptable (lower half)** |

### Anti-Patterns Verdict

**LLM assessment**: Three-pane Flight Director's Console honors the cinematic-calm direction. Deep-navy palette is tinted toward Signal Blue, tier identity is consistent, raw payloads correctly hide behind `<details>`. No hero-metric template, no gradient text, no glassmorphism, no identical card grid. The aesthetic does not scream AI. The leak that does: the 3px colored left-stripe — earned by DESIGN.md as a deliberate single-context exception for the event timeline — is reused on `.pane.right .synthesis blockquote` (line 255) and `.modal .edge` (line 351), generalizing the very pattern the system carves out.

**Deterministic scan**: bundled detector unavailable (`Error: bundled detector not found`, exit 1) — recorded and not retried. Manual mechanical pass found:
- 3 side-stripe declarations > 1px: `.event` (carved out), `.synthesis blockquote` (not carved out), `.modal .edge` (not carved out, 7 color variants).
- 0 gradient-text, glassmorphism, hero-metric, identical-card-grid, modal-as-first-thought findings.
- 3 em-dash instances in user-visible copy: lines 551, 704, 785.
- `#ffffff` at lines 228, 336; `color: white` at lines 61, 393 — bypassing the token system.
- Z-index inversion: toast `z-index: 10000` stacks above modal `z-index: 1000`. Mechanical bug.

**Visual overlays**: not available — FastAPI trace UI was not running.

### Overall Impression

The UI is a strong maintainer's console mis-framed as an audience's narrative. The architecture is correct and the visual system is calmer than its observability inspirations, but the screen is still tuned to a designer-at-60cm reader. The audience-from-3m reader — the one explicitly named as primary in PRODUCT.md — does not get the manager's plan as the protagonist; they get a vertical evidence log with metadata-heavy event cards in 10–13px type, no legend, and jargon that requires the presenter to translate. The single biggest opportunity is to promote the plan to a persistent top band and demote the event log to evidence underneath it — that one move would carry three of the five priority issues at once.

### What's Working

1. Three-pane geography: roster / timeline / synthesis is the right architecture for a watched demo; the fixed `280px · 1fr · 380px` grid lets the audience learn the layout in the first 30 seconds.
2. Tier color discipline: Plant Mint / Enterprise Violet are used as identity, never reassigned, and the active / used / hot-added agent states have meaningfully distinct visual treatments.
3. Payload depth without payload weight: raw JSON / SQL hides behind `<details>`, preserving developer-grade transparency without making the exec audience parse it.

### Priority Issues

1. **[P0] Parallelism reads as a serial log**
   The product's central claim is multi-agent dispatch. Today the center pane streams events vertically and the left rail shows only one active agent at a time, so concurrent calls look like sequence unless the presenter says "those three happened in parallel." For an audience that should follow the reasoning without narration, this is the demo's biggest unsupported claim.
   - Fix: Add a persistent manager-plan band above the timeline that visualizes the plan as a fan-out (manager → N agents, concurrent legs grouped). Allow multiple agent rows to pulse Signal Blue simultaneously when in flight. Group concurrent events into a single horizontal beat.
   - Suggested command: `/impeccable layout`

2. **[P0] No legend, exec-hostile jargon**
   "Magentic orchestration trace," "hop," "progress ledger," "task ledger," `NO_DIRECT_ALT`, raw scenario slugs (`supplier_risk_pm`) — none are decodable to a Manufacturing IT or plant ops leader on first viewing. No visible key for event-type colors, agent states, or tier badges. The audience that "should be able to follow the agent reasoning visually without narration" cannot, by definition, follow vocabulary they have never seen.
   - Fix: Replace technical labels with plain English (Magentic orchestration trace → "Live agent run"; hop → "Step"; ledger update → "Manager note"; `NO_DIRECT_ALT` → "No matching record"). Add a compact persistent legend (event types × agent states) somewhere the eye returns to.
   - Suggested command: `/impeccable clarify`

3. **[P1] "No data" and replan are underdramatic**
   PRODUCT.md Design Principle #4 says "Honest about uncertainty — first-class outcomes, not error states." Today a "no data" return looks visually identical to a successful agent response, and the manager's replan is buried inside `ledger_update` and `backtrack` event types. The lean-forward moment is currently a moment the audience would miss entirely.
   - Fix: Promote three named event treatments: "No matching rows" (distinct shape, not just amber color), "Manager replanning" (full-width banner inside the timeline, not a card), "New route chosen" (links the replan to the next agent_call). Pair shape with color.
   - Suggested command: `/impeccable clarify`

4. **[P1] Projector typography is sub-threshold for the story layer**
   At 3m from a projector, 10px type chips, 10px agent-project labels, 11px sequence numbers and timestamps, and 9.5px modal kind-tags will read as colored blocks, not type. The 13px body of event messages is borderline.
   - Fix: Promote what carries the story — event message → 15–16px, agent name → 15px, event-type chip → 12px minimum. Demote what is reference — timestamps and seq numbers stay 11–12px mono but shift to Text Dim.
   - Suggested command: `/impeccable typeset`

5. **[P1] The event-card side-stripe carve-out has leaked**
   DESIGN.md explicitly grants the 3px colored left-border to event cards as a single-context exception. The mechanical pass confirms the same pattern at `.synthesis blockquote` (line 255, Signal Blue) and `.modal .edge` (line 351, 7 color variants). Each unauthorized reuse weakens the deliberateness of the exception and re-opens the AI-slop signature DESIGN.md set out to avoid.
   - Fix: Replace the synthesis blockquote left-stripe with a full subtle border + tinted background (or no border, just left-padding + italic). Replace the modal dependency edges with leading colored pills or kind-tag chips.
   - Suggested command: `/impeccable polish`

6. **[P1] Z-index inversion: hot-add toast covers modal**
   `.hot-add-toast` is `z-index: 10000`; `.modal-backdrop` is `z-index: 1000`. If the demo hot-adds an agent while the blast-radius modal is open the toast will visibly occlude the modal.
   - Fix: Set modal stack to `z-index: 2000`, toast to `z-index: 3000`. Document the scale as tokens (`z-modal`, `z-toast`).
   - Suggested command: `/impeccable harden`

7. **[P1] The synthesis pane disappears entirely under 1100px**
   The single `@media (max-width: 1100px)` breakpoint drops the right pane (synthesis) and tightens the left rail to 240px. Under a hotel projector at non-standard resolution, the most-watched element of the demo vanishes.
   - Fix: At <1100px, do not hide synthesis — move it under the timeline as a full-width pane, or set a min-width and let the page horizontally scroll. Silent disappearance of the protagonist surface is the wrong default.
   - Suggested command: `/impeccable adapt`

### Persona Red Flags

**First-time exec watcher (Manufacturing IT director)**: Identifies three panes. Cannot tell "manager planned, three agents ran in parallel, one had no data, manager replanned" without the presenter saying it. Sees "Magentic," "hop," "ledger" and either guesses or tunes out. Reads the type chips as colored rectangles, not as types.

**Sam, accessibility-dependent / projector-distance user**: Status color paired with text or position in most places, but `--text-dim` on `--bg-elev` at 3.39:1 and on `--bg` at 3.72:1 (timestamps, seq numbers, agent project names) clears 3:1 large-text but not 4.5:1 body. From the back of the room those values read as gray fog. Live auto-scroll steals context with no reduced-motion fallback.

**Alex, presenter-power-user**: No stop/cancel on a running scenario, no keyboard shortcut for Run, no jump-to-latest, no jump-to-synthesis, no filter-by-agent. The trace UI is well-instrumented for watching, under-instrumented for driving.

**Microsoft seller running the demo**: Stable controls and great hot-add affordance, but lacks (a) visible fallback when SSE closes silently, (b) big "run complete" terminal state, (c) presenter-friendly highlighting for the current story beat, (d) graceful path when synthesis renders slowly or empty.

### Minor Observations

- `marked@12.0.2` loads from `cdn.jsdelivr.net` at line 8. Locked-down conference network or offline venue will silently break the synthesis pane's markdown. Self-host or inline.
- `color: white` at lines 61, 393, plus `#ffffff` at lines 228, 336 contradict the system's "never `#000`, never `#fff`" doctrine. Promote to `--text-strong` token tinted toward Signal Blue.
- Header gradient `#131a30 → #1a2240` (line 38) is decorative and meaning-free; the brand-dot glow already carries the "system is live" signal.
- Error toast uses Coral fill with white text (line 393), louder than the rest of the system which uses status color as outline + tinted background.
- Active-agent state (Signal Blue background + border + ring shadow, lines 100–103) has no accompanying label text; only difference between "active" and "used" is hue. Pair with a tiny "running" tag.

### Questions to Consider

- What if the manager plan were a persistent top band, and the event log became evidence underneath it?
- What if "no data" were treated as the hero proof of grounded AI, not as a quiet response card?
- If the presenter stopped speaking for 15 seconds during the cross-functional scenario, what would the audience understand from the UI alone?
