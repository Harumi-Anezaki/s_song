import React from 'react';
import type { AppRoute } from './store/appStore';
import { Video, Database, HardDrive, Settings } from 'lucide-react';
import { useAppStore } from './store/appStore';
import './App.css';

// Placeholder components for routing
import YouTubeSearch from './components/YouTubeSearch';
import LinkedDB from './components/LinkedDB';
import MainDB from './components/MainDB';
import AppSettings from './components/Settings';

const App: React.FC = () => {
  const { currentRoute, setCurrentRoute } = useAppStore();

  const renderContent = () => {
    switch (currentRoute) {
      case 'search':
        return <YouTubeSearch />;
      case 'linked-db':
        return <LinkedDB />;
      case 'main-db':
        return <MainDB />;
      case 'settings':
        return <AppSettings />;
      default:
        return <YouTubeSearch />;
    }
  };

  const navItems = [
    { id: 'search', label: 'YouTube検索', icon: Video },
    { id: 'linked-db', label: 'リンクドDB', icon: Database },
    { id: 'main-db', label: 'DB原本', icon: HardDrive },
    { id: 'settings', label: '設定', icon: Settings },
  ] as const;

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1 className="sidebar-title">Song Manager</h1>
        </div>
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <div
              key={item.id}
              className={`nav-item ${currentRoute === item.id ? 'active' : ''}`}
              onClick={() => setCurrentRoute(item.id as AppRoute)}
            >
              <item.icon className="nav-icon" />
              <span>{item.label}</span>
            </div>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {renderContent()}
      </main>
    </div>
  );
};

export default App;
