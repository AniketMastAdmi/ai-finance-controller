import React from 'react';
import { ShieldCheck } from 'lucide-react';

interface HeaderProps {
  pageTitle: string;
  pageSubtitle?: string;
}

export const Header: React.FC<HeaderProps> = ({ pageTitle, pageSubtitle }) => {
  return (
    <header className="top-header">
      <div>
        <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)', letterSpacing: -0.3 }}>
          {pageTitle}
        </div>
        {pageSubtitle && (
          <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 1 }}>
            {pageSubtitle}
          </div>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 6,
          backgroundColor: '#ECFDF5',
          color: '#065F46',
          border: '1px solid #A7F3D0',
          padding: '4px 10px',
          borderRadius: 'var(--radius-full)',
          fontSize: 11,
          fontWeight: 600,
        }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: '#10B981' }} />
          Operational • Tools Synced
        </div>

        <div style={{ fontSize: 12, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
          <ShieldCheck size={14} style={{ color: '#059669' }} />
          Immutable Audit Mode
        </div>
      </div>
    </header>
  );
};
