import { useEffect, useState } from 'react'
import Dashboard from './components/Dashboard'
import AlertPanel from './components/AlertPanel'

function App() {
  const [services, setServices] = useState([])
  const [incidents, setIncidents] = useState([])
  const [aiStatus, setAiStatus] = useState({})

  const fetchData = async () => {
    const s = await fetch('http://localhost:8000/api/v1/services').then(r => r.json())
    const i = await fetch('http://localhost:8000/api/v1/incidents').then(r => r.json())
    const a = await fetch('http://localhost:8000/api/v1/ai/status').then(r => r.json())

    setServices(s)
    setIncidents(i)
    setAiStatus(a)
  }

  useEffect(() => {
    fetchData()
    const t = setInterval(fetchData, 5000)
    return () => clearInterval(t)
  }, [])

  return (
    <div className="app">
      <h1>🤖 AutoSRE Dashboard</h1>
      <AlertPanel incidents={incidents} />
      <Dashboard
        services={services}
        incidents={incidents}
        aiStatus={aiStatus}
      />
    </div>
  )
}

export default App
