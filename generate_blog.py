#!/usr/bin/env python3
"""
Simple blog generator that converts markdown files to HTML.
Usage: python3 generate_blog.py
"""

import os
import re
from datetime import datetime
from pathlib import Path

try:
    import markdown
except ImportError:
    print("Installing markdown library...")
    os.system("pip3 install markdown")
    import markdown


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
    # Pattern to match img tags with alt text
    pattern = r'<img\s+alt="([^"]+)"\s+src="([^"]+)"\s*/>'

    def replace_img(match):
        alt_text = match.group(1)
        src = match.group(2)
        return f'<figure><img src="{src}" alt="{alt_text}"><figcaption>{alt_text}</figcaption></figure>'

    return re.sub(pattern, replace_img, html_content)


def generate_post_html(title, date, content):
    """Generate HTML for a blog post with site styling."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Owen Halpert</title>
    <style>
        body {{
            font-family: 'Georgia', serif;
            margin: 40px auto;
            line-height: 1.6;
            max-width: 67%;
        }}
        h1 {{
            margin-top: 10px;
            margin-bottom: 10px;
            font-weight: bold;
            font-size: 2.0em;
            text-decoration: underline;
        }}
        .date {{
            color: #666;
            font-style: italic;
            margin-bottom: 30px;
        }}
        .back-link {{
            margin-bottom: 30px;
        }}
        a {{
            color: #0066cc;
            text-decoration: none;
            font-size: 1.0em;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        figure {{
            margin: 30px 0;
            text-align: center;
        }}
        figure img {{
            max-width: 100%;
            height: auto;
        }}
        figcaption {{
            color: #666;
            font-style: italic;
            font-size: 0.9em;
            margin-top: 10px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="back-link">
        <a href="/">← Back to home</a>
    </div>
    <h1>{title}</h1>
    <div class="date">{date}</div>
    <div class="content">
        {content}
    </div>
</body>
</html>
"""


def update_index_html(posts):
    """Update index.html with blog posts list."""
    index_path = Path("index.html")

    with open(index_path, 'r') as f:
        html = f.read()

    # Generate blog posts HTML
    blog_html = ""
    if posts:
        blog_html = "\n        <h2>Blog</h2>\n        <ul>\n"
        for post in posts:
            blog_html += f'            <li><a href="/blog/{post["slug"]}.html">{post["title"]}</a>\n'
            blog_html += f'                <div class="project-desc">{post["date"]}</div>\n'
            blog_html += '            </li>\n'
        blog_html += "        </ul>"

    # Remove existing blog section if present
    html = re.sub(r'\s*<h2>Blog</h2>.*?</ul>', '', html, flags=re.DOTALL)

    # Insert blog section before Projects section
    html = html.replace('        <h2>Projects</h2>', blog_html + '\n        <h2>Projects</h2>')

    with open(index_path, 'w') as f:
        f.write(html)


def main():
    posts_dir = Path("posts")
    blog_dir = Path("blog")

    # Ensure directories exist
    posts_dir.mkdir(exist_ok=True)
    blog_dir.mkdir(exist_ok=True)

    # Process all markdown files
    posts = []
    md = markdown.Markdown(extensions=['fenced_code', 'codehilite'])

    for md_file in posts_dir.glob("*.md"):
        print(f"Processing {md_file.name}...")

        # Read markdown file
        with open(md_file, 'r') as f:
            content = f.read()

        # Parse frontmatter
        frontmatter, body = parse_frontmatter(content)

        title = frontmatter.get('title', md_file.stem.replace('-', ' ').title())
        date = frontmatter.get('date', datetime.now().strftime('%Y-%m-%d'))
        slug = md_file.stem

        # Convert markdown to HTML
        html_content = md.convert(body)
        md.reset()  # Reset for next file

        # Add captions to images
        html_content = add_image_captions(html_content)

        # Generate full HTML page
        full_html = generate_post_html(title, date, html_content)

        # Write to blog directory
        output_file = blog_dir / f"{slug}.html"
        with open(output_file, 'w') as f:
            f.write(full_html)

        print(f"  → Generated {output_file}")

        # Add to posts list
        posts.append({
            'title': title,
            'date': date,
            'slug': slug,
            'date_obj': datetime.strptime(date, '%Y-%m-%d')
        })

    # Sort posts by date (newest first)
    posts.sort(key=lambda x: x['date_obj'], reverse=True)

    # Update index.html
    if posts:
        print("\nUpdating index.html...")
        update_index_html(posts)
        print(f"✓ Added {len(posts)} blog post(s) to index.html")
    else:
        print("\nNo markdown files found in posts/ directory")
        print("Create a markdown file in posts/ with this format:")
        print("""
---
title: My First Post
date: 2026-01-30
---

Your content here in **markdown**!
        """)

    print("\n✓ Blog generation complete!")


if __name__ == "__main__":
    main()
