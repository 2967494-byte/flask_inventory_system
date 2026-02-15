import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Lightbulb, Tag, Calendar, ArrowLeft } from 'lucide-react';

interface IdeaDetailViewProps {
  ideaId: string;
  onBack: () => void;
  token: string | null;
  BASE_URL: string;
}

interface Idea {
  id: string;
  content: string;
  tags: string[];
  created_at: string;
  project?: {
    id: string;
    name: string;
  };
}

const IdeaDetailView: React.FC<IdeaDetailViewProps> = ({ ideaId, onBack, token, BASE_URL }) => {
  const [idea, setIdea] = useState<Idea | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchIdeaDetails();
  }, [ideaId, token, BASE_URL]);

  const fetchIdeaDetails = async () => {
    if (!token) return;
    setLoading(true);
    try {
      const config = { headers: { Authorization: `Bearer ${token}` } };
      const res = await axios.get(`${BASE_URL}/notes/${ideaId}`, config);
      setIdea(res.data);
    } catch (err) {
      console.error("Ошибка загрузки деталей идеи:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="fade-in">
        <button onClick={onBack} className="action-btn" style={{ marginBottom: '20px' }}>
          <ArrowLeft size={18} style={{ marginRight: '8px' }} />
          Назад к идеям
        </button>
        <h2 className="section-title">Загрузка идеи...</h2>
        <div className="glass card">
          <p className="empty-state">Пожалуйста, подождите.</p>
        </div>
      </div>
    );
  }

  if (!idea) {
    return (
      <div className="fade-in">
        <button onClick={onBack} className="action-btn" style={{ marginBottom: '20px' }}>
          <ArrowLeft size={18} style={{ marginRight: '8px' }} />
          Назад к идеям
        </button>
        <h2 className="section-title">Идея не найдена</h2>
        <div className="glass card">
          <p className="empty-state">Не удалось загрузить детали идеи.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fade-in">
      <button onClick={onBack} className="action-btn" style={{ marginBottom: '20px' }}>
        <ArrowLeft size={18} style={{ marginRight: '8px' }} />
        Назад к идеям
      </button>

      <h2 className="section-title">Детали Идеи</h2>

      <div className="glass card" style={{ marginBottom: '20px' }}>
        <div className="card-header">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Lightbulb size={20} color="var(--accent)" />
            Описание
          </h3>
        </div>

        <div style={{
          background: 'rgba(0, 242, 255, 0.05)',
          borderRadius: '8px',
          padding: '20px',
          borderLeft: '3px solid var(--accent)',
          marginBottom: '20px'
        }}>
          <p style={{
            lineHeight: '1.8',
            fontSize: '16px',
            margin: 0,
            whiteSpace: 'pre-wrap'
          }}>
            {idea.content}
          </p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          {/* Дата создания */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Calendar size={16} style={{ opacity: 0.5 }} />
            <span style={{ fontSize: '13px', color: 'var(--text-dim)' }}>
              Создано: {new Date(idea.created_at).toLocaleDateString('ru-RU', {
                day: 'numeric',
                month: 'long',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </span>
          </div>

          {/* Проект */}
          {idea.project && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '13px', color: 'var(--text-dim)' }}>Проект:</span>
              <span className="status-badge" style={{ fontSize: '12px' }}>
                {idea.project.name}
              </span>
            </div>
          )}

          {/* Теги */}
          {idea.tags && idea.tags.length > 0 && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <Tag size={16} style={{ opacity: 0.5 }} />
                <span style={{ fontSize: '13px', color: 'var(--text-dim)' }}>Теги:</span>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {idea.tags.map((tag, index) => (
                  <span
                    key={index}
                    style={{
                      background: 'rgba(0, 242, 255, 0.1)',
                      padding: '6px 12px',
                      borderRadius: '6px',
                      fontSize: '12px',
                      color: 'var(--accent)',
                      border: '1px solid rgba(0, 242, 255, 0.2)'
                    }}
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Информационная карточка о будущих функциях */}
      <div className="glass card">
        <div className="card-header">
          <h3 style={{ fontSize: '14px', opacity: 0.7 }}>Скоро появится</h3>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
          <div style={{ padding: '15px', background: 'rgba(0, 242, 255, 0.03)', borderRadius: '8px' }}>
            <div style={{ fontSize: '12px', color: 'var(--text-dim)', marginBottom: '5px' }}>💬 Комментарии</div>
            <div style={{ fontSize: '11px', opacity: 0.5 }}>Обсуждайте идеи с командой</div>
          </div>
          <div style={{ padding: '15px', background: 'rgba(0, 242, 255, 0.03)', borderRadius: '8px' }}>
            <div style={{ fontSize: '12px', color: 'var(--text-dim)', marginBottom: '5px' }}>✅ Чек-лист</div>
            <div style={{ fontSize: '11px', opacity: 0.5 }}>Отслеживайте прогресс</div>
          </div>
          <div style={{ padding: '15px', background: 'rgba(0, 242, 255, 0.03)', borderRadius: '8px' }}>
            <div style={{ fontSize: '12px', color: 'var(--text-dim)', marginBottom: '5px' }}>🤖 AI Предложения</div>
            <div style={{ fontSize: '11px', opacity: 0.5 }}>Умные рекомендации</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IdeaDetailView;
