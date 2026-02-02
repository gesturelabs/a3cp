# GestureLabs Component Specification (Minimal Anthropic-Style Set)

This document defines **7 reusable layout components** for the GestureLabs website.
Each component contains a purpose statement, required content slots, optional slots, and structural notes.
All definitions are raw, literal Markdown — no styling, no HTML, no Tailwind.

---

## 1. HeroSection

### Purpose
Top-of-page introduction block with large headline, short explanation, CTA buttons, and optional illustration.

### Content Slots (Required)
- `title` — main headline (1–3 lines)
- `subtitle` — short descriptive paragraph
- `primary_cta_label`
- `primary_cta_href`

### Content Slots (Optional)
- `secondary_cta_label`
- `secondary_cta_href`
- `eyebrow` — small label above the title
- `illustration` — image or SVG reference

### Structural Notes
- Two-column layout on desktop (text left, illustration right)
- Stacked layout on mobile
- Very large spacing top and bottom
- Title weight is the primary focal element

---

## 2. CenteredTextBlock

### Purpose
A short, centered emphasis block used to transition sections or highlight values/ethics.

### Content Slots (Required)
- `headline` — centered main sentence

### Content Slots (Optional)
- `subheadline` — centered paragraph
- `eyebrow`

### Structural Notes
- Max width ~700px
- Centered text, generous vertical spacing
- No media or buttons

---

## 3. ThreeCardRow

### Purpose
A row of three tiles representing categories, principles, or major topics.

### Content Slots (Per Card)
- `icon`
- `title`
- `description`
- `href`

### Structural Notes
- Three columns on desktop, stacked on mobile
- Soft pastel backgrounds or light cards
- Used to organize content into clear thematic groups

---

## 4. FeatureBanner

### Purpose
A full-width highlighted banner for major sections like “Build with A3CP” or “A3CP for Institutions”.

### Content Slots (Required)
- `title`
- `description`
- `cta_label`
- `cta_href`

### Content Slots (Optional)
- `illustration`
- `background_color`

### Structural Notes
- Large rounded rectangle
- Text on the left, illustration on the right
- High visual weight, but below the HeroSection

---

## 5. NarrativeBlock

### Purpose
A storytelling block combining a visual element, a quote or key message, and a short narrative.

### Content Slots (Required)
- `media` — image or video thumbnail
- `quote`
- `headline`
- `body` — 1–3 paragraphs

### Content Slots (Optional)
- `orientation` (media-left or media-right)

### Structural Notes
- Two-column layout with emphasis on readability
- Designed to add human context or mission framing

---

## 6. ResourceList

### Purpose
A simple list of documents, articles, or updates.

### Content Slots
- `section_title`
- `items` (list of objects):
  - `title`
  - `category`
  - `date`
  - `href`

### Structural Notes
- Minimal table-like structure
- Useful for Docs landing, Home "Featured", or research lists

---

## 7. CTA_Band

### Purpose
A full-width band prompting the user to take an action (e.g., “Join our pilot program”).

### Content Slots (Required)
- `headline`
- `primary_cta_label`
- `primary_cta_href`

### Content Slots (Optional)
- `secondary_cta_label`
- `secondary_cta_href`
- `subtext`

### Structural Notes
- Centered text
- Large spacing
- Typically near bottom of page

---

# End of Component Specification
