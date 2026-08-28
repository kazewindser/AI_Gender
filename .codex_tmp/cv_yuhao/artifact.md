# Yuhao Fu CV template contract

## Reference

- Retained reference: `/Users/minifu/Project/AI_Gender/.codex_tmp/cv_yuhao/template.docx`
- SHA-256: `c5649e4918c3e2812790b40cf5d9cd6c69cb8d534b455d59799d969181c9c5f4`
- Render evidence: `reference-render/page-1.png`, `reference-render/page-2.png`
- Two rendered pages, one Word section.

## Page system

- A4 portrait, 8.27 x 11.69 inches.
- Margins: 1.25 inches left/right and 1.00 inch top/bottom.
- One column; no visible header, footer, page number, table, image, or recurring page furniture.
- The new CV may contract to one page because the user has one position, one degree, and one publication.

## Typography and components

- Century throughout; approximately 10.5 pt body text.
- Name: source `Heading` role, bold, left aligned.
- Identity block: three compact body lines immediately below the name.
- Section headings: source `Heading 5` role, bold, left aligned, with a blank paragraph separating sections.
- Entries: source `Normal` role. Dates appear first; continuation/detail lines use the source half-inch first-line/tab indentation pattern.
- Publication: use Century at the source body size, hanging indentation, italic journal title, and no list marker because there is only one item.

## Content flow and slot map

1. Identity block: replace name, title, school, and university.
2. `Professional Position`: rename to `Current Position`; replace the full employment history with the current doctoral appointment and start date.
3. `Education`: retain only the user's highest completed degree, as explicitly requested.
4. `Selected Journal Publications since 2023`: rename to `Journal Publication`; replace the list with the user's sole paper and DOI.
5. `Honors, Fellowships, and Research Funding`: include the user's competitively selected JST SPRING doctoral fellowship and research support for 2024–Present. Do not label the user as PI.

## Package preservation and fidelity gates

- Preserve the original section geometry, styles, numbering definitions, theme, settings, and relationships from the converted reference.
- Replace only `word/document.xml` body content through the document object model; preserve all other package parts.
- Confirm one clean page, no clipping or unexpected wrap, consistent Century typography, recognizable source-derived hierarchy, and unchanged page geometry.
