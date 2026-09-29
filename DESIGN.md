---
version: 1.0.0
name: Control Room Glass
description: Design system for OrchestrAI/FlowPilot — a cockpit for monitoring AI workflow execution. Dark glass surfaces over deep space, phosphor-cyan indicators, monospace numerics. Built for extended monitoring sessions.
---

# Control Room Glass

## Overview

OrchestrAI lets users watch AI workflows execute in real time: step timelines, approval queues,
tool outputs, status indicators. Users stare at this interface for extended periods. The design
system treats the screen like a **deep-space observatory console**: deep dark surfaces so the
eyes never meet a pure white, phosphor-cyan indicators that read as "active system," and
monospace numerals so data is scannable without cognitive overhead.

**Named direction: Control Room Glass** — the aesthetic of a sophisticated machine monitored
from a dim cockpit. Inspired by Bloomberg Terminal density, Luxon autopilot HUDs, and the
control panels at CERN's control room. Glass panels over deep space with electric-cyan active
elements and hairline structural borders.

**Gives up:** approachability for first-time visitors (the dark theme is intimidating), warmth
(no organic tones anywhere), and any sense of playfulness (this is a working instrument, not a
landing page — warmth comes from the landing page, not the app).

---

## Colors

Palette anchored to the color of a CRT phosphor at low intensity — a deep cyan-green that
exists in the space between teal and electric blue (approximately Pantone 3202 C). Neutrals
are carried from this hue with a blue-green undertone, so the entire dark surface feels like
looking at a screen in a dark room rather than a cold grey void.

All ramps built in OKLCH with perceptually even lightness steps, hue bent across each ramp
(+3° in tints toward blue, −2° in shades toward green), and chroma tapered toward both ends.

### Semantic Tokens

