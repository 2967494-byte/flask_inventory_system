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
      console.error("Ошибка синхронизации:", err)
      setLoading(false)
    }
  }

  return (
    <div className="dashboard">
      <div className="scanline" />

      {/* Боковая панель */}
      <aside className="sidebar">
        <div className="logo" style={{ letterSpacing: '4px' }}>SYNAPSE_OS</div>

        <nav style={{ flex: 1 }}>
          <div
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <LayoutDashboard size={20} />
            <span>Панель управления</span>
          </div>
          <div
            className={`nav-item ${activeTab === 'projects' ? 'active' : ''}`}
            onClick={() => setActiveTab('projects')}
          >
            <FolderKanban size={20} />
            <span>Управление проектами</span>
          </div>
          <div
            className={`nav-item ${activeTab === 'tasks' ? 'active' : ''}`}
            onClick={() => setActiveTab('tasks')}
          >
            <CheckSquare size={20} />
            <span>Задачи и цели</span>
          </div>
          <div
            className={`nav-item ${activeTab === 'finance' ? 'active' : ''}`}
            onClick={() => setActiveTab('finance')}
          >
            <Wallet size={20} />
            <span>Финансовый учет</span>
          </div>
        </nav>

        <div className="nav-item">
          <Settings size={20} />
          <span>Системные настройки</span>
        </div>
      </aside>

      {/* Основная рабочая область */}
      <main className="main-view">
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }}>
          <div>
            <h1 style={{ fontSize: '26px', fontWeight: '800', textTransform: 'uppercase', letterSpacing: '2px', color: 'var(--accent)' }}>
              Информационный Терминал
            </h1>
            <p style={{ color: 'var(--text-dim)', fontSize: '14px', marginTop: '4px' }}>
              Узел: <span style={{ color: 'var(--text-main)', fontWeight: '600' }}>asauda_server</span> | Состояние: <span style={{ color: '#00ff95', fontWeight: '600' }}>СИСТЕМА_АКТИВНА</span>
            </p>
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button className="glass" style={{ padding: '12px 24px', color: 'var(--accent)', fontWeight: '700', cursor: 'pointer', border: '1px solid var(--accent-glow)', borderRadius: '8px' }}>
              <Plus size={18} style={{ marginBottom: '-3px', marginRight: '8px' }} />
              БЫСТРЫЙ ВВОД
            </button>
          </div>
        </header>

        {/* Сводка показателей */}
        <div className="grid-stats">
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="glass card">
            <div style={{ color: 'var(--text-dim)', fontSize: '12px', display: 'flex', justifyContent: 'space-between', textTransform: 'uppercase', fontWeight: '600' }}>
              Активные Проекты
              <FolderKanban size={14} color="var(--accent)" />
            </div>
            <div className="stat-value">{projects.length}</div>
            <div style={{ color: '#00ff95', fontSize: '11px', marginTop: '6px', fontWeight: '500' }}>Стабильная работа подсистем</div>
          </motion.div>

          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.1 }} className="glass card">
            <div style={{ color: 'var(--text-dim)', fontSize: '12px', display: 'flex', justifyContent: 'space-between', textTransform: 'uppercase', fontWeight: '600' }}>
              Баланс Потоков
              <Wallet size={14} color="var(--accent)" />
            </div>
            <div className="stat-value" style={{ color: '#ff4d4d' }}>-2,450 ₽</div>
            <div style={{ color: 'var(--text-dim)', fontSize: '11px', marginTop: '6px', fontWeight: '500' }}>Синхронизация за сегодня</div>
          </motion.div>

          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2 }} className="glass card">
            <div style={{ color: 'var(--text-dim)', fontSize: '12px', display: 'flex', justifyContent: 'space-between', textTransform: 'uppercase', fontWeight: '600' }}>
              Память Ядра
              <Activity size={14} color="var(--accent)" />
            </div>
            <div className="stat-value">14.2 ГБ</div>
            <div style={{ color: 'var(--accent)', fontSize: '11px', marginTop: '6px', fontWeight: '500' }}>ИИ-контекст оптимизирован</div>
          </motion.div>
        </div>

        {/* Центр обработки данных */}
        <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: '30px' }}>
          <div className="glass card" style={{ minHeight: '450px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '30px', borderBottom: '1px solid var(--border)', paddingBottom: '15px' }}>
              <h3 style={{ fontSize: '15px', textTransform: 'uppercase', color: 'var(--text-main)', letterSpacing: '1px' }}>Нейронный Реестр Событий</h3>
              <div style={{ color: 'var(--accent)', fontSize: '12px', fontWeight: '700' }}>АКТУАЛЬНЫЕ ДАННЫЕ</div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              {loading ? (
                <div style={{ textAlign: 'center', padding: '50px' }}>
                  <p style={{ color: 'var(--accent)' }}>Установка соединения...</p>
                </div>
              ) : projects.length > 0 ? (
                projects.map((p, i) => (
                  <div key={i} className="nav-item" style={{ background: 'rgba(255,255,255,0.03)', padding: '18px', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '15px', fontWeight: '700', color: 'var(--text-main)' }}>{p.name}</div>
                      <div style={{ fontSize: '12px', color: 'var(--text-dim)', fontFamily: 'monospace' }}>Код: {p.id.slice(0, 12).toUpperCase()}</div>
                    </div>
                    <span className="status-badge" style={{ background: 'rgba(0, 242, 255, 0.1)', color: 'var(--accent)', border: '1px solid var(--accent-glow)' }}>
                      {p.type === 'IT' ? 'РАЗРАБОТКА' : p.type}
                    </span>
                  </div>
                ))
              ) : (
                <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-dim)' }}>
                  <Activity size={40} style={{ opacity: 0.1, marginBottom: '20px' }} />
                  <p style={{ fontSize: '14px' }}>В системной базе данных пока пусто. Отправьте голосовое сообщение или текст боту, чтобы инициализировать первый проект.</p>
                </div>
              )}
            </div>
          </div>

          <div className="glass card">
            <h3 style={{ fontSize: '15px', textTransform: 'uppercase', color: 'var(--text-main)', marginBottom: '30px', borderBottom: '1px solid var(--border)', paddingBottom: '15px' }}>Аналитика Ядра ИИ</h3>
            <div style={{ padding: '25px', background: 'rgba(0, 242, 255, 0.05)', borderLeft: '4px solid var(--accent)', borderRadius: '0 12px 12px 0', marginBottom: '30px' }}>
              <p style={{ fontSize: '14px', color: 'var(--text-main)', lineHeight: '1.7', fontStyle: 'italic' }}>
                "Текущее наблюдение: Обнаружена высокая активность по созданию новых задач. Ваша эффективность за последние 24 часа выросла на 12%. Рекомендую сфокусироваться на проекте 'Разработка', так как он содержит наиболее приоритетные цели."
              </p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div style={{ padding: '15px', background: 'rgba(255,255,255,0.02)', borderRadius: '10px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '10px', fontWeight: '600' }}>
                  <span>Целостность данных</span>
                  <span style={{ color: '#00ff95' }}>98%</span>
                </div>
                <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px' }}>
                  <div style={{ width: '98%', height: '100%', background: '#00ff95', borderRadius: '3px', boxShadow: '0 0 10px rgba(0, 255, 149, 0.3)' }} />
                </div>
              </div>
              <div style={{ padding: '15px', background: 'rgba(255,255,255,0.02)', borderRadius: '10px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '10px', fontWeight: '600' }}>
                  <span>Выполнение целей</span>
                  <span style={{ color: 'var(--accent)' }}>84%</span>
                </div>
                <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px' }}>
                  <div style={{ width: '84%', height: '100%', background: 'var(--accent)', borderRadius: '3px', boxShadow: '0 0 10px var(--accent-glow)' }} />
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
