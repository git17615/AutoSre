const Dashboard = ({ services, incidents, aiStatus }) => (
  <div>
    <h2>Services</h2>
    {services.map(s => (
      <div key={s.id}>
        {s.name} — {s.status}
      </div>
    ))}

    <h2>AI Status</h2>
    <pre>{JSON.stringify(aiStatus, null, 2)}</pre>

    <h2>Incidents</h2>
    <pre>{JSON.stringify(incidents, null, 2)}</pre>
  </div>
)

export default Dashboard
