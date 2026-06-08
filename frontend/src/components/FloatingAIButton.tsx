'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Bot } from 'lucide-react';

export default function FloatingAIButton() {
  const pathname = usePathname();

  // Don't show on the chat page itself
  if (pathname === '/chat') return null;

  return (
    <Link href="/chat" className="floating-ai-btn" title="Ask AI Maintenance Wizard">
      <Bot size={24} />
    </Link>
  );
}
