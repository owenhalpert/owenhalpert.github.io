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
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Cache-Control', 's-maxage=30');

  const access_token = await getAccessToken();

  const response = await fetch('https://api.spotify.com/v1/me/player/currently-playing', {
    headers: { Authorization: `Bearer ${access_token}` },
  });

  if (response.status !== 204 && response.status < 400) {
    const song = await response.json();
    if (song?.item) {
      return res.status(200).json({
        isPlaying: song.is_playing,
        title: song.item.name,
        artist: song.item.artists.map(a => a.name).join(', '),
        url: song.item.external_urls.spotify,
      });
    }
  }

  // Nothing currently playing — fall back to recently played
  const recentRes = await fetch('https://api.spotify.com/v1/me/player/recently-played?limit=1', {
    headers: { Authorization: `Bearer ${access_token}` },
  });

  if (recentRes.status >= 400) {
    return res.status(200).json({ isPlaying: false });
  }

  const recent = await recentRes.json();
  const track = recent?.items?.[0]?.track;

  if (!track) {
    return res.status(200).json({ isPlaying: false });
  }

  return res.status(200).json({
    isPlaying: false,
    title: track.name,
    artist: track.artists.map(a => a.name).join(', '),
    url: track.external_urls.spotify,
  });
}
