import React from 'react';
import { Sidebar, NavTab } from './Sidebar';
import { Header } from './Header';

interface AppLayoutProps {
  activeTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  reviewCount?: number;
  pageTitle: string;
  pageSubtitle?: string;
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({
  activeTab,
  onSelectTab,
  reviewCount,
  pageTitle,
  pageSubtitle,
  children,
}) => {
  return (
    <div className="app-container">
      <Sidebar activeTab={activeTab} onSelectTab={onSelectTab} reviewCount={reviewCount} />
      <div className="main-content">
        <Header pageTitle={pageTitle} pageSubtitle={pageSubtitle} />
        <main className="page-container">
          {children}
        </main>
      </div>
    </div>
  );
};
