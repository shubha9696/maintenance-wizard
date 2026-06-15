'use client';

import React, { useRef, useState } from 'react';

export default function ThreeDCard({
  children,
  className = '',
  style = {},
  onClick = undefined,
}: {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
  onClick?: () => void;
}) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [transform, setTransform] = useState('');
  const [shadow, setShadow] = useState('');

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const card = cardRef.current;
    if (!card) return;
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const xc = rect.width / 2;
    const yc = rect.height / 2;
    // Calculate tilt angles (limit to 12 degrees)
    const rx = -((y - yc) / yc) * 12;
    const ry = ((x - xc) / xc) * 12;
    
    setTransform(`perspective(1000px) rotateX(${rx}deg) rotateY(${ry}deg) scale3d(1.02, 1.02, 1.02)`);
    setShadow(`${-ry * 0.6}px ${rx * 0.6}px 20px rgba(59, 130, 246, 0.18)`);
  };

  const handleMouseLeave = () => {
    setTransform('');
    setShadow('');
  };

  return (
    <div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      className={`card-3d ${className}`}
      style={{
        transform,
        boxShadow: shadow,
        transition: 'transform 0.15s ease-out, box-shadow 0.15s ease-out',
        transformStyle: 'preserve-3d',
        cursor: onClick ? 'pointer' : 'default',
        ...style,
      }}
    >
      <div style={{ transform: 'translateZ(18px)', transformStyle: 'preserve-3d' }}>
        {children}
      </div>
    </div>
  );
}
