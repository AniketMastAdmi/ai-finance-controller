import React from 'react';

interface SkeletonProps {
  lines?: number;
  height?: number | string;
  width?: number | string;
  className?: string;
}

export const SkeletonLoader: React.FC<SkeletonProps> = ({ 
  lines = 3, 
  height = 16, 
  width = '100%',
  className = '' 
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }} className={className}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="skeleton"
          style={{
            height,
            width: i === lines - 1 && lines > 1 ? '70%' : width,
          }}
        />
      ))}
    </div>
  );
};
