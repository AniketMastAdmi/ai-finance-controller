import React from 'react';

interface StatusBadgeProps {
  status: 'MATCHED' | 'EXCEPTION' | string;
  reason?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, reason }) => {
  const isMatched = status === 'MATCHED';
  const badgeClass = isMatched ? 'badge-matched' : 'badge-exception';

  const formatReason = (r?: string) => {
    if (!r) return '';
    return r.replace(/_/g, ' ');
  };

  return (
    <span className={`badge ${badgeClass}`}>
      <span style={{ 
        width: 5, 
        height: 5, 
        borderRadius: '50%', 
        backgroundColor: isMatched ? '#10B981' : '#EF4444',
        marginRight: 2 
      }} />
      {status}
      {reason && reason !== 'clean_match' && (
        <span style={{ opacity: 0.85, fontWeight: 400, marginLeft: 3 }}>
          • {formatReason(reason)}
        </span>
      )}
    </span>
  );
};
