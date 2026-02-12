import { useState } from 'react'
import {
  LayoutDashboard,
  FolderKanban,
  CheckSquare,
  Wallet,
  StickyNote,
  Settings,
  Activity,
  Plus,
  Mic
} from 'lucide-react'
import { motion } from 'framer-motion'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')

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
          <div
            className={`nav-item ${activeTab === 'notes' ? 'active' : ''}`}
            onClick={() => setActiveTab('notes')}
          >
            <StickyNote size={20} />
            <span>Notes</span>
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
            <h1 style={{ fontSize: '24px', fontWeight: '700' }}>System Overview</h1>
            <p style={{ color: 'var(--text-dim)', fontSize: '14px' }}>Welcome back, Operator. AI Subsystems optimal.</p>
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button className="glass" style={{ padding: '10px 20px', color: 'var(--accent)', fontWeight: '600', cursor: 'pointer' }}>
              <Plus size={18} style={{ marginBottom: '-4px', marginRight: '8px' }} />
              New Project
            </button>
            <div className="glass" style={{ width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent)' }}>
              <Activity size={20} />
            </div>
          </div>
        </header>

        {/* Stats Grid */}
        <div className="grid-stats">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass card">
            <div style={{ color: 'var(--text-dim)', fontSize: '13px', display: 'flex', justifyContent: 'space-between' }}>
              Projects
              <FolderKanban size={16} color="var(--accent)" />
            </div>
            <div className="stat-value">12</div>
            <div style={{ color: '#00ff95', fontSize: '12px', marginTop: '4px' }}>+2 this week</div>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass card">
            <div style={{ color: 'var(--text-dim)', fontSize: '13px', display: 'flex', justifyContent: 'space-between' }}>
              Active Tasks
              <CheckSquare size={16} color="var(--accent)" />
            </div>
            <div className="stat-value">48</div>
            <div style={{ color: 'var(--text-dim)', fontSize: '12px', marginTop: '4px' }}>8 high priority</div>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass card">
            <div style={{ color: 'var(--text-dim)', fontSize: '13px', display: 'flex', justifyContent: 'space-between' }}>
              Monthly Flow
              <Wallet size={16} color="var(--accent)" />
            </div>
            <div className="stat-value">-42.5k</div>
            <div style={{ color: '#ff4d4d', fontSize: '12px', marginTop: '4px' }}>Expense threshold reached</div>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="glass card">
            <div style={{ color: 'var(--text-dim)', fontSize: '13px', display: 'flex', justifyContent: 'space-between' }}>
              Memories
              <StickyNote size={16} color="var(--accent)" />
            </div>
            <div className="stat-value">156</div>
            <div style={{ color: 'var(--text-dim)', fontSize: '12px', marginTop: '4px' }}>32 AI-tagged ideas</div>
          </motion.div>
        </div>

        {/* Recent Events / Activity */}
        <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '24px' }}>
          <div className="glass card">
            <h3 style={{ marginBottom: '20px', fontSize: '16px' }}>Neural Ingestion Log</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {[
                { time: '14:20', text: 'Заправил машину на 3000 рублей, пробег 150к', type: 'Transaction', status: '✅' },
                { time: '11:05', text: 'Купить SSL сертификат для сайта-визитки', type: 'Task', status: '✅' },
                { time: 'Yesterday', text: 'Идея: сделать сайт для продажи кирпича', type: 'Idea', status: '✅' },
              ].map((item, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '16px', padding: '12px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
                  <div style={{ color: 'var(--accent)', fontSize: '12px', fontWeight: 'bold', width: '60px' }}>{item.time}</div>
                  <div style={{ flex: 1, fontSize: '14px' }}>{item.text}</div>
                  <span className="status-badge status-active">{item.type}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="glass card">
            <h3 style={{ marginBottom: '20px', fontSize: '16px' }}>AI Insights</h3>
            <div style={{ padding: '20px', background: 'rgba(0, 242, 255, 0.05)', borderLeft: '2px solid var(--accent)', borderRadius: '0 8px 8px 0' }}>
              <p style={{ fontSize: '14px', color: 'var(--accent)', lineHeight: '1.5' }}>
                "На основе ваших последних записей, проект 'Машина' требует внимания. Стоимость владения выросла на 15% в этом месяце."
              </p>
            </div>
            <div style={{ marginTop: '20px', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-dim)', fontSize: '13px' }}>
              <Mic size={14} />
              <span>Voice intake active via Telegram</span>
            </div>
          </div>
        </div>
      </main>
    </div >
  )
}

export default App
