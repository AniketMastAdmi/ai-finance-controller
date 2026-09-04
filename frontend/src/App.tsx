import React, { useState, useEffect } from 'react';
import { AppLayout } from './components/Layout/AppLayout';
import { NavTab } from './components/Layout/Sidebar';
import { OverviewPage } from './pages/OverviewPage';
import { ReconciliationPage } from './pages/ReconciliationPage';
import { ReviewQueuePage } from './pages/ReviewQueuePage';
import { AskAiPage } from './pages/AskAiPage';
import { AuditPage } from './pages/AuditPage';
import { UsagePage } from './pages/UsagePage';
import { getLowConfidenceMatches } from './api/reconciliation';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<NavTab>('overview');
  const [prefilledQuestion, setPrefilledQuestion] = useState<string>('');
  const [reviewCount, setReviewCount] = useState<number>(0);

  useEffect(() => {
    // Pre-fetch count of low-confidence items for sidebar badge
    getLowConfidenceMatches()
      .then((res) => setReviewCount(res.total_low_confidence_matches))
      .catch(() => setReviewCount(0));
  }, []);

  const handleAskAi = (question: string) => {
    setPrefilledQuestion(question);
    setActiveTab('ask-ai');
  };

  const pageDetails: Record<NavTab, { title: string; subtitle: string }> = {
    overview: {
      title: 'Finance Control Center',
      subtitle: 'Batch reconciliation health & key operations telemetry',
    },
    reconciliation: {
      title: 'Reconciliation Ledger',
      subtitle: 'Complete invoice-to-settlement matching records and audit status',
    },
    'review-queue': {
      title: 'Review Queue: Borderline Matches',
      subtitle: 'Transactions classified as matched that sit near the fee tolerance boundary',
    },
    'ask-ai': {
      title: 'AI-CFO Reasoning Layer',
      subtitle: 'Natural language investigation grounded in deterministic financial tools',
    },
    audit: {
      title: 'Governance & Audit Trail',
      subtitle: 'Immutable chronological trace of all decisions and tool executions',
    },
    usage: {
      title: 'Operations & API Metering',
      subtitle: 'Proof-of-concept telemetry and compute unit tracking',
    },
  };

  return (
    <AppLayout
      activeTab={activeTab}
      onSelectTab={setActiveTab}
      reviewCount={reviewCount}
      pageTitle={pageDetails[activeTab].title}
      pageSubtitle={pageDetails[activeTab].subtitle}
    >
      {activeTab === 'overview' && (
        <OverviewPage onNavigate={setActiveTab} onAskAi={handleAskAi} />
      )}
      {activeTab === 'reconciliation' && (
        <ReconciliationPage onAskAi={handleAskAi} />
      )}
      {activeTab === 'review-queue' && (
        <ReviewQueuePage onAskAi={handleAskAi} />
      )}
      {activeTab === 'ask-ai' && (
        <AskAiPage
          initialQuestion={prefilledQuestion}
          onClearInitialQuestion={() => setPrefilledQuestion('')}
        />
      )}
      {activeTab === 'audit' && <AuditPage />}
      {activeTab === 'usage' && <UsagePage />}
    </AppLayout>
  );
};

export default App;
