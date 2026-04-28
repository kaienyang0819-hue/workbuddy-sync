---
name: aippt-maker
description: >-
  Generate professional PowerPoint presentations locally. Use when the user asks
  to make a PPT, create slides, build a deck, generate a slideshow, design a
  keynote, make a presentation, or produce report/proposal materials. Also
  applies to incremental edits: modifying a single slide, changing theme or
  color scheme, adding or removing pages, or exporting existing content to
  .pptx. Trigger this skill for ANY slide or PPT creation and editing task.
---

# AI PPT Maker Skill

> [!IMPORTANT]
> ## Language & Communication Rule
>
> - **Response language**: Always match the language of the user's input. If the user writes in Chinese, respond in Chinese; if in English, respond in English.
> - **Explicit override**: If the user requests a specific language (e.g. "reply in English" / "请用中文回答"), use that language instead.

---

## Conventions

- **SKILL_DIR**: The directory containing this SKILL.md file.
- **`dist/export-pptx.mjs`** is a compiled bundle. Execute it directly with `node` — do NOT read it.

## Reference Documents

| Document | Path | When to Read |
|----------|------|--------------|
| Style Presets | `references/style-presets.md` | MUST read at Step 2 (Style Selection) |
| Research Collection Guide | `references/research-collection.md` | Read before generating `research.md` (Standard Path only) |
| HTML Technical Spec | `references/html-spec.md` | MUST read before generating any HTML slide |
| PPT Content Design Guide | `references/ppt-design.md` | Read when planning outline and `content_spec` |
| Slide Generation Guide | `references/slide-generation.md` | Read before Step 6 to choose serial vs. parallel mode |

---

## How It Works

This skill uses a **Research → HTML → PPTX** three-stage pipeline:

1. **`research.md` as the unified content layer** — Before drafting the outline, consolidate all content material into `<project_dir>/research.md`. This applies whether the source is web research results, user-provided files, or AI-organized knowledge. Downstream outline planning and HTML generation always pull from this file — never from context memory.

2. **`presentation.json` as the single source of truth** — Records the title, theme, per-slide metadata, and file mappings. All create/read/update/delete operations go through this file.

3. **HTML as the intermediate representation** — Each slide is a standalone HTML file (1280×720 canvas) using Tailwind CSS + Lucide icons. HTML is chosen because LLMs generate HTML/CSS naturally, visual expressiveness exceeds raw PPTX XML, and slides can be previewed in a browser.

4. **Per-slide isolated generation** — Each HTML file is generated independently. Style consistency is enforced through the `theme` field and post-generation consistency validation.

---

## Project File Structure

```
<project_dir>/
├── research.md          ← Content layer — single source for all slide content
├── presentation.json    ← State file — slide registry and metadata
├── preview.html         ← Auto-generated preview page (all slides)
└── slides/
    ├── slide_001.html
    ├── slide_002.html
    └── ...
```

### `presentation.json` Format

```json
{
  "title": "Presentation Title",
  "theme": "Natural-language style description (from preset or custom)",
  "slides": [
    {
      "file": "slide_001.html",
      "type": "title | section | content",
      "title": "Slide Title",
      "content_spec": "What this slide covers (see ppt-design.md). May use [ref: section-name] to anchor to research.md sections.",
      "local_theme": "Optional — special visual treatment for this slide only"
    }
  ]
}
```

- The **order** of the `slides` array defines slide order.
- `file` is a stable identifier — **never rename a file after creation**.
- Naming rule: `slide_<three-digit-index>.html` (e.g. `slide_001.html`). Indices are monotonically increasing and never reused.
- `content_spec` supports `[ref: section-name]` syntax to reference specific sections in `research.md`, reducing generation drift.

---

## `content_spec`: Slide Content Summary

`content_spec` describes **what specific points this slide presents** — list the topical directions, but leave the actual copy to be drawn from `research.md` at generation time.

- Supports `[ref: section-name]` anchor syntax to point to specific sections in research.md
- Core principle: say clearly "what this slide is about and how it is divided", without hard-coding copy or specifying layout.

See [references/ppt-design.md](references/ppt-design.md) for writing conventions and examples.

---

## Workflow

> [!CAUTION]
> ## Global Execution Discipline (MANDATORY)
>
> 1. **SERIAL EXECUTION** — Steps MUST be executed in order. Non-BLOCKING steps may proceed continuously.
> 2. **⛔ BLOCKING = HARD STOP** — Steps marked ⛔ BLOCKING require explicit user response. MUST NOT proceed without it.
> 3. **NO SPECULATIVE EXECUTION** — Pre-generating content for a later step while executing an earlier step is FORBIDDEN.
> 4. **GATE BEFORE ENTRY** — Each step's prerequisites MUST be verified before starting.
> 5. **DECLARE SUCCESS ONLY AFTER VERIFICATION**.

---

### Core Workflow (Full Generation)

---

#### Step 1: Gather Requirements

🚧 **GATE**: User has initiated a PPT creation request.

Ask the user about: topic, purpose, target audience, desired page count. Find out whether the user already has source material (existing document / file).

**Determine path:**
- User has a complete document/file → **Quick Path** (skip Step 3)
- User needs research or has only rough ideas → **Standard Path**

✅ **Checkpoint — Requirements understood, path determined. Proceed to Step 2.**

---

#### Step 2: Style Selection

🚧 **GATE**: Step 1 complete.

⛔ **BLOCKING**: Read [references/style-presets.md](references/style-presets.md) and present the 6 style presets to the user. Ask the user to:
- Pick a preset number (1-6), OR
- Describe a custom style

