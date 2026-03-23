const BASE64_CREDENTIALS = Buffer.from(
  `${process.env.SPOTIFY_CLIENT_ID}:${process.env.SPOTIFY_CLIENT_SECRET}`
).toString('base64');

async function getAccessToken() {
  const res = await fetch('https://accounts.spotify.com/api/token', {
    method: 'POST',
    headers: {
      Authorization: `Basic ${BASE64_CREDENTIALS}`,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token: process.env.SPOTIFY_REFRESH_TOKEN,
    }),
  });
  const data = await res.json();
  return data.access_token;
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', 'https://owenhalpert.com');
  res.setHeader('Cache-Control', 's-maxage=30');

  const access_token = await getAccessToken();

  const response = await fetch('https://api.spotify.com/v1/me/player/currently-playing', {
    headers: { Authorization: `Bearer ${access_token}` },
  });

  if (response.status === 204 || response.status >= 400) {
    return res.status(200).json({ isPlaying: false });
  }

  const song = await response.json();

  if (!song?.item) {
    return res.status(200).json({ isPlaying: false });
  }

  return res.status(200).json({
    isPlaying: song.is_playing,
    title: song.item.name,
    artist: song.item.artists.map(a => a.name).join(', '),
    url: song.item.external_urls.spotify,
  });
}
