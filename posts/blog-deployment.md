---
title: How I publish my blog
date: 2026-01-30
---
High on the list of my 2026 New Year's Resolutions was to write (and publish) more. To do this, I knew I needed to provide myself with an *extremely low friction* system of publishing blog posts. Here is the system I came up with:

Everything lives within [Obsidian](https://obsidian.md/), a beautifully lightweight Markdown file editor. I know how to write in Markdown, it's familiar and comfortable. 

My main Obsidian "vault" (file store) is a folder in my local Git repository for my website. This means once I'm done writing, I don't have to move any files around. I can keep drafts in a different vault, if needed.

In Obsidian, I have a blog post [template.](https://help.obsidian.md/plugins/templates) This allows me to open a new note and quickly apply the template, which looks like this:
```
---
title: How I publish my blog
date: 2026-01-30
---
```
Quite simple — the title becomes the Heading 1 text at the top of the page. 

Once I am done writing, I run a [shell command](https://github.com/Taitava/obsidian-shellcommands) from within Obsidian(!), which adds the new blog post to my Git staging, adds a commit message with the date, and pushes to Github.

In my GitHub Actions, I have a lightweight Python script run as part of deployment that converts the Markdown into HTML. I don't even have to look at any HTML throughout this entire process.

![It can even do images!](/static/images/cute-dog.png)