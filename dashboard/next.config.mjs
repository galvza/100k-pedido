/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  transpilePackages: ["react-leaflet", "leaflet"],
};

export default nextConfig;
