const LETTERBOXD_RSS_URL = 'https://letterboxd.com/owenology/rss/';

function decodeXml(text) {
  return text
    .replace(/<!\[CDATA\[(.*?)\]\]>/gs, '$1')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
}

function extractTag(xml, tag) {
  const match = xml.match(new RegExp(`<${tag}>([\\s\\S]*?)</${tag}>`, 'i'));
  return match ? decodeXml(match[1].trim()) : null;
}

function extractFirstItem(xml) {
  const match = xml.match(/<item>([\s\S]*?)<\/item>/i);
  return match ? match[1] : null;
}

function parseTitle(rawTitle) {
  if (!rawTitle) return null;
  const [titlePart, ratingPart] = rawTitle.split(' - ');
  const match = titlePart.match(/^(.*?),\s*(\d{4})$/);

  return {
    title: match ? match[1] : titlePart,
    year: match ? match[2] : null,
    rating: ratingPart ?? null,
  };
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Cache-Control', 's-maxage=1800');

  try {
    const response = await fetch(LETTERBOXD_RSS_URL, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; owenhalpert.com latest movie widget)',
        Accept: 'application/rss+xml, application/xml, text/xml;q=0.9, */*;q=0.8',
      },
    });

    if (!response.ok) {
      return res.status(200).json({ found: false });
    }

    const xml = await response.text();
    const item = extractFirstItem(xml);

    if (!item) {
      return res.status(200).json({ found: false });
    }

    const titleData = parseTitle(extractTag(item, 'title'));
    const watchedAt = extractTag(item, 'pubDate');
    const rawLink = extractTag(item, 'link') ?? '';
    const url = rawLink.replace(/letterboxd\.com\/[^/]+\/film\//, 'letterboxd.com/film/');
    const description = extractTag(item, 'description') ?? '';
    const posterMatch = description.match(/<img[^>]+src="([^"]+)"/i);
    const posterUrl = posterMatch ? posterMatch[1] : null;

    return res.status(200).json({
      found: true,
      title: titleData?.title ?? null,
      year: titleData?.year ?? null,
      rating: titleData?.rating ?? null,
      url,
      watchedAt,
      posterUrl,
    });
  } catch {
    return res.status(200).json({ found: false });
  }
}
