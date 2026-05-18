/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['images-na.ssl-images-amazon.com', 'http2.mlstatic.com', 'cf.shopee.com.br', 'm.media-amazon.com'],
    unoptimized: true,
  },
}

module.exports = nextConfig
