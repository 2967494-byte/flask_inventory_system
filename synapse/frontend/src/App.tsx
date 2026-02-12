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
      const apiHost = window.location.hostname
      const res = await axios.get(`http://${apiHost}:8001/api/v1/projects`)
      setProjects(res.data)
      setLoading(false)
    } catch (err) {
      console.error("Ошибка загрузки:", err)
      setLoading(false)
    }
  }

  return (
    <div className="dashboard">
      <div className="scanline" />

      {/* Sidebar / Боковая панель */}
      <aside className="sidebar">
        <div className="logo">SYNAPSE_OS</div>

        <nav style={{ flex: 1 }}>
          <div
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <LayoutDashboard size={20} />
            <span>Панель</span>
          </div>
          <div
            className={`nav-item ${activeTab === 'projects' ? 'active' : ''}`}
            onClick={() => setActiveTab('projects')}
          >
            <FolderKanban size={20} />
            <span>Проекты</span>
          </div>
          <div
            className={`nav-item ${activeTab === 'tasks' ? 'active' : ''}`}
            onClick={() => setActiveTab('tasks')}
          >
            <CheckSquare size={20} />
            <span>Задачи</span>
          </div>
          <div
            className={`nav-item ${activeTab === 'finance' ? 'active' : ''}`}
            onClick={() => setActiveTab('finance')}
          >
            <Wallet size={20} />
            <span>Финансы</span>
          </div>
        </nav>

        <div className="nav-item">
          <Settings size={20} />
          <span>Настройки</span>
        </div>
      </aside>

      {/* Main Content / Основной контент */}
      <main className="main-view">
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }}>
          <div>
            <h1 style={{ fontSize: '24px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '1px' }}>
              Системный Терминал
            </h1>
            <p style={{ color: 'var(--text-dim)', fontSize: '14px' }}>
              Узел: <span style={{ color: 'var(--accent)' }}>asauda_production</span> | Статус: <span style={{ color: '#00ff95' }}>ИИ_АКТИВЕН</span>
            </p>
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button className="glass" style={{ padding: '10px 20px', color: 'var(--accent)', fontWeight: '600', cursor: 'pointer', border: '1px solid var(--accent-glow)' }}>
              <Plus size={18} style={{ marginBottom: '-4px', marginRight: '8px' }} />
              Быстрый ввод
            </button>
          </div>
        </header>

        {/* Stats Grid / Сетка статистики */}
        <div className="grid-stats">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass card">
            <div style={{ color: 'var(--text-dim)', fontSize: '12px', display: 'flex', justifyContent: 'space-between', textTransform: 'uppercase' }}>
              Проекты
              <FolderKanban size={14} color="var(--accent)" />
            </div>
            <div className="stat-value">{projects.length}</div>
            <div style={{ color: '#00ff95', fontSize: '11px', marginTop: '4px' }}>Активные подсистемы</div>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass card">
            <div style={{ color: 'var(--text-dim)', fontSize: '12px', display: 'flex', justifyContent: 'space-between', textTransform: 'uppercase' }}>
              Денежный поток
              <Wallet size={14} color="var(--accent)" />
            </div>
            <div className="stat-value" style={{ color: '#ff4d4d' }}>-2,450 ₽</div>
            <div style={{ color: 'var(--text-dim)', fontSize: '11px', marginTop: '4px' }}>Дневная синхронизация</div>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass card">
            <div style={{ color: 'var(--text-dim)', fontSize: '12px', display: 'flex', justifyContent: 'space-between', textTransform: 'uppercase' }}>
              Загрузка памяти
              <Activity size={14} color="var(--accent)" />
            </div>
            <div className="stat-value">14.2 ГБ</div>
            <div style={{ color: 'var(--accent)', fontSize: '11px', marginTop: '4px' }}>Контекст ИИ оптимизирован</div>
          </motion.div>
        </div>

        {/* Action Center / Центр управления */}
        <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '24px' }}>
          <div className="glass card" style={{ minHeight: '400px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
              <h3 style={{ fontSize: '14px', textTransform: 'uppercase', color: 'var(--text-dim)' }}>Нейронный Реестр</h3>
              <div style={{ color: 'var(--accent)', fontSize: '12px' }}>ПРЯМОЙ_ЭФИР</div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {loading ? (
                <p>Синхронизация...</p>
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
                  <p style={{ fontSize: '13px' }}>В базе нет проектов. Отправьте команду боту, чтобы создать первый.</p>
                </div>
              )}
            </div>
          </div>

          <div className="glass card">
            <h3 style={{ fontSize: '14px', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: '24px' }}>Аналитика Ядра ИИ</h3>
            <div style={{ padding: '20px', background: 'rgba(0, 242, 255, 0.03)', borderLeft: '2px solid var(--accent)', borderRadius: '0 8px 8px 0', marginBottom: '20px' }}>
              <p style={{ fontSize: '13px', color: 'var(--text-main)', lineHeight: '1.6', fontStyle: 'italic' }}>
                "Текущее наблюдение: Вы инициировали 12 задач на этой неделе. Рейтинг эффективности — 84%. Проект 'Synapse' является наиболее активным узлом."
              </p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ padding: '12px', border: '1px solid var(--border)', borderRadius: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '8px' }}>
                  <span>Финансовая Целостность</span>
                  <span style={{ color: '#00ff95' }}>Стабильно</span>
                </div>
                <div style={{ height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px' }}>
                  <div style={{ width: '70%', height: '100%', background: 'var(--accent)', borderRadius: '2px' }} />
                </div>
              </div>
              <div style={{ padding: '12px', border: '1px solid var(--border)', borderRadius: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '8px' }}>
                  <span>Завершение задач</span>
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
