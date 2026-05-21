/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  images: {
    unoptimized: true,
  },
  trailingSlash: true,
  // GitHub Pages uses /subdirectory, adjust basePath if needed
  basePath: '',
  assetPrefix: '',
};

export default nextConfig;