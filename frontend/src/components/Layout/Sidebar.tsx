import React from 'react';
import { 
  LayoutDashboard, 
  TableProperties, 
  AlertCircle, 
  Sparkles, 
  FileText, 
  Gauge, 
  Scale
} from 'lucide-react';

export type NavTab = 'overview' | 'reconciliation' | 'review-queue' | 'ask-ai' | 'audit' | 'usage';

interface SidebarProps {
  activeTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  reviewCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onSelectTab, reviewCount = 0 }) => {
  const navItems = [
    { id: 'overview' as NavTab, label: 'Overview', icon: LayoutDashboard },
    { id: 'reconciliation' as NavTab, label: 'Reconciliation', icon: TableProperties },
    { id: 'review-queue' as NavTab, label: 'Review Queue', icon: AlertCircle, badge: reviewCount > 0 ? reviewCount : undefined },
    { id: 'ask-ai' as NavTab, label: 'Ask AI-CFO', icon: Sparkles },
    { id: 'audit' as NavTab, label: 'Audit Trail', icon: FileText },
    { id: 'usage' as NavTab, label: 'API Metering', icon: Gauge },
  ];

  return (
    <aside className="sidebar">
      {/* Brand */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '0 8px 24px 8px', borderBottom: '1px solid var(--border-subtle)', marginBottom: 20 }}>
        <div style={{
          width: 32,
          height: 32,
          borderRadius: 'var(--radius-md)',
          backgroundColor: 'var(--accent-primary)',
          color: '#FFFFFF',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          <Scale size={18} />
        </div>
        <div>
          <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)', letterSpacing: -0.2 }}>
            AI-CFO
          </div>
          <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
            Finance Control Layer
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ display: 'flex', flexDirection: 'column', gap: 4, flex: 1 }}>
        <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5, padding: '4px 8px 8px 8px' }}>
          Operations
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '9px 12px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: isActive ? 'var(--bg-card)' : 'transparent',
                color: isActive ? 'var(--accent-primary)' : 'var(--text-secondary)',
                fontWeight: isActive ? 600 : 500,
                fontSize: 13,
                border: isActive ? '1px solid var(--border-subtle)' : '1px solid transparent',
                boxShadow: isActive ? 'var(--shadow-subtle)' : 'none',
                transition: 'all 0.15s ease',
              }}
              onMouseOver={(e) => {
                if (!isActive) e.currentTarget.style.backgroundColor = 'var(--bg-card-subtle)';
              }}
              onMouseOut={(e) => {
                if (!isActive) e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <Icon size={16} style={{ color: isActive ? 'var(--accent-primary)' : 'var(--text-muted)' }} />
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && (
                <span style={{
                  backgroundColor: 'var(--status-review-bg)',
                  color: 'var(--status-review-text)',
                  border: '1px solid var(--status-review-border)',
                  borderRadius: 'var(--radius-full)',
                  padding: '1px 6px',
                  fontSize: 10,
                  fontWeight: 700,
                }}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* System info footer */}
      <div style={{
        marginTop: 'auto',
        padding: '14px 12px',
        backgroundColor: 'var(--bg-card-subtle)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-md)',
        fontSize: 11,
      }}>
        <div style={{ color: 'var(--text-secondary)', fontWeight: 600, marginBottom: 4 }}>
          Engine Parameters
        </div>
        <div style={{ color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
          <span>Fee Tolerance:</span>
          <span className="font-mono">1.0% – 3.5%</span>
        </div>
        <div style={{ color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between' }}>
          <span>Review Band:</span>
          <span className="font-mono">3.0% – 4.0%</span>
        </div>
      </div>
    </aside>
  );
};
