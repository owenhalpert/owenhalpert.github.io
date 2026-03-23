#!/usr/bin/env python3
"""
Simple blog generator that converts markdown files to HTML.
Usage: python3 generate_blog.py
"""

import os
import re
from datetime import datetime
from html import escape
from pathlib import Path

try:
    import markdown
except ImportError:
    print("Installing markdown library...")
    os.system("pip3 install markdown")
    import markdown

DATE_FORMAT = '%Y-%m-%d'

# Matches <img> with alt/src in either order
IMG_PATTERN = re.compile(
    r'<img\s+(?:alt="(?P<alt>[^"]+)"\s+src="(?P<src1>[^"]+)"|src="(?P<src2>[^"]+)"\s+alt="(?P<alt2>[^"]+)")\s*/>',
)
WEBP_PATTERN = re.compile(r'\.(png|jpg|jpeg)$', re.IGNORECASE)


def parse_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return {}, content

    frontmatter_text = match.group(1)
    body = match.group(2)

    frontmatter = {}
    for line in frontmatter_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    return frontmatter, body


def add_image_captions(html_content):
    """Convert img tags to figure tags with captions from alt text."""
    def replace_img(match):
        alt_text = match.group('alt') or match.group('alt2')
        src = match.group('src1') or match.group('src2')
        webp_src = WEBP_PATTERN.sub('.webp', src)
        return (
            f'<figure>'
            f'<picture>'
            f'<source srcset="{webp_src}" type="image/webp">'
            f'<img src="{src}" alt="{alt_text}">'
            f'</picture>'
            f'<figcaption>{alt_text}</figcaption>'
            f'</figure>'
        )

    return IMG_PATTERN.sub(replace_img, html_content)


def generate_post_html(title, date, content):
    """Generate HTML for a blog post with site styling."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)} - Owen Halpert</title>
    <style>
        *, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Helvetica Neue', Helvetica, 'Segoe UI', Arial, sans-serif;
            background: #fff;
            color: #111;
            font-size: 15px;
            line-height: 1.6;
            max-width: 680px;
            margin: 60px auto;
            padding: 0 24px;
        }}
        .back-link {{
            font-size: 0.8rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 40px;
            display: block;
        }}
        a {{ color: #111; text-decoration: none; }}
        a:hover {{ text-decoration: underline; text-underline-offset: 3px; }}
        h1 {{
            font-size: 1.5rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            line-height: 1.25;
            margin-bottom: 6px;
        }}
        .date {{
            font-size: 0.75rem;
            color: #888;
            font-variant-numeric: tabular-nums;
            margin-bottom: 36px;
        }}
        p {{ margin-bottom: 1.2em; }}
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9em;
        }}
        pre {{
            background: #f4f4f4;
            padding: 16px;
            border-radius: 4px;
            overflow-x: auto;
            margin-bottom: 1.2em;
        }}
        pre code {{ background: transparent; padding: 0; }}
        figure {{ margin: 32px 0; text-align: center; }}
        figure img {{ max-width: 100%; height: auto; }}
        figcaption {{ color: #888; font-size: 0.85em; margin-top: 8px; }}
    </style>
</head>
<body>
    <a class="back-link" href="/">← Owen Halpert</a>
    <h1>{escape(title)}</h1>
    <div class="date">{escape(date)}</div>
    <div class="content">
        {content}
    </div>
</body>
</html>
"""


def main():
    posts_dir = Path("posts")
    blog_dir = Path("blog")

    posts_dir.mkdir(exist_ok=True)
    blog_dir.mkdir(exist_ok=True)

    posts = []
    md = markdown.Markdown(extensions=['fenced_code', 'codehilite'])

    for md_file in posts_dir.glob("*.md"):
        print(f"Processing {md_file.name}...")

        with open(md_file, 'r') as f:
            content = f.read()

        frontmatter, body = parse_frontmatter(content)

        title = frontmatter.get('title', md_file.stem.replace('-', ' ').title())
        date = frontmatter.get('date', datetime.now().strftime(DATE_FORMAT))
        slug = md_file.stem

        html_content = md.convert(body)
        md.reset()

        html_content = add_image_captions(html_content)
        full_html = generate_post_html(title, date, html_content)

        output_file = blog_dir / f"{slug}.html"
        with open(output_file, 'w') as f:
            f.write(full_html)

        print(f"  → Generated {output_file}")

        posts.append({
            'title': title,
            'date': date,
            'slug': slug,
            'date_obj': datetime.strptime(date, DATE_FORMAT)
        })

    posts.sort(key=lambda x: x['date_obj'], reverse=True)
    print(f"\n✓ Blog generation complete! ({len(posts)} post(s))")


if __name__ == "__main__":
    main()
