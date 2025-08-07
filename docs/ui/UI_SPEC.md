============================================================
 A3CP WEBSITE DESIGN SPECIFICATION
============================================================

Version: 1.0
Date: 2025-08-07
Audience: UI/UX Designer
Goal: Improve the visual design and usability of the A3CP website

------------------------------------------------------------
 OVERVIEW
------------------------------------------------------------

A3CP (Ability-Adaptive Augmentative Communication Platform) is an
open-source system for multimodal communication support. This site
introduces the project and provides access to an interactive
demonstrator for researchers, caregivers, and funders.

The website must be:
  • Clear, accessible, and professional
  • Modular and easy to extend (e.g. add video or donation pages)
  • Technically credible for funders and collaborators
  • Mobile-first, works on tablet and desktop

------------------------------------------------------------
 CURRENT PAGES
------------------------------------------------------------

[ Home ]           → Landing page for general visitors
[ Demonstrator ]   → Interactive prototype (gesture/sound/etc.)
[ Docs ]           → Technical + user documentation
[ About ]          → Project overview, team, contact

Future (optional):
[ Donate ]         → Link to OpenCollective or similar
[ Join / Contribute ] → Contributor guidelines, GitHub link
[ Partners ]       → EU, grant, or institutional collaborators

------------------------------------------------------------
 GLOBAL NAVIGATION BAR (TOP OF PAGE)
------------------------------------------------------------

+----------------------------------------------+
| A3CP Logo |  Home  Demonstrator  Docs  About |
+----------------------------------------------+

Mobile:
- Collapsible hamburger menu
- Use sticky nav for mobile scroll

------------------------------------------------------------
 HOME PAGE
------------------------------------------------------------

Goal: Communicate mission and invite exploration

Sections:
  1. Hero Banner
     - Short tagline: e.g. "Communication without barriers."
     - Button: [ Try the Demonstrator ] or [ Learn More ]

  2. What is A3CP?
     - 1–2 paragraph summary
     - Emphasize inclusive tech, multimodal AI, non-verbal support

  3. Who It's For
     - Icons or sections for:
       • Families
       • Educators
       • Researchers
       • Clinicians

  4. Key Features
     - Short cards with icons:
       • Multimodal input (gesture, sound, speech)
       • Personalized training
       • Open source + auditable
       • Supports caregivers

  5. Call to Action
     - [ Try the Demonstrator ]
     - [ Read the Docs ]
     - [ Contact Us ]

------------------------------------------------------------
 VISUAL STYLE / TONE
------------------------------------------------------------

- Clean, modern, quiet confidence
- Focus on usability and trust
- Avoid overly corporate or techy aesthetics
- Accessibility: high contrast, large touch targets
- Layout: grid-based, mobile-first responsive design

Typography:
  - System font stack or Inter / Roboto
  - Optional monospace (e.g. Courier) for live demo areas

Color Palette (suggestion):
  - Soft neutrals + bold accent (e.g. navy + coral, or gray + teal)

Imagery:
  - Avoid stock photos where possible
  - Favor iconography, diagrams, animated feedback
  - Real photos (if used) must reflect diverse users

------------------------------------------------------------
 DEMONSTRATOR PAGE
------------------------------------------------------------

Purpose: Provide access to 3-tab live interface:
  [ Record Action ] [ Train Model ] [ Try It ]

UI should be embedded directly or linked:
  → Design should communicate this is an interactive prototype
  → Add explainer section above the tabs (optional)

------------------------------------------------------------
 DOCS PAGE
------------------------------------------------------------

Simple markdown-style layout:
  - Table of contents on left (or collapsible nav)
  - Main content area on right
  - Support code snippets, diagrams, schemas

Optional: use tabbed or sidebar layout for:
  • "Developer Docs"
  • "User Guide"
  • "API Reference"

------------------------------------------------------------
 ABOUT PAGE
------------------------------------------------------------

Content:
  - Short history of the project
  - Mission + values (inclusion, ethics, openness)
  - Team members or contributors
  - Contact info or form

Optional:
  - Logos of supporting institutions
  - License / open source notice

------------------------------------------------------------
 FOOTER
------------------------------------------------------------

+------------------------------------------------------------+
| A3CP is an open-source project by GestureLabs e.V.         |
| [ GitHub ] [ Contact ] [ License ]                         |
+------------------------------------------------------------+

------------------------------------------------------------
 DESIGN DELIVERABLES
------------------------------------------------------------

- Figma layout or responsive design mockups
- Mobile and desktop versions of each page
- Component styles:
    • Header
    • Button variants
    • Card / section layout
    • Tabbed demo panel

- Reusable color + typography styles
- Optional: design system for future expansion

============================================================
