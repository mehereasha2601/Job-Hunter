import { useState } from 'react';
import { isAuthenticated } from './api';
import Login from './components/Login';
import Header from './components/Header';
import JobTable from './components/JobTable';
import Dashboard from './components/Dashboard';
import OutputsViewer from './components/OutputsViewer';
import './index.css';

function App() {
  const [authenticated, setAuthenticated] = useState(isAuthenticated());
  const [currentView, setCurrentView] = useState('jobs');

  if (!authenticated) {
    return <Login onLogin={() => setAuthenticated(true)} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header
        currentView={currentView}
        onViewChange={setCurrentView}
        onLogout={() => setAuthenticated(false)}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'jobs' && <JobTable />}
        {currentView === 'dashboard' && <Dashboard />}
        {currentView === 'outputs' && <OutputsViewer />}
      </main>
    </div>
  );
}

export default App;
