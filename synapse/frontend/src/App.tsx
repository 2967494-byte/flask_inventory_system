import { useState, useEffect } from 'react'
import {
  LayoutDashboard,
  FolderKanban,
  CheckSquare,
  Wallet,
  Activity,
  Plus,
  CheckCircle2,
  Circle,
  TrendingDown,
  TrendingUp,
  Clock,
  LogOut,
  ShieldCheck
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import './index.css'

const COLORS = ['#00f2ff', '#ff4d4d', '#00ff95', '#ffcc00', '#9945ff', '#ff6b9d', '#4dffa6']

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [projects, setProjects] = useState<any[]>([])
  const [tasks, setTasks] = useState<any[]>([])
  const [transactions, setTransactions] = useState<any[]>([])
  const [stats, setStats] = useState<any>(null)
  const [user, setUser] = useState<any>(null)
  const [financeAnalytics, setFinanceAnalytics] = useState<any>(null)
  const [aiInsight, setAiInsight] = useState<string | null>(null)
  const [selectedProject, setSelectedProject] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [token, setToken] = useState<string | null>(localStorage.getItem('synapse_token'))
  const [authError, setAuthError] = useState(false)

  const apiHost = window.location.hostname
  const BASE_URL = `http://${apiHost}:8001/api/v1`

  useEffect(() => {
    // Check URL for token
    const urlParams = new URLSearchParams(window.location.search)
    const urlToken = urlParams.get('token')
    if (urlToken) {
      localStorage.setItem('synapse_token', urlToken)
      setToken(urlToken)
      window.history.replaceState({}, document.title, "/") // Clean URL
    }
  }, [])

  useEffect(() => {
    if (token) {
      fetchAll()
      fetchUser()
    }
  }, [token])

  const fetchUser = async () => {
    try {
      const config = { headers: { Authorization: `Bearer ${token}` } }
      const res = await axios.get(`${BASE_URL}/user/me`, config)
      setUser(res.data)
    } catch (err) {
      console.error("Ошибка загрузки профиля:", err)
    }
  }

  const fetchFinanceAnalytics = async () => {
    try {
      const config = { headers: { Authorization: `Bearer ${token}` } }
      const res = await axios.get(`${BASE_URL}/analytics/finance`, config)
      setFinanceAnalytics(res.data)
    } catch (err) {
      console.error("Ошибка загрузки аналитики:", err)
    }
  }

  const fetchAll = async () => {
    if (!token) return
    setLoading(true)
    setAuthError(false)
    try {
      const config = { headers: { Authorization: `Bearer ${token}` } }
      const [pRes, tRes, trRes, sRes] = await Promise.all([
        axios.get(`${BASE_URL}/projects`, config),
        axios.get(`${BASE_URL}/tasks`, config),
        axios.get(`${BASE_URL}/transactions`, config),
        axios.get(`${BASE_URL}/dashboard/stats`, config)
      ])
      setProjects(pRes.data)
      setTasks(tRes.data)
      setTransactions(trRes.data)
      setStats(sRes.data)
    } catch (err: any) {
      console.error("Ошибка синхронизации:", err)
      if (err.response?.status === 401) {
        setAuthError(true)
        setToken(null)
        localStorage.removeItem('synapse_token')
      }
    }
    setLoading(false)
  }

  useEffect(() => {
    if (activeTab === 'finance' && token) {
      fetchFinanceAnalytics()
    }
  }, [activeTab])

  const toggleTask = async (id: string, completed: boolean) => {
    try {
      const config = { headers: { Authorization: `Bearer ${token}` } }
      await axios.patch(`${BASE_URL}/tasks/${id}`, { is_completed: !completed }, config)
      fetchAll()
    } catch (err) {
      console.error("Ошибка обновления задачи:", err)
    }
  }

  const logout = () => {
    localStorage.removeItem('synapse_token')
    setToken(null)
    setUser(null)
  }

  if (!token) {
    return (
      <div className="login-screen fade-in">
        <div className="scanline" />
        <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="glass auth-card">
          <div className="logo-main" style={{ textAlign: 'center', marginBottom: '10px' }}>SYNAPSE</div>
          <p style={{ textAlign: 'center', color: 'var(--text-dim)', fontSize: '14px', marginBottom: '30px' }}>PERSONAL_OS ACCESS TERMINAL</p>

          <div style={{ background: 'rgba(0, 242, 255, 0.05)', padding: '20px', borderRadius: '12px', border: '1px solid var(--accent-glow)' }}>
            <h4 style={{ color: 'var(--accent)', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldCheck size={18} /> Авторизация
            </h4>
            <p style={{ fontSize: '13px', lineHeight: '1.6' }}>
              Для входа в систему, пожалуйста, используйте команду <code style={{ color: 'var(--accent)', background: 'rgba(255,255,255,0.05)', padding: '2px 6px', borderRadius: '4px' }}>/login</code> в вашем Telegram-боте.
            </p>
          </div>

          {authError && (
            <p style={{ color: '#ff4d4d', fontSize: '12px', marginTop: '15px', textAlign: 'center' }}>
              Сессия истекла или токен недействителен.
            </p>
          )}

          <div style={{ marginTop: '30px', textAlign: 'center' }}>
            <Activity className="pulse" size={40} style={{ opacity: 0.1 }} />
          </div>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="dashboard-container">
      <div className="scanline" />

      {/* Боковая панель */}
      <aside className="sidebar">
        <div className="logo-section">
          <div className="logo-main">SYNAPSE</div>
          <div className="logo-sub">PERSONAL_OS</div>
        </div>

        {user && (
          <div className="user-profile-section glass">
            {user.profile_photo ? (
              <img src={user.profile_photo} alt="User" className="user-avatar" />
            ) : (
              <div className="user-avatar-placeholder">
                {user.full_name?.charAt(0) || user.username?.charAt(0) || '?'}
              </div>
            )}
            <div className="user-info">
              <div className="user-name">{user.full_name || 'Пользователь'}</div>
              <div className="user-handle">@{user.username || 'unknown'}</div>
            </div>
          </div>
        )}

        <nav className="nav-menu">
          <div className={`nav-link ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>
            <LayoutDashboard size={20} /> <span>Панель</span>
          </div>
          <div className={`nav-link ${activeTab === 'projects' ? 'active' : ''}`} onClick={() => setActiveTab('projects')}>
            <FolderKanban size={20} /> <span>Проекты</span>
          </div>
          <div className={`nav-link ${activeTab === 'tasks' ? 'active' : ''}`} onClick={() => setActiveTab('tasks')}>
            <CheckSquare size={20} /> <span>Задачи</span>
          </div>
          <div className={`nav-link ${activeTab === 'finance' ? 'active' : ''}`} onClick={() => setActiveTab('finance')}>
            <Wallet size={20} /> <span>Финансы</span>
          </div>
        </nav>

        <div className="sidebar-footer">
          <div className="nav-link" onClick={logout} style={{ color: '#ff4d4d' }}>
            <LogOut size={20} /> <span>Выход</span>
          </div>
          <div className="system-status">
            <div className="status-dot pulsed" />
            УЗЕЛ_ОНЛАЙН
          </div>
        </div>
      </aside>

      {/* Основная область */}
      <main className="main-content">
        <header className="main-header">
          <div>
            <div className="breadcrumb">СИСТЕМА / {activeTab.toUpperCase()}</div>
            <h1 className="page-title">
              {activeTab === 'dashboard' && 'Системный Терминал'}
              {activeTab === 'projects' && 'Реестр Проектов'}
              {activeTab === 'tasks' && 'Менеджер Задач'}
              {activeTab === 'finance' && 'Учет Потоков'}
            </h1>
          </div>
          <button className="action-btn" onClick={fetchAll}>
            {loading ? <Activity className="animate-spin" size={18} /> : <Plus size={18} />}
            ОБНОВИТЬ ДАННЫЕ
          </button>
        </header>

        <div className="content-scroll">
          <AnimatePresence mode="wait">
            {activeTab === 'dashboard' && (
              <div className="fade-in">
                <div className="grid-stats">
                  <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="glass card">
                    <div className="card-label">Активные Проекты <FolderKanban size={14} /></div>
                    <div className="stat-value">{stats?.projects_count || 0}</div>
                    <div className="stat-sub" style={{ color: '#00ff95' }}>Система синхронизирована</div>
                  </motion.div>

                  <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.1 }} className="glass card">
                    <div className="card-label">Баланс <Wallet size={14} /></div>
                    <div className="stat-value" style={{ color: (stats?.finance?.balance || 0) < 0 ? '#ff4d4d' : '#00ff95' }}>
                      {stats?.finance?.balance?.toLocaleString() || 0} ₽
                    </div>
                    <div className="stat-sub">Общий поток транзакций</div>
                  </motion.div>

                  <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2 }} className="glass card">
                    <div className="card-label">Выполнение задач <CheckSquare size={14} /></div>
                    <div className="stat-value">{Math.round(stats?.tasks?.percentage || 0)}%</div>
                    <div className="stat-sub">{stats?.tasks?.completed || 0} из {stats?.tasks?.total || 0} завернено</div>
                  </motion.div>
                </div>

                {/* AI Insights Section */}
                <div className="glass card" style={{ marginTop: '30px' }}>
                  <div className="card-header">
                    <h3>🧠 AI-Аналитика</h3>
                    <button
                      className="action-btn"
                      style={{ fontSize: '12px', padding: '8px 16px' }}
                      onClick={async () => {
                        try {
                          const config = { headers: { Authorization: `Bearer ${token}` } }
                          const res = await axios.get(`${BASE_URL}/analytics/ai-insights`, config)
                          setAiInsight(res.data.insight)
                        } catch (err) {
                          console.error("Ошибка AI-инсайта:", err)
                        }
                      }}
                    >
                      Получить инсайт
                    </button>
                  </div>
                  {aiInsight ? (
                    <p style={{ lineHeight: '1.7', color: 'var(--text)', padding: '10px', background: 'rgba(0, 242, 255, 0.03)', borderRadius: '8px', borderLeft: '3px solid var(--accent)' }}>
                      {aiInsight}
                    </p>
                  ) : (
                    <p className="empty-state">Нажмите кнопку выше, чтобы получить персональный AI-инсайт</p>
                  )}
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: '30px', marginTop: '30px' }}>
                  <div className="glass card">
                    <div className="card-header">
                      <h3>Последние Задачи</h3>
                      <span className="live-tag">LIVE</span>
                    </div>
                    <div className="list-container">
                      {tasks.slice(0, 5).map((task) => (
                        <div key={task.id} className="list-item" onClick={() => toggleTask(task.id, task.is_completed)}>
                          {task.is_completed ? <CheckCircle2 size={18} color="#00ff95" /> : <Circle size={18} color="var(--accent)" />}
                          <div style={{ flex: 1, textDecoration: task.is_completed ? 'line-through' : 'none', opacity: task.is_completed ? 0.5 : 1 }}>
                            {task.title}
                          </div>
                          <Clock size={12} color="var(--text-dim)" />
                        </div>
                      ))}
                      {tasks.length === 0 && <p className="empty-state">Нет активных задач</p>}
                    </div>
                  </div>

                  <div className="glass card">
                    <div className="card-header">
                      <h3>Фин. Потоки</h3>
                    </div>
                    <div className="list-container">
                      {transactions.slice(0, 5).map((tr) => (
                        <div key={tr.id} className="list-item">
                          {tr.type === 'income' ? <TrendingUp size={16} color="#00ff95" /> : <TrendingDown size={16} color="#ff4d4d" />}
                          <div style={{ flex: 1 }}>{tr.category || 'Прочее'}</div>
                          <div style={{ fontWeight: '700', color: tr.type === 'income' ? '#00ff95' : '#ff4d4d' }}>
                            {tr.type === 'income' ? '+' : '-'}{tr.amount}
                          </div>
                        </div>
                      ))}
                      {transactions.length === 0 && <p className="empty-state">История пуста</p>}
                    </div>
                  </div>
                </div>
              </div>
            )}
            {activeTab === 'projects' && (
              <div className="fade-in">
                <h2 className="section-title">Список Проектов</h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
                  {projects.map(p => (
                    <div key={p.id} className="glass card project-card">
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '15px' }}>
                        <div>
                          <div style={{ fontSize: '18px', fontWeight: '800', marginBottom: '8px' }}>{p.name}</div>
                          <div className="status-badge">{p.type.toUpperCase()}</div>
                        </div>
                        <button
                          className="action-btn"
                          style={{ fontSize: '11px', padding: '6px 12px' }}
                          onClick={() => setSelectedProject(p)}
                        >
                          Паспорт
                        </button>
                      </div>
                      {p.description && <p style={{ fontSize: '13px', color: 'var(--text-dim)', marginBottom: '10px', lineHeight: '1.5' }}>{p.description.substring(0, 100)}{p.description.length > 100 && '...'}</p>}
                      {p.progress !== undefined && p.progress !== null && (
                        <div style={{ marginTop: '15px' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', marginBottom: '5px' }}>
                            <span>Прогресс</span>
                            <span style={{ color: 'var(--accent)' }}>{p.progress}%</span>
                          </div>
                          <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                            <div style={{ width: `${p.progress}%`, height: '100%', background: 'linear-gradient(90deg, var(--accent), #00ff95)', transition: 'width 0.3s' }} />
                          </div>
                        </div>
                      )}
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-dim)', marginTop: '15px' }}>
                        <span>Создан: {new Date(p.created_at).toLocaleDateString()}</span>
                        {p.deadline && <span style={{ color: 'var(--accent)' }}>⏰ {new Date(p.deadline).toLocaleDateString()}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {activeTab === 'tasks' && (
              <div className="fade-in">
                <h2 className="section-title">Все Задачи</h2>
                <div className="glass card">
                  <div className="list-container">
                    {tasks.map((task) => (
                      <div key={task.id} className="list-item" onClick={() => toggleTask(task.id, task.is_completed)}>
                        {task.is_completed ? <CheckCircle2 size={20} color="#00ff95" /> : <Circle size={20} color="var(--accent)" />}
                        <div style={{ flex: 1, fontSize: '16px', textDecoration: task.is_completed ? 'line-through' : 'none', opacity: task.is_completed ? 0.6 : 1 }}>
                          {task.title}
                        </div>
                        <div className="status-badge" style={{ fontSize: '10px' }}>
                          {projects.find(p => p.id === task.project_id)?.name || 'Личное'}
                        </div>
                      </div>
                    ))}
                    {tasks.length === 0 && <p className="empty-state">Задач пока нет. Отправьте команду боту.</p>}
                  </div>
                </div>
              </div>
            )}
            {activeTab === 'finance' && (
              <div className="fade-in">
                <h2 className="section-title">Финансовая Аналитика</h2>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
                  <div className="glass card">
                    <h3 style={{ marginBottom: '20px' }}>Расходы по категориям</h3>
                    {financeAnalytics && financeAnalytics.categories.length > 0 ? (
                      <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                          <Pie
                            data={financeAnalytics.categories.filter((c: any) => c.expense > 0)}
                            dataKey="expense"
                            nameKey="category"
                            cx="50%"
                            cy="50%"
                            outerRadius={100}
                            label={(entry: any) => `${entry.category}: ${entry.expense}₽`}
                          >
                            {financeAnalytics.categories.map((_: any, index: number) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip />
                        </PieChart>
                      </ResponsiveContainer>
                    ) : (
                      <p className="empty-state">Нет данных о расходах</p>
                    )}
                  </div>

                  <div className="glass card">
                    <h3 style={{ marginBottom: '20px' }}>Доходы  по категориям</h3>
                    {financeAnalytics && financeAnalytics.categories.filter((c: any) => c.income > 0).length > 0 ? (
                      <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                          <Pie
                            data={financeAnalytics.categories.filter((c: any) => c.income > 0)}
                            dataKey="income"
                            nameKey="category"
                            cx="50%"
                            cy="50%"
                            outerRadius={100}
                            label={(entry: any) => `${entry.category}: ${entry.income}₽`}
                          >
                            {financeAnalytics.categories.map((_: any, index: number) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip />
                        </PieChart>
                      </ResponsiveContainer>
                    ) : (
                      <p className="empty-state">Нет данных о доходах</p>
                    )}
                  </div>
                </div>

                <div className="glass card" style={{ marginTop: '30px' }}>
                  <h3 style={{ marginBottom: '20px' }}>Детализация по категориям</h3>
                  <div className="list-container">
                    {financeAnalytics && financeAnalytics.categories.map((cat: any) => (
                      <div key={cat.category} className="list-item">
                        <div style={{ flex: 1, fontWeight: '700' }}>{cat.category}</div>
                        <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
                          {cat.income > 0 && <span style={{ color: '#00ff95' }}>+{cat.income}₽</span>}
                          {cat.expense > 0 && <span style={{ color: '#ff4d4d' }}>-{cat.expense}₽</span>}
                          <span style={{ color: 'var(--text-dim)', fontSize: '12px' }}>({cat.count} операций)</span>
                        </div>
                      </div>
                    ))}
                    {(!financeAnalytics || financeAnalytics.categories.length === 0) && (
                      <p className="empty-state">Нет финансовых данных. Добавьте транзакции через бота.</p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </AnimatePresence>
        </div>
      </main>

      {/* Project Passport Modal */}
      {selectedProject && (
        <div className="modal-overlay" onClick={() => setSelectedProject(null)}>
          <motion.div
            className="modal-content glass"
            onClick={(e) => e.stopPropagation()}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <div className="modal-header">
              <h2 style={{ fontSize: '24px', fontWeight: '900' }}>Паспорт проекта</h2>
              <button className="close-btn" onClick={() => setSelectedProject(null)}>✕</button>
            </div>
            <div className="modal-body">
              <div style={{ marginBottom: '20px' }}>
                <h3 style={{ fontSize: '28px', marginBottom: '5px' }}>{selectedProject.name}</h3>
                <span className="status-badge">{selectedProject.type}</span>
              </div>

              <div className="form-group">
                <label>Описание</label>
                <textarea
                  value={selectedProject.description || ''}
                  onChange={(e) => setSelectedProject({ ...selectedProject, description: e.target.value })}
                  placeholder="Опишите проект..."
                  rows={4}
                />
              </div>

              <div className="form-group">
                <label>Цели и задачи</label>
                <textarea
                  value={selectedProject.goals || ''}
                  onChange={(e) => setSelectedProject({ ...selectedProject, goals: e.target.value })}
                  placeholder="Что нужно достичь..."
                  rows={3}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                <div className="form-group">
                  <label>Дедлайн</label>
                  <input
                    type="date"
                    value={selectedProject.deadline ? selectedProject.deadline.split('T')[0] : ''}
                    onChange={(e) => setSelectedProject({ ...selectedProject, deadline: e.target.value ? new Date(e.target.value).toISOString() : null })}
                  />
                </div>

                <div className="form-group">
                  <label>Бюджет (₽)</label>
                  <input
                    type="number"
                    value={selectedProject.budget || ''}
                    onChange={(e) => setSelectedProject({ ...selectedProject, budget: parseFloat(e.target.value) || 0 })}
                    placeholder="0"
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Прогресс: {selectedProject.progress || 0}%</label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={selectedProject.progress || 0}
                  onChange={(e) => setSelectedProject({ ...selectedProject, progress: parseInt(e.target.value) })}
                  style={{ width: '100%' }}
                />
              </div>

              <div className="form-group">
                <label>Заметки</label>
                <textarea
                  value={selectedProject.notes || ''}
                  onChange={(e) => setSelectedProject({ ...selectedProject, notes: e.target.value })}
                  placeholder="Дополнительная информация..."
                  rows={3}
                />
              </div>

              <div className="form-group">
                <label>Теги (через запятую)</label>
                <input
                  type="text"
                  value={Array.isArray(selectedProject.tags) ? selectedProject.tags.join(', ') : ''}
                  onChange={(e) => setSelectedProject({ ...selectedProject, tags: e.target.value.split(',').map((t: string) => t.trim()).filter((t: string) => t) })}
                  placeholder="frontend, дизайн, срочно"
                />
              </div>

              <button
                className="action-btn"
                style={{ width: '100%', marginTop: '20px', padding: '12px' }}
                onClick={async () => {
                  console.log("Кнопка нажата, начинаю сохранение...");
                  console.log("Данные проекта:", selectedProject);
                  try {
                    const config = { headers: { Authorization: `Bearer ${token}` } }
                    console.log("Отправляю запрос на:", `${BASE_URL}/projects/${selectedProject.id}/passport`);
                    const response = await axios.patch(`${BASE_URL}/projects/${selectedProject.id}/passport`, {
                      description: selectedProject.description,
                      goals: selectedProject.goals,
                      deadline: selectedProject.deadline,
                      budget: selectedProject.budget,
                      progress: selectedProject.progress,
                      notes: selectedProject.notes,
                      tags: selectedProject.tags
                    }, config)
                    console.log("Успешно сохранено:", response.data);
                    fetchAll()
                    setSelectedProject(null)
                  } catch (err: any) {
                    console.error("Ошибка сохранения паспорта:", err);
                    console.error("Детали ошибки:", err.response?.data);
                    alert(`Ошибка сохранения: ${err.response?.data?.detail || err.message}`)
                  }
                }}
              >
                Сохранить паспорт
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  )
}

export default App
