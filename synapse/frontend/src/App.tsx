import { useState, useEffect } from 'react'
import {
  LayoutDashboard,
  FolderKanban,
  CheckSquare,
  Wallet,
  Settings,
  Activity,
  Plus
} from 'lucide-react'
import { motion } from 'framer-motion'
import axios from 'axios'
import './index.css'



function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [projects, setProjects] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      // Use the same domain but port 8001 for API
      const apiHost = window.location.hostname
      const res = await axios.get(`http://${apiHost}:8001/api/v1/projects`)
      setProjects(res.data)
      setLoading(false)
    } catch (err) {
      console.error("Fetch error:", err)
      setLoading(false)
    }
  }

  return (
    <div className="dashboard">
      <div className="scanline" />

      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo">SYNAPSE_OS</div>

        <nav style={{ flex: 1 }}>
          <div
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <LayoutDashboard size={20} />
            <span>Dashboard</span>
          </div>
          <div
            className={`nav-item ${activeTab === 'projects' ? 'active' : ''}`}
            onClick={() => setActiveTab('projects')}
          >
            <FolderKanban size={20} />
            <span>Projects</span>
          </div>
          <div
            className={`nav-item ${activeTab === 'tasks' ? 'active' : ''}`}
            onClick={() => setActiveTab('tasks')}
          >
            <CheckSquare size={20} />
            <span>Tasks</span>
          </div>
          <div
            className={`nav-item ${activeTab === 'finance' ? 'active' : ''}`}
            onClick={() => setActiveTab('finance')}
          >
            <Wallet size={20} />
            <span>Finance</span>
          </div>
        </nav>

        <div className="nav-item">
          <Settings size={20} />
          <span>Settings</span>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-view">
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }}>
          <div>
            <h1 style={{ fontSize: '24px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '1px' }}>
              System Terminal
            </h1>
            <p style={{ color: 'var(--text-dim)', fontSize: '14px' }}>
              Node: <span style={{ color: 'var(--accent)' }}>asauda_production</span> | Status: <span style={{ color: '#00ff95' }}>AI_ACTIVE</span>
            </p>
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button className="glass" style={{ padding: '10px 20px', color: 'var(--accent)', fontWeight: '600', cursor: 'pointer', border: '1px solid var(--accent-glow)' }}>
              <Plus size={18} style={{ marginBottom: '-4px', marginRight: '8px' }} />
              Quick Ingest
            </button>
          </div>
        </header>

        {/* Stats Grid */}
        <div className="grid-stats">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass card">
            <div style={{ color: 'var(--text-dim)', fontSize: '12px', display: 'flex', justifyContent: 'space-between', textTransform: 'uppercase' }}>
              Projects
              <FolderKanban size={14} color="var(--accent)" />
            </div>
            <div className="stat-value">{projects.length}</div>
            <div style={{ color: '#00ff95', fontSize: '11px', marginTop: '4px' }}>Active Subsystems</div>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass card">
            <div style={{ color: 'var(--text-dim)', fontSize: '12px', display: 'flex', justifyContent: 'space-between', textTransform: 'uppercase' }}>
              Cash Flow
              <Wallet size={14} color="var(--accent)" />
            </div>
            <div className="stat-value" style={{ color: '#ff4d4d' }}>-2,450 ₽</div>
            <div style={{ color: 'var(--text-dim)', fontSize: '11px', marginTop: '4px' }}>Daily synchronization</div>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass card">
            <div style={{ color: 'var(--text-dim)', fontSize: '12px', display: 'flex', justifyContent: 'space-between', textTransform: 'uppercase' }}>
              Memory Load
              <Activity size={14} color="var(--accent)" />
            </div>
            <div className="stat-value">14.2 GB</div>
            <div style={{ color: 'var(--accent)', fontSize: '11px', marginTop: '4px' }}>AI Context Optimized</div>
          </motion.div>
        </div>

        {/* Action Center */}
        <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '24px' }}>
          <div className="glass card" style={{ minHeight: '400px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
              <h3 style={{ fontSize: '14px', textTransform: 'uppercase', color: 'var(--text-dim)' }}>Neural Registry</h3>
              <div style={{ color: 'var(--accent)', fontSize: '12px' }}>LIVE_FEED</div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {loading ? (
                <p>Synchronizing...</p>
              ) : projects.length > 0 ? (
                projects.map((p, i) => (
                  <div key={i} className="nav-item" style={{ background: 'rgba(255,255,255,0.02)', padding: '16px' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '14px', fontWeight: '600' }}>{p.name}</div>
                      <div style={{ fontSize: '11px', color: 'var(--text-dim)' }}>ID: {p.id.slice(0, 8)}...</div>
                    </div>
                    <span className="status-badge status-active">{p.type}</span>
                  </div>
                ))
              ) : (
                <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-dim)' }}>
                  <Activity size={32} style={{ opacity: 0.2, marginBottom: '12px' }} />
                  <p style={{ fontSize: '13px' }}>No projects in database. Send a command to the bot to create one.</p>
                </div>
              )}
            </div>
          </div>

          <div className="glass card">
            <h3 style={{ fontSize: '14px', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: '24px' }}>AI Core Insights</h3>
            <div style={{ padding: '20px', background: 'rgba(0, 242, 255, 0.03)', borderLeft: '2px solid var(--accent)', borderRadius: '0 8px 8px 0', marginBottom: '20px' }}>
              <p style={{ fontSize: '13px', color: 'var(--text-main)', lineHeight: '1.6', fontStyle: 'italic' }}>
                "Current observation: You have initiated 12 tasks this week. Efficiency rating is 84%. Project 'Synapse' is the most active node."
              </p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ padding: '12px', border: '1px solid var(--border)', borderRadius: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '8px' }}>
                  <span>Finance Integrity</span>
                  <span style={{ color: '#00ff95' }}>Stable</span>
                </div>
                <div style={{ height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px' }}>
                  <div style={{ width: '70%', height: '100%', background: 'var(--accent)', borderRadius: '2px' }} />
                </div>
              </div>
              <div style={{ padding: '12px', border: '1px solid var(--border)', borderRadius: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '8px' }}>
                  <span>Task Completion</span>
                  <span style={{ color: 'var(--accent)' }}>84%</span>
                </div>
                <div style={{ height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px' }}>
                  <div style={{ width: '84%', height: '100%', background: 'var(--accent)', borderRadius: '2px' }} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
