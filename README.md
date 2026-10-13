# Stacie’s teaching calendar

Calendar-first Grade 3 / Grade 4 teaching planner for October 13–December 18, 2026. The original `dist/index.html`, `app.js`, `data.js`, `style.css` and resource filenames are preserved.

## Use the calendar

Open `dist/index.html` in Safari or Chrome, keeping the entire dist folder together. Choose Week, Month or Nine weeks; open a subject on a dated card. The six pages share the same selected week. Light mode is the default; a chosen theme is saved on this device.

Each resource has a PDF download and an Open / print PDF link. All 108 PDFs are included under `dist/resources`. Parent outlines, individual daily lessons, weekly teaching maps, real-book guides, original student-facing printables for all nine shared books—with a dated student page for each teaching day, reusable picture cards, book-specific sequence or information mats, and a make-and-create page—Friday checks, classroom mats, grade records and blank progress-monitoring forms are included. Complete packets contain the revised component files. Week 1 uses the approved illustrated student packet as-is; the build script preserves that file while generating the remaining book-matched packs. Actual books and licensed curriculum lessons must be obtained separately.

## GitHub Pages

The included workflow publishes the existing dist folder. In repository Settings → Pages, select GitHub Actions as the source. Changes pushed to main then deploy automatically. Expected project URL after a successful deployment: https://danchronisterjr.github.io/stacie-classroom/

This is a static public teaching website. Printable student records are blank; it does not upload or store student scores or IEP data online. Actual IEP goals have not been supplied and are not invented.

## Alignment

64 subject-qualified TEKS entries were checked by code and wording against the TEA grade-level documents linked below. Capitalization and terminal punctuation are normalized. Informational text 9D(i) includes its introductory clause. Daily classroom targets are supported steps, not claims of complete TEKS mastery. Spelling words, exact spelling substandards, publisher lesson identifiers and Bridges placement require the teacher’s existing data.

- Grade 3: https://tea.texas.gov/curriculum-and-instruction/curriculum-standards/grade3-teks-062024.pdf
- Grade 4: https://tea.texas.gov/curriculum-and-instruction/curriculum-standards/grade4-teks-062024.pdf

The supplied dates and pacing remain intact: 42 school days, nine Friday checks, and science labs on October 23, November 6, November 20 and December 11. Confirm campus dates before distributing the family outline.

## Maintain the printable resources

Edit dist/data.js, then run `python3 scripts/make_pdfs.py` in an environment with reportlab and pypdf installed. The script rebuilds the book-specific student packs and all other PDFs from the calendar data, then combines the complete packets. No build step is needed to view or host the website.
