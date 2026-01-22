import { Inter, Orbitron } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'], weight: ['400', '700'], variable: '--font-inter' });
const orbitron = Orbitron({ subsets: ['latin'], weight: ['400', '700'], variable: '--font-orbitron' });

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
    <html lang="en" className={`${inter.variable} ${orbitron.variable}`} suppressHydrationWarning={true}>
      <body>
        <main className={inter.className}>{children}</main>
      </body>
    </html>
  );
}
