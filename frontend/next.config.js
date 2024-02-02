/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'i.discogs.com',
      },
      {
        protocol: 'https',
        hostname: 'www.deejay.de',
      },
      {
        protocol: 'https',
        hostname: 'deejay.de',
      },
    ],
  },
}

module.exports = nextConfig
