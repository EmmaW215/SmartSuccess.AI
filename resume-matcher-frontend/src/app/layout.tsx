import { Inter, Roboto_Mono } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'], weight: ['400', '700'] });
const robotoMono = Roboto_Mono({ subsets: ['latin'], weight: ['400'] });

export const metadata = {
  title: 'SmartSuccess.AI - AI-Powered Career Success Platform',
  description: 'AI-powered resume optimization, job matching analysis, and mock interview preparation to accelerate your career success.',
  keywords: 'AI resume, job matching, mock interview, career success, resume optimization',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.className}>
      <body>
        <main className={robotoMono.className}>{children}</main>
      </body>
    </html>
  );
}
