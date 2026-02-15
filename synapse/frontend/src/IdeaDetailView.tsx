import React from 'react';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Lightbulb, CheckSquare, MessageSquare, Brain, Plus, Trash2 } from 'lucide-react';

interface IdeaDetailViewProps {
  ideaId: string;
  onBack: () => void;
  token: string | null;
  BASE_URL: string;
}

interface Idea {
  id: string;
  content: string;
  ai_suggestions: string[];
  comments: Comment[];
  checklist: ChecklistItem[];
  project_id: string | null;
  tags: string[];
  created_at: string;
}

interface Comment {
  id: string;
  text: string;
  created_at: string;
}

interface ChecklistItem {
  id: string;
  text: string;
  is_completed: boolean;
}

const IdeaDetailView: React.FC<IdeaDetailViewProps> = ({ ideaId, onBack, token, BASE_URL }) => {
  const [idea, setIdea] = useState<Idea | null>(null);
  const [loading, setLoading] = useState(true);
  const [newComment, setNewComment] = useState('');
  const [newChecklistItem, setNewChecklistItem] = useState('');

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

  const handleAddComment = async () => {
    if (!token || !newComment.trim()) return;
    try {
      const config = { headers: { Authorization: `Bearer ${token}` } };
      await axios.post(`${BASE_URL}/notes/${ideaId}/comments`, { text: newComment }, config);
      setNewComment('');
      fetchIdeaDetails();
    } catch (err) {
      console.error("Ошибка добавления комментария:", err);
    }
  };

  const handleDeleteComment = async (commentId: string) => {
    if (!token) return;
    try {
      const config = { headers: { Authorization: `Bearer ${token}` } };
      await axios.delete(`${BASE_URL}/notes/${ideaId}/comments/${commentId}`, config);
      fetchIdeaDetails();
    } catch (err) {
      console.error("Ошибка удаления комментария:", err);
    }
  };

  const handleAddChecklistItem = async () => {
    if (!token || !newChecklistItem.trim()) return;
    try {
      const config = { headers: { Authorization: `Bearer ${token}` } };
      await axios.post(`${BASE_URL}/notes/${ideaId}/checklist`, { text: newChecklistItem }, config);
      setNewChecklistItem('');
      fetchIdeaDetails();
    } catch (err) {
      console.error("Ошибка добавления пункта чек-листа:", err);
    }
  };

  const handleToggleChecklistItem = async (itemId: string, isCompleted: boolean) => {
    if (!token) return;
    try {
      const config = { headers: { Authorization: `Bearer ${token}` } };
      await axios.patch(`${BASE_URL}/notes/${ideaId}/checklist/${itemId}`, { is_completed: !isCompleted }, config);
      fetchIdeaDetails();
    } catch (err) {
      console.error("Ошибка обновления пункта чек-листа:", err);
    }
  };

  const handleDeleteChecklistItem = async (itemId: string) => {
    if (!token) return;
    try {
      const config = { headers: { Authorization: `Bearer ${token}` } };
      await axios.delete(`${BASE_URL}/notes/${ideaId}/checklist/${itemId}`, config);
      fetchIdeaDetails();
    } catch (err) {
      console.error("Ошибка удаления пункта чек-листа:", err);
    }
  };

  if (loading) {
    return (
      <div className="fade-in">
        <button onClick={onBack} className="back-button">← Назад к идеям</button>
        <h2 className="section-title">Загрузка идеи...</h2>
        <div className="glass card">
          <p>Пожалуйста, подождите.</p>
        </div>
      </div>
    );
  }

  if (!idea) {
    return (
      <div className="fade-in">
        <button onClick={onBack} className="back-button">← Назад к идеям</button>
        <h2 className="section-title">Идея не найдена</h2>
        <div className="glass card">
          <p>Не удалось загрузить детали идеи.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fade-in">
      <button onClick={onBack} className="back-button">← Назад к идеям</button>
      <h2 className="section-title">Детали Идеи: {idea.content.substring(0, 50)}...</h2>

      <div className="glass card" style={{ marginBottom: '20px' }}>
        <div className="card-header">
          <h3><Lightbulb size={18} /> Описание Идеи</h3>
        </div>
        <p style={{ lineHeight: '1.6' }}>{idea.content}</p>
        {idea.tags && idea.tags.length > 0 && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '10px' }}>
            {idea.tags.map((tag, index) => (
              <span
                key={index}
                style={{
                  background: 'rgba(0, 242, 255, 0.1)',
                  padding: '4px 8px',
                  borderRadius: '4px',
                  fontSize: '11px',
                  color: 'var(--accent)'
                }}
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="glass card" style={{ marginBottom: '20px' }}>
        <div className="card-header">
          <h3><Brain size={18} /> Предложения AI</h3>
          <button
            className="action-btn"
            style={{ fontSize: '12px', padding: '8px 16px' }}
            onClick={async () => {
              if (!token) return;
              try {
                const config = { headers: { Authorization: `Bearer ${token}` } };
                await axios.post(`${BASE_URL}/notes/${ideaId}/ai-suggestions`, {}, config);
                fetchIdeaDetails();
              } catch (err) {
                console.error("Ошибка получения AI-предложений:", err);
              }
            }}
          >
            Сгенерировать
          </button>
        </div>
        {idea.ai_suggestions && idea.ai_suggestions.length > 0 ? (
          <div className="list-container">
            {idea.ai_suggestions.map((suggestion, index) => (
              <div key={index} className="list-item" style={{ borderLeft: '3px solid var(--accent)' }}>
                {suggestion}
              </div>
            ))}
          </div>
        ) : (
          <p className="empty-state">Нажмите кнопку "Сгенерировать", чтобы получить предложения AI.</p>
        )}
      </div>

      <div className="glass card" style={{ marginBottom: '20px' }}>
        <div className="card-header">
          <h3><MessageSquare size={18} /> Комментарии</h3>
        </div>
        <div className="list-container">
          {idea.comments && idea.comments.length > 0 ? (
            idea.comments.map((comment) => (
              <div key={comment.id} className="list-item">
                <div style={{ flex: 1 }}>{comment.text}</div>
                <div style={{ fontSize: '10px', color: 'var(--text-dim)' }}>
                  {new Date(comment.created_at).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })}
                </div>
                <button onClick={() => handleDeleteComment(comment.id)} className="icon-btn"><Trash2 size={14} /></button>
              </div>
            ))
          ) : (
            <p className="empty-state">Пока нет комментариев.</p>
          )}
        </div>
        <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
          <input
            type="text"
            className="form-input"
            placeholder="Добавить комментарий..."
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            onKeyPress={(e) => { if (e.key === 'Enter') handleAddComment(); }}
          />
          <button onClick={handleAddComment} className="action-btn"><Plus size={18} /></button>
        </div>
      </div>

      <div className="glass card">
        <div className="card-header">
          <h3><CheckSquare size={18} /> Чек-лист</h3>
        </div>
        <div className="list-container">
          {idea.checklist && idea.checklist.length > 0 ? (
            idea.checklist.map((item) => (
              <div key={item.id} className="list-item">
                <input
                  type="checkbox"
                  checked={item.is_completed}
                  onChange={() => handleToggleChecklistItem(item.id, item.is_completed)}
                  style={{ marginRight: '10px' }}
                />
                <span style={{ flex: 1, textDecoration: item.is_completed ? 'line-through' : 'none' }}>
                  {item.text}
                </span>
                <button onClick={() => handleDeleteChecklistItem(item.id)} className="icon-btn"><Trash2 size={14} /></button>
              </div>
            ))
          ) : (
            <p className="empty-state">Чек-лист пуст.</p>
          )}
        </div>
        <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
          <input
            type="text"
            className="form-input"
            placeholder="Добавить пункт чек-листа..."
            value={newChecklistItem}
            onChange={(e) => setNewChecklistItem(e.target.value)}
            onKeyPress={(e) => { if (e.key === 'Enter') handleAddChecklistItem(); }}
          />
          <button onClick={handleAddChecklistItem} className="action-btn"><Plus size={18} /></button>
        </div>
      </div>
    </div>
  );
};

export default IdeaDetailView;