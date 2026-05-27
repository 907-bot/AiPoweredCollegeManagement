/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  images: {
    unoptimized: true,
  },
  trailingSlash: true,
  // GitHub Pages serves from /AiPoweredCollegeManagement/
  basePath: '/AiPoweredCollegeManagement',
  assetPrefix: '/AiPoweredCollegeManagement',
};

export default nextConfig;
