# Product

## Register

product

## Users

**Primary (during a live demo)**: Manufacturing IT leaders and plant-operations leadership watching a ~25-minute presentation. They are seeing the system for the first time, looking at a projector or shared screen from across a conference room. They are not operating the UI themselves. They need to follow the agent reasoning — plan, dispatch, hop, replan, synthesis — without the presenter narrating every pixel.

**Secondary (presenter)**: A Microsoft seller / solution engineer driving the run-of-show in `docs/demo/run-of-show.md`. They have rehearsed; they need the UI to keep up with their story beats and survive the inevitable network hiccup or empty result.

**Tertiary (developer)**: The maintainer (you) debugging scenarios between demos. This audience does not get to override choices that hurt the primary one.

## Product Purpose

Make a Magentic multi-agent run *watchable*. The trace UI exists to prove — visually, in real time — that a Foundry-hosted manager can decompose a real plant-floor question, dispatch the right specialists from a portal-managed agent pool, ground each one in a Foundry IQ knowledge base mixing docs and live Azure SQL, and synthesize a row-truthful answer. Success means an exec who has never seen Agent Framework can, after one demo, describe what they just watched in their own words: "the manager planned, three agents ran in parallel, one had no data, the manager replanned, then it answered."

The trace UI is not a general-purpose observability tool. It is a narrative surface tuned for one ~25-minute story.

## Brand Personality

**Three words**: calm, cinematic, transparent.

**Voice**: confident technical, never breathless. The interface does not need to convince anyone that AI is impressive — the trace itself does that. Copy is precise and short; counts are tabular; status colors are restrained.

**Emotional goal**: the moment the manager replans after an agent returns "no data," the audience should lean forward, not squint. The UI should feel like a flight director's console during a calm launch — every signal is in its expected place, nothing is shouting, but everything important is unmissable.

**Reference direction**: Datadog APM flame charts and Honeycomb trace views, *deliberately calmer and more legible at projector distance*. Borrow their information density and timeline thinking; reject their stimulant-grade color usage and developer-only density.

## Anti-references

- **Splunk / Kibana / Grafana log-wall**: dense rows of monochrome text scrolling past. The audience tunes out in 10 seconds.
- **Toy AI chat demos** (ChatGPT-style bubble UI, single column of long messages): hides the parallelism and the *plan*, which is the whole story.
- **SaaS marketing dashboards** (hero-metric template, gradient cards, big number / small label / supporting stats): wrong register entirely; reads as sales theater, not engineering.
- **Side-stripe-border alert cards** with color-coded left borders. Banned by the parent skill anyway, but worth naming.
- **Dark-because-cool**. The dark theme here is justified by the physical scene (conference room, projector, presenter focal point), not by aesthetic reflex. If the demo ever moved to a printed handout, the answer would change.

## Design Principles

1. **Readable across the room before pretty up close.** Every type-size, contrast, and density decision is judged from ~3m, not from a designer's 60cm. If a label needs a presenter to read it aloud, it failed.
2. **Show the plan, not just the logs.** The manager's plan and replans are the protagonist of the story; tool calls and SQL rows are supporting evidence. Layout and visual weight should reflect that hierarchy, not the order events arrived on the SSE stream.
3. **Calm under load.** When ten events arrive in two seconds, the UI must absorb them without strobing, jumping, or burying the manager's last narration. Motion serves comprehension; it never competes for attention.
4. **Honest about uncertainty.** "No data," refusals, and replans are first-class outcomes, not error states. The UI treats them as part of the story, not as something to apologize for.
5. **One file, one machine, no surprises.** The trace UI is intentionally a single static HTML file served by FastAPI. Resilience comes from simplicity, not from a framework. Future work earns its complexity.

## Accessibility & Inclusion

No formal WCAG target. This is an internal demo running on a known projector + laptop combination, not a shipped product. That said:

- **Projector legibility is a hard requirement** and overlaps heavily with WCAG AA contrast; satisfy it for that reason, not for compliance.
- **Status colors** (success / warn / danger / plant-tier / enterprise-tier) appear repeatedly and must remain distinguishable to the most common color-vision deficiencies. Pair color with shape, label, or position — never color alone.
- **Reduced motion** is not currently respected; the critique should flag it only if motion choices are genuinely problematic, not as a generic checkbox.
- Screen-reader parity, keyboard-only navigation, and i18n are explicitly out of scope.
