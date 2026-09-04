import React from 'react';

interface ConfidenceBadgeProps {
  confidence?: 'HIGH_CONFIDENCE' | 'LOW_CONFIDENCE' | 'UNRESOLVED' | string;
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({ confidence }) => {
  if (!confidence) return null;

  let badgeClass = 'badge-matched';
  let label = 'HIGH CONFIDENCE';

  if (confidence === 'LOW_CONFIDENCE' || confidence.includes('LOW')) {
    badgeClass = 'badge-review';
    label = 'LOW CONFIDENCE • REVIEW';
  } else if (confidence === 'UNRESOLVED' || confidence.includes('UNRESOLVED')) {
    badgeClass = 'badge-exception';
    label = 'UNRESOLVED';
  }

  return (
    <span className={`badge ${badgeClass}`}>
      {label}
    </span>
  );
};
