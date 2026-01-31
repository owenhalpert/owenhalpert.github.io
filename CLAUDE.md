# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a personal website hosted on GitHub Pages (owenhalpert.github.io) with a simple blog system. The site is intentionally minimal - a static HTML homepage with a Python-based blog generator that converts markdown posts to HTML.

## Architecture

### Site Structure
- `index.html` - Main landing page with two-column layout (personal info + projects/blog)
- `posts/` - Markdown source files for blog posts with YAML frontmatter
- `blog/` - Generated HTML blog posts (auto-created, do not edit directly)
- `static/` - Static assets (resume.pdf, images/)
- `generate_blog.py` - Blog generation script

### Blog System Flow
1. Write markdown files in `posts/` with YAML frontmatter (title, date)
2. Commit and push to main branch
3. GitHub Action automatically runs `generate_blog.py`
4. Script converts markdown to HTML with site styling and adds image captions
5. Script automatically updates the Blog section in `index.html` with post links
6. Generated files in `blog/` directory are deployed to GitHub Pages

Note: `blog/` is gitignored since it's generated in CI. You can run `python3 generate_blog.py` locally to preview changes.

### Styling Philosophy
- Georgia serif font, 1.6 line-height
- 67% max-width for readability
- Underlined h1 headings
- Blue links (#0066cc)
- Italic project descriptions with left margin
- Blog posts inherit the same styling system from `generate_blog.py` template

## Common Commands

### Blog Development
```bash
# Generate blog posts from markdown
python3 generate_blog.py

# The script will:
# - Create posts/ and blog/ directories if needed
# - Convert all .md files in posts/ to HTML in blog/
# - Auto-install markdown library if missing
# - Update index.html Blog section with newest posts first
```

### Deployment
Deployment is automatic via GitHub Actions (`.github/workflows/pages.yml`). Every push to main triggers:
1. Python setup and dependency installation (markdown library)
2. Blog generation via `generate_blog.py`
3. Static site deployment to GitHub Pages

## Key Implementation Notes

### Markdown Post Format
Posts in `posts/` should use this structure:
```markdown
---
title: Post Title
date: YYYY-MM-DD
---

Content in markdown...
```

### index.html Blog Section Updates
The `generate_blog.py` script uses regex to remove/replace the `<h2>Blog</h2>` section in `index.html`. It inserts the updated blog list before the Projects section, maintaining the site's manual structure while automating blog updates.

### Generated HTML Structure
Blog posts in `blog/` are complete standalone HTML files with:
- Inline CSS matching site styling
- Back link to home
- Title (h1, underlined)
- Date in italics
- Content converted from markdown (with code highlighting support)
