---
name: ppt-incremental-content-update
description: Incrementally update an existing local PPTX with new product content while preserving the original slide template, chapter hierarchy, visual language, and data-evidence boundaries. Use for adding new product cases, data-validation pages, or linked wording updates to an established presentation.
description_zh: 增量更新现有PPT
description_en: Incremental PPT update
disable: false
agent_created: true
---

# ppt-incremental-content-update

## When to use

Use this skill when a user asks to add or revise content in an existing local PPTX, especially when:

- New product capabilities must be inserted into an existing narrative rather than appended arbitrarily.
- The new content must reuse existing visual templates and chapter styles.
- Product claims need clear separation between launched facts, measured results, and future exploration.
- The user requires a reviewable HTML preview in addition to the updated PPTX.

## Steps

1. Load `tencent-docs-routing`, then `tencent-local-office-edit`, and read `slide.md` before content work.
2. Read the complete slide structure with `slide_get_info` and `slide_get_page_info`; identify the narrative chapter, adjacent slides, and reusable template slide.
3. State the insertion logic before editing: define what the new slide proves, its chapter placement, and any linked slides whose wording must change.
4. Duplicate the closest existing template slide with `slide_duplicate_slide`; insert it at the correct index instead of creating an unrelated visual format.
5. Update content using `slide_set_text`. Keep titles concise, use user-facing language, and distinguish:
   - launched/current practice;
   - measured data validation;
   - future or planned exploration.
6. If the new page needs a new data block, remove irrelevant inherited images and add only simple shapes and text that match the deck's existing color and spacing system. Do not invent metrics; label missing values as data to be supplemented.
7. Update any necessary upstream/downstream links. For example, a newly launched multiplayer mode should be referenced in the capability-evolution page and reflected in the future-exploration page as an existing starting point, not a hypothesis.
8. Save the PPTX with `save_file`, verify `is_dirty=false` and slide count, then refresh the single-file HTML preview using `G:\workclaw\build_ppt_html_preview.py`.

## Pitfalls

- Do not add a new design language, chapter cover, or unrelated visual system when the user asks for consistency with the existing deck.
- Do not describe launched content as a future possibility, or describe planned work as validated impact.
- Do not position an AI feature as a blanket solution when it only targets a specific subpopulation; state the existing system coverage and the precise gap being addressed.
- Do not claim an industry first/blank-space position without verifiable external evidence; use "frontier exploration" or equivalent instead.
- After duplicating slides, page indexes and shape IDs change. Re-read relevant pages before writing text.
- Avoid AI-sounding verbs such as "铸造", and abstract nouns such as "交互模态" when simpler product language is available.

## Verification

- Confirm the PPTX opens and `slide_get_info` reports `is_dirty=false`.
- Confirm slide count includes every expected new page.
- Read back all inserted and linked slides with `slide_get_page_info`.
- Confirm the HTML preview includes the same slide count as the PPTX.
- Present both the refreshed HTML preview and updated PPTX to the user.
