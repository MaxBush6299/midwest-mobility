---
name: MMC Demo Trace UI
description: Cinematic, calm, transparent trace surface for the Midwest Mobility multi-agent demo.
colors:
  bg-deep-space: "#0b1020"
  bg-console: "#131a30"
  bg-console-raised: "#1a2240"
  border-rail: "#243056"
  text-primary: "#e8ecf6"
  text-muted: "#8c9ab9"
  text-dim: "#5f6e91"
  accent-signal-blue: "#4f8cff"
  tier-plant-mint: "#5bd1c2"
  tier-enterprise-violet: "#c79bff"
  status-warn-amber: "#f4b740"
  status-danger-coral: "#ef6b6b"
  status-success-jade: "#4ad991"
typography:
  display:
    fontFamily: "Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "18px"
    fontWeight: 600
    lineHeight: 1.3
  headline:
    fontFamily: "Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "17px"
    fontWeight: 600
    lineHeight: 1.3
  title:
    fontFamily: "Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "15px"
    fontWeight: 600
    lineHeight: 1.3
  body:
    fontFamily: "Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.55
  label-eyebrow:
    fontFamily: "Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "11px"
    fontWeight: 600
    letterSpacing: "1.2px"
  mono:
    fontFamily: "Cascadia Mono, Consolas, SF Mono, ui-monospace, monospace"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.5
rounded:
  sm: "4px"
  md: "8px"
  lg: "10px"
spacing:
  xs: "6px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
components:
  button-primary:
    backgroundColor: "{colors.accent-signal-blue}"
    textColor: "#ffffff"
    rounded: "{rounded.md}"
    padding: "8px 12px"
  button-secondary:
    backgroundColor: "{colors.bg-console-raised}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.md}"
    padding: "8px 12px"
  agent-row:
    backgroundColor: "transparent"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.md}"
    padding: "8px 10px"
  event-card:
    backgroundColor: "{colors.bg-console}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.lg}"
    padding: "12px 14px"
  synthesis-pane:
    backgroundColor: "{colors.bg-console}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.lg}"
    padding: "18px 20px"
  scenario-card:
    backgroundColor: "{colors.bg-console-raised}"
    textColor: "{colors.text-muted}"
    rounded: "{rounded.lg}"
    padding: "14px"
  stat-chip:
    backgroundColor: "{colors.bg-console}"
    textColor: "{colors.text-muted}"
    rounded: "{rounded.md}"
    padding: "8px 12px"
---

# Design System: MMC Demo Trace UI

## 1. Overview

**Creative North Star: "The Flight Director's Console"**

This is mission control during a calm launch. Three rails of information — the roster on the left, the live timeline in the middle, the synthesis on the right — each one owning its job, none of them shouting. The audience watches the manager plan, dispatch, and replan from across a conference room, and the UI's job is to make that motion legible without a presenter narrating every label aloud.

The aesthetic borrows from observability culture (Datadog APM, Honeycomb traces, Azure Monitor) but rejects its stimulant-grade defaults. Saturation is restrained, motion is exponential and short, type sits big enough for the back row. The interface never tries to convince the audience that AI is impressive — the trace does that — so the chrome stays out of the way.

**Key Characteristics:**
- Deep-navy console palette, tinted toward the signal-blue accent (never `#000`, never neutral gray).
- Three-pane fixed grid; no nested cards, no decorative dividers.
- Color carries meaning: tier (plant vs enterprise), event type (call, response, replan, error), state (active, used, hot-added).
- Tabular numerics everywhere counts appear. Counts never jitter.
- Motion is reserved for new information arriving — never for decoration.

## 2. Colors

A deep-space navy ground tinted toward the signal-blue accent, with three saturated role colors (mint for plant tier, violet for enterprise tier, jade-amber-coral for success / warn / danger) used only where they carry meaning.

### Primary
- **Signal Blue** (`#4f8cff`): the manager's voice. Active agent borders, primary buttons, code accents in the synthesis pane, links. Reserved for "the system is talking to you right now."

### Secondary (tier identity)
- **Plant Mint** (`#5bd1c2`): identifies every Plant-7 agent on the roster and in event rows. Carries through wherever the plant tier shows up.
- **Enterprise Violet** (`#c79bff`): the same role for the enterprise tier.

### Tertiary (status)
- **Jade Success** (`#4ad991`): agent responded, run complete. Used on event-card type chips and the synthesis pane's gradient halo.
- **Amber Warn** (`#f4b740`): ledger updates, hot-added agents, manager replans. The "something interesting just happened" color.
- **Coral Danger** (`#ef6b6b`): backtracks and errors. Rare on purpose.

### Neutral (tinted toward Signal Blue)
- **Deep Space** (`#0b1020`): the trace pane and modal-content ground; the darkest surface.
- **Console** (`#131a30`): left + right rails, event cards, modals. One step elevated.
- **Console Raised** (`#1a2240`): controls, scenario card, stat chips, type-chip backgrounds. Two steps elevated.
- **Rail Border** (`#243056`): every divider and card edge. Single source of separation.
- **Text Primary** (`#e8ecf6`): body and emphasis text.
- **Text Muted** (`#8c9ab9`): metadata, secondary info, eyebrow labels.
- **Text Dim** (`#5f6e91`): timestamps, sequence numbers, inactive states.

