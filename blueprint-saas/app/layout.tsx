import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Blueprint GTM - Intelligence-Driven Outreach",
  description: "Get a custom GTM playbook with data-backed messaging for your target accounts. Only pay when your playbook is ready.",
  icons: {
    icon: '/favicon.png',
    apple: '/apple-touch-icon.png',
  },
  openGraph: {
    title: "Blueprint GTM - Intelligence-Driven Outreach",
    description: "Get a custom GTM playbook with data-backed messaging for your target accounts.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
