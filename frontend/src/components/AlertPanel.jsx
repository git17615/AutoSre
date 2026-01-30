const AlertPanel = ({ incidents }) => {
  if (!incidents || incidents.length === 0) return null
  return <div className="alert">🚨 Active Incidents Detected</div>
}

export default AlertPanel
