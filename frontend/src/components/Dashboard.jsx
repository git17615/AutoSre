import React from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

const Dashboard = ({ services, incidents, aiStatus, restartService }) => {
  const healthyCount = services.filter(s => s.status === 'healthy').length;
  const unhealthyCount = services.length - healthyCount;
  const activeIncidents = incidents.filter(i => i.status !== 'resolved').length;

  // Chart data
  const serviceHealthData = [
    { name: 'Healthy', value: healthyCount, color: '#10b981' },
    { name: 'Unhealthy', value: unhealthyCount, color: '#ef4444' }
  ];

  const incidentSeverityData = incidents
    .filter(i => i.status !== 'resolved')
    .map(inc => ({
      name: inc.service_name,
      severity: inc.severity * 100
    }));

  return (
    <div className="dashboard">
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Services</h3>
          <p className="stat-value">{services.length}</p>
        </div>
        <div className="stat-card">
          <h3>Healthy Services</h3>
          <p className="stat-value healthy">{healthyCount}</p>
        </div>
        <div className="stat-card">
          <h3>Active Incidents</h3>
          <p className="stat-value warning">{activeIncidents}</p>
        </div>
        <div className="stat-card">
          <h3>AI Confidence</h3>
          <p className="stat-value info">
            {aiStatus.patterns_loaded ? `${aiStatus.patterns_loaded} patterns` : 'Loading...'}
          </p>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h4>Service Health Distribution</h4>
          <PieChart width={300} height={200}>
            <Pie
              data={serviceHealthData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {serviceHealthData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
          </PieChart>
        </div>

        <div className="chart-card">
          <h4>Incident Severity</h4>
          <BarChart width={400} height={200} data={incidentSeverityData}>
            <Bar dataKey="severity" fill="#f59e0b" />
          </BarChart>
        </div>
      </div>

      <div className="services-overview">
        <h3>Services Overview</h3>
        <div className="services-list">
          {services.map(service => (
            <div key={service.id} className="service-item">
              <div className="service-info">
                <span className={`status-dot ${service.status}`}></span>
                <div>
                  <h4>{service.name}</h4>
                  <p className="service-meta">
                    {service.type} • Port {service.port} • {service.status}
                  </p>
                </div>
              </div>
              <button
                className="btn-sm"
                onClick={() => restartService(service.id)}
                disabled={service.status === 'healthy'}
              >
                Restart
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;