Wait for the user's choice.

After selection, generate **1 cover slide HTML** as a visual preview. Present it to the user for confirmation. If the user is not satisfied, offer to switch preset or adjust.

> ❌ **NEVER proceed to Step 3/4 before the user confirms the style.**

✅ **Checkpoint — Style confirmed. Proceed to Step 3 (Standard Path) or Step 4 (Quick Path).**

---

#### Step 3: Generate `research.md` (Standard Path only)

🚧 **GATE**: Step 2 complete; style confirmed. Only for Standard Path.

Read [references/research-collection.md](references/research-collection.md). Based on the user's situation, choose the appropriate mode:

| Mode | When to Use | Action |
|------|-------------|--------|
| **Web Research** | Topic involves recent data, industry trends | Call search tools to gather information |
| **Organize User Material** | User provided text, files, or documents | Format and structure — do not add or remove content |
| **AI-Organized Content** | General or evergreen topic | AI organizes content from existing knowledge |

Write all content to `<project_dir>/research.md`.

✅ **Checkpoint — `research.md` written. Proceed to Step 4.**

---

#### Step 3Q: Quick Path — Import Existing Document

🚧 **GATE**: Step 2 complete; style confirmed. Only for Quick Path (user has existing document).

Read the user's existing document and convert it into `<project_dir>/research.md`:
- Preserve original content structure and data — do NOT add or remove content
- Organize into clear sections with headings for easy reference in `content_spec`

✅ **Checkpoint — `research.md` written from existing document. Proceed to Step 4.**

---

#### Step 4: Plan Outline

🚧 **GATE**: Step 2/3 complete; `research.md` exists and contains content.

Read [references/ppt-design.md](references/ppt-design.md). Using content from `research.md`, design each slide's `type` / `title` / `content_spec`. Use `[ref: section-name]` anchors in content_spec where applicable.

✅ **Checkpoint — Outline planned. Proceed to Step 5.**

---

#### Step 5: Present Plan to User

🚧 **GATE**: Step 4 complete.

⛔ **BLOCKING**: Present the full outline (slide list + theme) to the user and wait for explicit confirmation.

> ❌ **NEVER proceed to Step 6 before receiving explicit user confirmation.**

✅ **Checkpoint — User confirmed. Proceed to Step 6.**

---

#### Step 6: Initialize & Generate Slides

🚧 **GATE**: Step 5 complete; user has confirmed the outline.

- Create `<project_dir>/slides/` directory.
- Write `<project_dir>/presentation.json`.
- Read [references/slide-generation.md](references/slide-generation.md) and [references/html-spec.md](references/html-spec.md).
- Generate each slide HTML with simultaneous reference to both `research.md` and the HTML spec.

✅ **Checkpoint — All slide HTML files generated. Proceed to Step 7.**

---

#### Step 7: Validate Icons

🚧 **GATE**: Step 6 complete; all HTML files exist.

```bash
node "$SKILL_DIR/scripts/validate-icons.mjs" "<project_dir>"
```

If output contains items flagged "⚠ recommend manual review", inspect those icons for semantic correctness.

✅ **Checkpoint — Icon validation complete. Proceed to Step 8.**

---

#### Step 8: Validate Consistency

🚧 **GATE**: Step 7 complete.

```bash
node "$SKILL_DIR/scripts/validate-consistency.mjs" "<project_dir>"
```

This script checks cross-slide consistency: tailwind.config colors, font declarations, border-radius values, icon sizes, text sizes. Fix any reported issues before proceeding.

✅ **Checkpoint — Consistency validation passed. Proceed to Step 9.**

---

#### Step 9: Preview & Confirm

🚧 **GATE**: Step 8 complete.

Generate a preview page showing all slides:

```bash
node "$SKILL_DIR/scripts/preview-all.mjs" "<project_dir>"
```

⛔ **BLOCKING**: Open `<project_dir>/preview.html` in the browser for the user to review. Wait for confirmation or change requests.

✅ **Checkpoint — User confirmed preview. Proceed to Step 10.**

---

#### Step 10: Export .pptx

🚧 **GATE**: Step 9 complete; user confirmed preview.

**Before first export**, check and install fonts:

```bash
node "$SKILL_DIR/scripts/check-fonts.mjs"           # check
node "$SKILL_DIR/scripts/check-fonts.mjs" --install  # install if not found
```

**Run export:**

```bash
node "$SKILL_DIR/dist/export-pptx.mjs" <project_dir> --output <output_path>
```

If export fails due to missing Playwright:

```bash
npm init -y && npm install playwright && npx playwright install chromium
```

Output filename format: `<title>_YYYYMMDD_HHmmss.pptx`.

✅ **Checkpoint — .pptx exported successfully. Workflow complete.**

---

### Incremental Edit Rules

When making partial changes to an existing project, select the relevant steps from the core workflow and follow these constraints:

**Filenames are immutable**: HTML filenames on disk are never renamed. Indices are monotonically increasing and never reused. New slides take max index + 1.

**Minimum-change principle**:

| Change Type | Operation |
|-------------|-----------|
| Text / numbers only | Direct string replacement |
| Style / color / layout only | Local edit — do not touch copy |
| Keep visuals, change copy | Replace text nodes only — preserve all class/style |
| Keep copy, change visuals | Preserve text content — freely restyle |
| Full redesign | Rewrite entire slide |

**Theme change**: Update `theme` in presentation.json, then rewrite all slides in "keep copy, change visuals" mode.

After any modification: sync `content_spec` in presentation.json → re-run icon validation → re-run consistency validation → regenerate preview → re-export .pptx.