### Named Rules

**The Meaning-Or-Mute Rule.** Saturated color (Signal Blue, Plant Mint, Enterprise Violet, Jade, Amber, Coral) appears only when it carries information. Decorative tints (gradients on the synthesis pane, the brand dot's glow, scenario-card accents) stay below `0.1` alpha. If you can't name the meaning, it's neutral.

**The Tier-Pair Rule.** Plant and Enterprise are always shown as a balanced pair — mint and violet, never one without the other implied. Never reassign these hues to other concepts.

## 3. Typography

**Display / Body Font:** Segoe UI, with system-ui and -apple-system fallbacks. Native on the demo machine (Windows), neutral enough to disappear, projector-friendly at standard weights.

**Mono Font:** Cascadia Mono, with Consolas / SF Mono / ui-monospace fallbacks. Reserved for sequence numbers, timestamps, raw payloads in `<details>`, and inline code in the synthesis pane.

**Character:** Functional and humanist, not editorial. The type's job is to vanish into the data; the surprise is that there is a system at all.

### Hierarchy
- **Display** (600, 18px, 1.3): empty-state heading in the trace pane.
- **Headline** (600, 17px, 1.3): top-level headings inside the synthesis pane (markdown `h1`).
- **Title** (600, 15px, 1.3): modal titles, synthesis `h2` (colored Signal Blue when it lands inside the synthesis pane).
- **Body** (400, 13px, 1.55): default for event content, agent rows, controls, scenario descriptions.
- **Label/Eyebrow** (600, 11px, uppercase, 1.2px tracking): pane titles ("AGENTS", "SCENARIOS"), scenario-card section labels.
- **Mono** (400, 12px, 1.5): timestamps, sequence indices, raw event payloads in `<details><pre>`, inline `code` in synthesis.

### Named Rules

**The Projector Rule.** Body text never drops below 12px. Anything that needs to be read from across a conference room runs at 13px or larger. Mono can sit at 11–12px because it's reference data, not narrative.

**The Type-As-Chrome Rule.** Headings inside the synthesis pane lift to Signal Blue at h2/h3 to anchor the structure; outside the synthesis pane, headings stay in Text Primary or Text Muted. The synthesis is the only place type carries color.

## 4. Elevation

Tonal layering, not shadows. Surfaces stack by lightness — Deep Space → Console → Console Raised → border — and the rare real shadow is reserved for things that genuinely float above the layout (modal, hot-add toast). The visual depth is generated by the contrast between adjacent surface tones, not by drop-shadows on every card.

### Shadow Vocabulary
- **Console drop** (`box-shadow: 0 4px 24px rgba(0,0,0,0.3)`): floating panels and the hot-add toast. Soft, far-cast.
- **Modal lift** (`box-shadow: 0 24px 64px rgba(0,0,0,0.6)`): the blast-radius modal. Deliberate weight; says "this is a focused moment."
- **Brand-dot glow** (`box-shadow: 0 0 12px var(--accent)`): the only decorative glow, on the 10px brand indicator. A single signal that the system is live.

### Named Rules

**The Flat-By-Default Rule.** Surfaces are flat at rest. Shadows appear only on (1) the modal, (2) the toast, and (3) the brand-dot glow. Event cards, agent rows, the synthesis pane, and the scenario card carry no shadow.

## 5. Components

### Buttons
- **Shape:** rounded-md (8px).
- **Primary** (`button.primary`): Signal Blue background, white text, 600 weight, 8×12 padding. Used for "Run scenario."
- **Secondary** (default `button`, `select`): Console Raised background, Text Primary, Rail Border outline. Hover lifts the border to Signal Blue, never changes the fill.
- **Hot-add** (dashed Amber border): the "introduce a new agent mid-run" affordance. The dashed border is the affordance — it says "this is provisional." Hover fills with a 15% Amber wash.
- **Hot-add reset**: solid Rail Border, Text Muted. Quiet, intentionally lower-status than the hot-add buttons themselves.

### Stat chips
Right-side header strip. Console background, Rail Border outline, 11–12px label with tabular-numeric strong value. Single source of run state ("Events: 12 · Hops: 3 · Duration: 14s"). Never split into cards; chips stay inline.

### Agent rows (left rail)
- **Shape:** rounded-md (8px), transparent border at rest.
- **Tier badge:** 8×8 circle, Plant Mint or Enterprise Violet. Always present.
- **Active state:** Signal Blue 15%-alpha background, Signal Blue border, +1px Signal Blue shadow ring. Loud on purpose — this is the agent the manager is talking to *right now*.
- **Used state:** Jade 8%-alpha background, no border. Quiet — the agent has contributed.
- **Hot-added state:** dashed Amber border, Amber 7%-alpha background, glowing Amber badge. Visually distinct from "active" because it tells a different story (new arrival vs current speaker).

### Event cards (center pane)
- **Shape:** rounded-lg (10px), Rail Border outline, Console background.
- **Left accent:** 3px colored left border keyed to event type (Signal Blue for agent_call, Jade for agent_response, Amber for ledger_update, Coral for backtrack/error). **This is intentional information density**, not decoration — the audience tracks the colored ribbon down the timeline to see the rhythm of plan → dispatch → replan.
- **Type chip:** uppercase, 600 weight, 10px, 0.6px tracking. Background matches the event-type accent (with Deep Space text on light chips for legibility).
- **Metadata row:** seq/hop/agent/timestamp in mono, Text Dim/Text Muted. Tabular-numeric.
- **Content block:** Deep Space background nested inside the card, 6px radius, 13px body. Pre-wrapped to preserve line breaks from agent output.
- **Raw payload:** collapsed inside `<details>`, opens to a scrollable 240px-max mono `<pre>`. The "show your work" affordance for the developer audience without burdening the demo audience.

### Synthesis pane (right rail)
The single most-watched element after the trace itself. Console background, very subtle Jade-to-transparent vertical gradient halo at the top (the "answer arrived" warmth), Rail Border outline. Renders markdown produced by the manager: headings lift to Signal Blue at h2/h3, body text runs at 13.5px / 1.6 line-height for reading comfort, tables and code blocks are first-class. The empty state runs centered, dim, italicized — "waiting for the manager."

### Scenario card (right rail footer)
Console Raised background, Rail Border outline, 14px padding. Eyebrow label (uppercase, tracked), title, description, code-styled scenario slug in Signal Blue. Lives below the synthesis as the "what you're watching" reference card.

### Modal (blast radius)
Centered, max-width 720px. Header strip in Console Raised carries the agent identity (Title weight + mono agent-id). Body in Console. Heavy lift shadow. Backdrop is the only place we use `rgba(8,12,24,0.72)` — a translucent darken of the underlying scene rather than a true black.

### Toast (hot-add confirmation)
Bottom-right, fixed. Console Raised background, Amber border, console-drop shadow. Pops in with the same exponential ease as event cards. 220ms, no bounce.

### Named Rules

**The Three-Pane Rule.** The grid is `280px 1fr 380px`. No accordion, no collapse, no tabs. Anyone walking up to the demo sees roster / timeline / synthesis at one glance.

**The Anchored-Action Rule.** Primary actions (Run, scenario picker, stat chips) live in the top header strip and never move. The audience learns where things are in the first 30 seconds; nothing reorganizes after that.

## 6. Do's and Don'ts

### Do:
- **Do** keep body text at 13px or larger so the back row of the conference room can read it.
- **Do** use Signal Blue **only** for the manager's voice (active agent, primary action, synthesis headings, links). Its scarcity is the signal.
- **Do** pair tier color with the agent's name and tier-badge position — never use Plant Mint or Enterprise Violet alone to identify a tier.
- **Do** use tabular-numeric for every count, sequence index, and timestamp. Numbers must not jitter as they update.
- **Do** treat "no data," refusals, and replans as first-class events with their own visual weight. Ledger updates get Amber; backtracks get Coral with a tinted background.
- **Do** keep the three-pane grid fixed. The audience learns the geography in the first 30 seconds.
- **Do** use exponential ease-out for the event-card pop (`220ms ease-out`, 4px translateY). Motion serves comprehension; arrival is the only thing animated.
- **Do** keep the mono font (Cascadia Mono) for everything that is reference data: timestamps, seq numbers, raw payloads, inline code.

### Don't:
- **Don't** introduce a fourth saturated color. The palette is locked at Signal Blue + Plant Mint + Enterprise Violet + Jade/Amber/Coral.
- **Don't** add `border-left` greater than 3px or repurpose the left-edge accent for cards outside the trace timeline. The event card's colored left border is a deliberate, single-context exception to the parent skill's side-stripe ban — earned because the audience reads the ribbon down the timeline. Do not generalize it.
- **Don't** add drop shadows to event cards, agent rows, the synthesis pane, or the scenario card. Tonal layering carries depth; the only shadows are modal, toast, and the brand-dot glow.
- **Don't** use `#000` or `#fff` anywhere. Body text is `#e8ecf6`; strong text inside the synthesis pane is allowed to push to `#ffffff` for emphasis weight only.
- **Don't** build a hero-metric template (big number / small label / supporting stats / gradient accent). The stat chips in the header strip are the only metric surface.
- **Don't** wrap cards inside cards. If a card needs internal structure, nest a `Deep Space` content block (see event-card content), not another bordered card.
- **Don't** add Splunk-style log-wall density: rows of monochrome mono text scrolling past. The center pane is a narrative timeline of typed events, not a tail.
- **Don't** use gradient text, `background-clip: text`, or decorative glassmorphism. The Jade halo on the synthesis pane is a soft fade, not a glass blur, and it's the only gradient in the system.
- **Don't** add bounce, elastic, or `ease-in-out` curves. Motion is exponential ease-out, short.
- **Don't** ship copy that restates a heading or fills empty states with marketing prose. Labels are precise and short.