- **primary (#0F6B7A):** Deep teal — the system's native hue. Used for default interactive states,
  links, and secondary indicators. This is the color of the phosphor at rest.
- **tertiary (#00E5CC):** Electric cyan — the sole driver for primary actions, active status,
  live indicators, and the brand accent. Used on under 5% of the surface. This is the phosphor
  at full intensity. Bright enough to be the only thing your eyes find in a dark room.
- **error (#E54D4D):** Warm red — derived from the primary family by shifting hue 150° and
  increasing saturation. Never pure #FF0000. Reads as "system fault" not "stop sign."
- **success (#3DDC84):** Signal green — complementary to the error tone. Used for completed
  states and confirmations. Tinted toward cyan so it belongs to the same family.
- **warning (#F5A623):** Amber — the only warm tone in the system. Reserved for approval
  states and "needs attention." Stands out intentionally from the cool register.
- **surface (#0D1117):** Deep space — the page background. A near-black with a trace of blue
  undertone. Not pure black, not slate-900. This is the color of a screen in a dark room.
- **surface-elevated (#161B22):** Raised surface — cards, panels, modals. One tonal step above
  the base surface, distinguished by value not by shadow.
- **on-surface (#E6EDF3):** Primary text — high-contrast off-white with a blue undertone.
  Not pure white. Reads as "emitted light" on the dark surface.
- **on-surface-muted (#8B949E):** Secondary text — timestamps, labels, metadata. Tuned to
  WCAG AA against surface-elevated (4.6:1).
- **border (#30363D):** Hairline structural — 1px borders that define panel edges. Visible but
  never loud. The color of a faint grid line.
- **border-active (#0F6B7A):** Active border — used on focused inputs and selected items.
  Draws from primary at 30% opacity equivalent.

---

## Typography

Two typefaces, classified differently: **Space Grotesk** (geometric sans) for display and
UI chrome, **JetBrains Mono** (monospace) for all data, numerics, and code-like content.
This split exists because workflows are dense in numbers — run IDs, timestamps, step counts,
amounts — and monospace lets the eye scan without re-parsing character widths.

Space Grotesk is the open-source successor to the geometric sans used on 1970s instrument
panels. JetBrains Mono is the modern standard for developer tools, chosen specifically for its
tabular numerals and clear differentiation of l/1/I/O/0.

Modular scale: 1.25 ratio (≈ perfect fourth). Nine levels. Line height inversely proportional
to size. Optical tracking deliberate: negative on display sizes, positive on small caps labels.

| Role | Font | Size | Weight | Line Height | Tracking |
|------|------|------|--------|-------------|----------|
| display-xl | Space Grotesk | 48px | 700 | 1.05 | -0.03em |
| display-lg | Space Grotesk | 36px | 700 | 1.08 | -0.02em |
| display-md | Space Grotesk | 28px | 700 | 1.12 | -0.01em |
| headline | Space Grotesk | 22px | 600 | 1.2 | 0 |
| title | Space Grotesk | 18px | 600 | 1.3 | 0 |
| body-lg | Space Grotesk | 17px | 400 | 1.6 | 0 |
| body-md | Space Grotesk | 15px | 400 | 1.55 | 0 |
| body-sm | Space Grotesk | 13px | 400 | 1.5 | 0 |
| label-caps | JetBrains Mono | 11px | 500 | 1.4 | +0.1em |
| label | Space Grotesk | 12px | 500 | 1.3 | 0 |
| mono-sm | JetBrains Mono | 12px | 400 | 1.5 | 0 |
| mono-xs | JetBrains Mono | 11px | 400 | 1.4 | 0 |

**Fallback stacks:**
- Space Grotesk: `'Space Grotesk', 'Geist', system-ui, sans-serif`
- JetBrains Mono: `'JetBrains Mono', 'Geist Mono', 'SF Mono', monospace`

---

## Layout

**Grid:** 12-column, 24px gutters. Content constrained to 1280px on desktop, full-bleed on
mobile with 16px gutters. The dashboard uses a masonry-like card layout within the grid —
not a rigid row system — because workflow data varies in density.

**Spacing base:** 4px. All spacing tokens are multiples of 4. This matches the grid gutter
(24px = 6×4) and keeps rhythm between layout and component internals.

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Tight inline gaps, icon-to-label |
| sm | 8px | Card internal padding, list item spacing |
| md | 16px | Standard component padding, section gaps |
| lg | 32px | Section spacing, card gaps in grid |
| xl | 64px | Page-level vertical rhythm |

**Density posture:** Information-dense by default. The app is a monitoring instrument, not
a marketing page. Users should see more data per screen, with hierarchy conveyed through
size and weight rather than whitespace. The landing page (separate from the app) uses a
more generous editorial layout.

**Measure:** Body text at 68ch max. Monospace numerics at 40ch max before wrapping.

---

## Elevation & Depth

No shadows. Depth is conveyed through tonal shift, 1px hairline borders, and spacing alone.
This matches the "control room" metaphor — instruments are flush panels, not floating cards.

**Surface hierarchy (tonal):**
- Level 0: `surface` (#0D1117) — page background
- Level 1: `surface-elevated` (#161B22) — cards, panels, dropdowns
- Level 2: `surface-overlay` (#1C2128) — modals, tooltips, popovers

**Overlays:** When a modal or tooltip appears, it uses `surface-overlay` with a 1px border
in `border` (#30363D). The modal background has `backdrop-filter: blur(12px)` and
`background: rgba(22, 27, 34, 0.85)` — this is the "glass" in Control Room Glass. It's
subtle: 85% opacity, not frosted. Enough to read what's behind, not enough to be distracting.

**No box-shadows anywhere.** If something needs to feel "above," it gets a brighter surface
and a border. The exception is the global loading state, which may use a single focused glow
in tertiary at 15% opacity behind the spinner.

---

## Shapes

Border radius is hierarchical, not uniform. Different elements have different personalities.

| Token | Value | Usage |
|-------|-------|-------|
| none | 0px | Status chips, table cells, code blocks |
| sm | 4px | Buttons, inputs, small interactive elements |
| md | 6px | Cards, panels, dropdown menus |
| lg | 8px | Modals, large containers |

**Border treatment:** All borders are 1px, color `#30363D` (border token), except:
- Active/focused elements: `border-active` (#0F6B7A at 60% opacity)
- Error states: `#E54D4D` at 60% opacity
- Glass panels: `border` at 40% opacity with the blur backdrop described above

No double borders. No inset shadows as border substitutes.

---

## Components

Components defined with `{colors.x}` / `{typography.y}` / `{rounded.z}` references.

### page
```yaml
backgroundColor: "{colors.surface}"
textColor: "{colors.on-surface}"
typography: "{typography.body-md}"
```

### card
```yaml
backgroundColor: "{colors.surface-elevated}"
textColor: "{colors.on-surface}"
typography: "{typography.body-md}"
rounded: "{rounded.md}"
padding: "{spacing.md}"
```
Cards sit on the surface with a hairline border. They are flat — no inner shadow, no gradient.
Elevation is tonal: surface-elevated vs surface.

### card-glass
```yaml
backgroundColor: "rgba(22, 27, 34, 0.75)"
textColor: "{colors.on-surface}"
typography: "{typography.body-md}"
rounded: "{rounded.md}"
padding: "{spacing.md}"
```
The signature glass panel. Used for the approval gate overlay and the run console timeline.
Background is 75% surface-elevated with `backdrop-filter: blur(16px)`. Border at 40% opacity.

### button-primary
```yaml
backgroundColor: "{colors.tertiary}"
textColor: "{colors.surface}"
typography: "{typography.label-caps}"
rounded: "{rounded.sm}"
padding: "{spacing.sm} {spacing.md}"
height: 40px
```
The one bright thing on the dark surface. Used for primary actions: "Run Workflow," "Approve."
Tertiary (#00E5CC) on surface (#0D1117) — contrast ratio 11.2:1, well above WCAG AAA.

### button-primary-hover
```yaml
backgroundColor: "#33EAD4"
textColor: "{colors.surface}"
```
One step brighter on hover. No transition longer than 150ms.

### button-secondary
```yaml
backgroundColor: "{colors.surface-elevated}"
textColor: "{colors.primary}"
rounded: "{rounded.sm}"
padding: "{spacing.sm} {spacing.md}"
height: 40px"
```
Outlined — border in primary at 40% opacity, no fill. Used for secondary actions: "Back,"
"Cancel," "Reject."

### button-danger
```yaml
backgroundColor: "rgba(229, 77, 77, 0.12)"
textColor: "{colors.error}"
rounded: "{rounded.sm}"
padding: "{spacing.sm} {spacing.md}"
height: 40px"
```
Tinted danger — not a filled red button. The background is error at 12% opacity against
surface-elevated. Subtle but legible.

### input
```yaml
backgroundColor: "{colors.surface}"
textColor: "{colors.on-surface}"
rounded: "{rounded.sm}"
padding: "{spacing.sm} {spacing.md}"
```
Hairline border in `border` (#30363D). Focus ring in `border-active` (#0F6B7A) at 60% opacity.
No inner shadow.

### input-error
```yaml
backgroundColor: "{colors.surface}"
textColor: "{colors.error}"
borderColor: "{colors.error}"
```
Error state: border and text shift to error color. Background stays surface.

### badge-status
```yaml
backgroundColor: "{colors.surface-elevated}"
textColor: "{colors.primary}"
rounded: "{rounded.none}"
padding: "{spacing.xs} {spacing.sm}"
typography: "{typography.label-caps}"
```
Status chips (running, completed, failed, waiting_approval) are borderless label-caps with
a left-edge color indicator. No background fill — just text on the card surface.

### timeline-node
```yaml
backgroundColor: "{colors.surface}"
rounded: "{rounded.sm}"
padding: "{spacing.sm} {spacing.md}"
```
Execution timeline steps. Completed nodes get a left border in `{colors.tertiary}`.
Failed nodes get a left border in `{colors.error}`. Waiting nodes get a left border in
`#F5A623` (warning/amber).

### code
```yaml
backgroundColor: "{colors.surface}"
textColor: "{colors.on-surface-muted}"
typography: "{typography.mono-xs}"
rounded: "{rounded.sm}"
padding: "{spacing.xs} {spacing.sm}"
```
Inline code (tool names, run IDs, node IDs). JetBrains Mono at 11px on surface background
with 4px padding. Used for machine-readable identifiers throughout.

### code-block
```yaml
backgroundColor: "{colors.surface}"
textColor: "{colors.on-surface}"
typography: "{typography.mono-sm}"
rounded: "{rounded.md}"
padding: "{spacing.md}"
```
Multi-line code blocks (JSON context in approval gates). Slightly larger padding, same surface.

### tooltip
```yaml
backgroundColor: "{colors.surface-overlay}"
textColor: "{colors.on-surface}"
rounded: "{rounded.md}"
padding: "{spacing.sm}"
```
Floating tooltips use surface-overlay (#1C2128) with backdrop blur. Arrow pointing up,
1px border in `border`.

---

## Do's and Don'ts

- **Do** use tertiary (#00E5CC) for exactly three things: primary action buttons, active/selected states, and live status indicators. That's it.
- **Do** use JetBrains Mono for every identifier, number, timestamp, and code reference. If it's machine-readable, it's monospace.
- **Do** use tonal surfaces instead of shadows for elevation. If you need something to feel "above," brighten the surface and add a border.
- **Do** tint every neutral with the primary hue's undertone. Pure grey is forbidden in this system.
- **Do** keep the tertiary accent under 5% of total pixels. If you find yourself reaching for it on a label or an icon that isn't interactive, stop.
- **Do** use the landing page for warmth and approachability. The app itself is intentionally austere — it's an instrument, not a brochure.
- **Do** keep all transitions under 200ms. State changes should feel instantaneous; this is a monitoring tool, not a showcase.
- **Don't** introduce a second accent color. If something needs emphasis that isn't a primary action, use weight, size, or spacing — never a new hue.
- **Don't** use pure white (#FFFFFF) or pure black (#000000) anywhere in the app. The landing page may use off-white (#F7F5F2) for paper stock contrast, but the app stays in the deep-space register.
- **Don't** add decorative gradients, glows, or blur blobs. The glass effect is strictly functional: backdrop blur on overlays, nothing else.
- **Don't** use Inter, Poppins, Montserrat, or any geometric sans other than Space Grotesk. They all read as defaults.
- **Don't** use rounded-md on everything. Buttons get sm (4px), cards get md (6px), code blocks get md. One radius on everything is the `rounded-2xl` tell.
- **Don't** use shadow for elevation in the app. If a card needs to feel raised, it gets surface-elevated and a border. Shadows are for the landing page hero only.
- **Don't** use the warning amber (#F5A623) for anything other than "needs human attention" — approval states, pending items, blocked workflows. It's the only warm tone and it must stay rare.
- **Don't** put the tertiary accent on headings, dividers, or decorative elements. It is for actions and active states only.
