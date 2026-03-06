import type { NextConfig } from "next";

const apiUrl = process.env.NEXT_PUBLIC_API_URL;

const nextConfig: NextConfig = {
  async rewrites() {
    if (apiUrl) {
      return [{ source: "/api/:path*", destination: `${apiUrl}/api/:path*` }];
    }
    return [];
  },
};

export default nextConfig;
