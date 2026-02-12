import { useState } from 'react';
import {
  Search,
  TrendingUp,
  Image as ImageIcon,
  ArrowRight,
  MessageSquare,
  Bot
} from 'lucide-react';
import './App.css';

function App() {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <div className="app-container">
      {/* Navigation */}
      <nav className="glass" style={{ margin: '20px 5%', padding: '15px 30px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'sticky', top: '20px', zIndex: 1000 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div className="gradient-text" style={{ fontSize: '24px', fontWeight: '800', letterSpacing: '-1px' }}>
            ASAUDA AI
          </div>
          <div className="tag" style={{ background: 'rgba(59, 130, 246, 0.1)', color: '#3b82f6', border: '1px solid rgba(59, 130, 246, 0.2)' }}>BETA</div>
        </div>
        <div style={{ display: 'flex', gap: '30px', color: 'var(--text-secondary)', fontWeight: '500' }}>
          <a href="#" style={{ transition: 'color 0.3s' }}>Predict</a>
          <a href="#" style={{ transition: 'color 0.3s' }}>Catalog</a>
          <a href="#" style={{ transition: 'color 0.3s' }}>Insights</a>
        </div>
        <button className="btn-primary" style={{ padding: '10px 20px' }}>
          Launch Agent
        </button>
      </nav>

      <main className="main-content">
        {/* Hero Section */}
        <section className="hero-section">
          <h1 className="hero-title">
            Управляйте неликвидами с <br />
            <span className="gradient-text">интеллектом нового уровня</span>
          </h1>
          <p className="hero-subtitle">
            Первая в России AI-система для автоматизации B2B продаж складских остатков.
            Поиск, оценка и реализация — всё в одном месте.
          </p>

          <div className="search-box">
            <Search className="search-icon" size={24} />
            <input
              type="text"
              className="search-input"
              placeholder="Например: Понадобятся ли запчасти для спецтехники в Хабаровске в марте?"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <div className="tag-list">
              <span className="tag">Прогноз спроса</span>
              <span className="tag">Оценка стоимости</span>
              <span className="tag">Поиск контрагентов</span>
            </div>
          </div>
        </section>

        {/* Dashboard Modules */}
        <div className="dashboard-grid">
          {/* Module 1: AI Predict */}
          <div className="glass card ai-card">
            <div className="feature-icon">
              <TrendingUp size={24} />
            </div>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '12px' }}>AI Оценка и Спрос</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
              Анализируем тысячи сделок в вашей категории для определения оптимальной цены
              реализации ваших остатков с точностью до 95%.
            </p>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-primary)', fontWeight: '600', cursor: 'pointer' }}>
              Рассчитать стоимость <ArrowRight size={18} />
            </div>
          </div>

          {/* Module 2: AI Catalog */}
          <div className="glass card ai-card">
            <div className="feature-icon">
              <ImageIcon size={24} />
            </div>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '12px' }}>Авто-Каталогизация</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
              Просто загрузите фото или накладную. AI автоматически создаст карточки товаров,
              подберет категории и напишет продающее описание.
            </p>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-primary)', fontWeight: '600', cursor: 'pointer' }}>
              Загрузить файлы <ArrowRight size={18} />
            </div>
          </div>

          {/* Module 3: AI Assistant */}
          <div className="glass card ai-card">
            <div className="feature-icon">
              <Bot size={24} />
            </div>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '12px' }}>AI Переговорщик</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
              Ваш персональный агент, который отвечает на вопросы покупателей 24/7 и
              согласовывает базовые условия сделки по заданным правилам.
            </p>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-primary)', fontWeight: '600', cursor: 'pointer' }}>
              Настроить агента <ArrowRight size={18} />
            </div>
          </div>
        </div>

        {/* Status Bar */}
        <div className="glass" style={{ marginTop: '60px', padding: '30px', display: 'flex', justifyContent: 'space-around', textAlign: 'center' }}>
          <div>
            <div style={{ fontSize: '2rem', fontWeight: '800', color: 'var(--accent-primary)' }}>1.2M+</div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Товаров проанализировано</div>
          </div>
          <div style={{ width: '1px', background: 'var(--glass-border)' }}></div>
          <div>
            <div style={{ fontSize: '2rem', fontWeight: '800', color: 'var(--accent-secondary)' }}>420</div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Успешных сделок сегодня</div>
          </div>
          <div style={{ width: '1px', background: 'var(--glass-border)' }}></div>
          <div>
            <div style={{ fontSize: '2rem', fontWeight: '800', color: '#10b981' }}>-30%</div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Средний срок реализации</div>
          </div>
        </div>
      </main>

      {/* Floating Chat */}
      <div className="glass" style={{ position: 'fixed', bottom: '40px', right: '40px', width: '60px', height: '60px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', boxShadow: '0 10px 40px rgba(0,0,0,0.5)', border: '1px solid var(--accent-primary)' }}>
        <MessageSquare color="var(--accent-primary)" size={28} />
      </div>
    </div>
  );
}

export default App;
