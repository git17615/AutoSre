import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import ServiceGrid from './components/ServiceGrid';
import IncidentTable from './components/IncidentTable';
import AlertPanel from './components/AlertPanel';
import { Toaster, toast } from 'react-hot-toast';
import './styles/App.css';

// Icons (using emoji for simplicity)
const Icons = {
  Dashboard: '📊',
  Services: '🛠️',
  Incidents: '🚨',
  AI: '🤖',
  Metrics: '📈'
};

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [services, setServices] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [aiStatus, setAiStatus] = useState({ active: false });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [servicesRes, incidentsRes, aiRes] = await Promise.all([
        fetch('http://localhost:8000/api/v1/services'),
        fetch('http://localhost:8000/api/v1/incidents?active=true'),
        fetch('http://localhost:8000/api/v1/ai/status')
      ]);

      const servicesData = await servicesRes.json();
      const incidentsData = await incidentsRes.json();
      const aiData = await aiRes.json();

      setServices(servicesData);
      setIncidents(incidentsData);
      setAiStatus(aiData);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to fetch data from backend');
    }
  };

  const restartService = async (serviceId) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/services/${serviceId}/restart`,
        { method: 'POST' }
      );
      
      if (response.ok) {
        toast.success('Service restarted successfully');
        fetchData();
      } else {
        toast.error('Failed to restart service');
      }
    } catch (error) {
      toast.error('Error restarting service');
    }
  };

  const simulateIncident = async () => {
    try {
      const response = await fetch(
        'http://localhost:8000/api/v1/simulate/incident',
        { method: 'POST' }
      );
      
      if (response.ok) {
        toast.success('Incident simulated successfully');
        fetchData();
      }
    } catch (error) {
      toast.error('Error simulating incident');
    }
  };

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: Icons.Dashboard },
    { id: 'services', label: 'Services', icon: Icons.Services },
    { id: 'incidents', label: 'Incidents', icon: Icons.Incidents }
  ];

  return (
    <div className="app">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="header">
        <div className="header-left">
          <h1>🤖 AutoSRE</h1>
          <span className="subtitle">Local AI Self-Healing Platform</span>
        </div>
        
        <div className="header-right">
          <div className={`ai-status ${aiStatus.status}`}>
            <span className="status-dot"></span>
            AI: {aiStatus.status === 'active' ? 'Active' : 'Inactive'}
          </div>
          <button className="btn simulate-btn" onClick={simulateIncident}>
            🐛 Simulate Incident
          </button>
          <button className="btn refresh-btn" onClick={fetchData}>
            🔄 Refresh
          </button>
        </div>
      </header>

      {/* Navigation */}
      <nav className="tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="tab-icon">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </nav>

      {/* Main Content */}
      <main className="main-content">
        {loading ? (
          <div className="loading">Loading...</div>
        ) : (
          <>
            <AlertPanel incidents={incidents} />
            
            {activeTab === 'dashboard' && (
              <Dashboard
                services={services}
                incidents={incidents}
                aiStatus={aiStatus}
                restartService={restartService}
              />
            )}
            
            {activeTab === 'services' && (
              <ServiceGrid
                services={services}
                restartService={restartService}
              />
            )}
            
            {activeTab === 'incidents' && (
              <IncidentTable
                incidents={incidents}
                services={services}
              />
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>AutoSRE v2.0 • Local AI Self-Healing • No external APIs required</p>
        <p>
          Monitoring {services.length} services • 
          {incidents.filter(i => i.status !== 'resolved').length} active incidents
        </p>
      </footer>
    </div>
  );
}

export default App;