'use client';

import React from 'react';
import katex from 'katex';

interface MathRendererProps {
  formula: string;
  block?: boolean;
  className?: string;
}

export const MathRenderer: React.FC<MathRendererProps> = ({ formula, block = false, className = '' }) => {
  const containerRef = React.useRef<HTMLSpanElement>(null);

  React.useEffect(() => {
    if (containerRef.current) {
      try {
        katex.render(formula, containerRef.current, {
          displayMode: block,
          throwOnError: false
        });
      } catch (e) {
        console.error('KaTeX rendering error:', e);
        if (containerRef.current) {
          containerRef.current.innerText = formula;
        }
      }
    }
  }, [formula, block]);

  return <span ref={containerRef} className={`math-formula ${block ? 'block my-2 text-center' : 'inline-block px-1'} ${className}`} />;
};
