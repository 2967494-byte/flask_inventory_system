import React from 'react';
import { Lightbulb, Tag, Calendar } from 'lucide-react';

interface Note {
  id: string;
  content: string;
  tags: string[];
  created_at: string;
  project?: {
    name: string;
  };
}

interface IdeasSectionProps {
  notes: Note[];
  projects: any[];
  onIdeaClick: (ideaId: string) => void;
}

const IdeasSection: React.FC<IdeasSectionProps> = ({ notes, projects, onIdeaClick }) => {
  const getProjectName = (projectId: string | null) => {
    if (!projectId) return 'Без проекта';
    const project = projects.find(p => p.id === projectId);
    return project?.name || 'Без проекта';
  };

  return (
    <div className="fade-in">
      <h2 className="section-title">Банк Идей</h2>
      
      <div className="glass card" style={{ marginBottom: '30px' }}>
        <div className="card-header">
          <h3>Все идеи ({notes.length})</h3>
          <div style={{ fontSize: '12px', color: 'var(--text-dim)' }}>
            Идеи сохраняются автоматически, когда вы говорите "у меня есть идея" или "хочу запомнить" в Telegram
          </div>
        </div>
        
        {notes.length === 0 ? (
          <div className="empty-state">
            <Lightbulb size={40} style={{ opacity: 0.3, marginBottom: '15px' }} />
            <p>Идей пока нет. Отправьте сообщение в Telegram с идеей, и она появится здесь.</p>
            <p style={{ fontSize: '12px', marginTop: '10px' }}>
              Пример: "У меня есть идея создать мобильное приложение для учета финансов"
            </p>
          </div>
        ) : (
          <div className="list-container">
            {notes.map((note) => (
              <div key={note.id} className="list-item" style={{ alignItems: 'flex-start', cursor: 'pointer' }} onClick={() => onIdeaClick(note.id)}>
                <div style={{ 
                  background: 'rgba(0, 242, 255, 0.1)', 
                  borderRadius: '8px', 
                  padding: '12px', 
                  flex: 1,
                  borderLeft: '3px solid var(--accent)'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Lightbulb size={16} color="var(--accent)" />
                      <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>
                        {new Date(note.created_at).toLocaleDateString('ru-RU', {
                          day: 'numeric',
                          month: 'long',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </span>
                    </div>
                    <div className="status-badge" style={{ fontSize: '10px' }}>
                      {getProjectName(note.project?.id || null)}
                    </div>
                  </div>
                  
                  <p style={{ margin: '10px 0', lineHeight: '1.6' }}>{note.content}</p>
                  
                  {note.tags && note.tags.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '10px' }}>
                      <Tag size={12} style={{ opacity: 0.5 }} />
                      {note.tags.map((tag, index) => (
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
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="glass card">
        <h3 style={{ marginBottom: '15px' }}>Как это работает?</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
          <div style={{ padding: '15px', background: 'rgba(0, 242, 255, 0.05)', borderRadius: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
              <div style={{ 
                width: '30px', 
                height: '30px', 
                background: 'rgba(0, 242, 255, 0.2)', 
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <span style={{ fontSize: '18px' }}>1</span>
              </div>
              <h4 style={{ fontSize: '14px', margin: 0 }}>Отправьте идею в Telegram</h4>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--text-dim)', lineHeight: '1.5' }}>
              Напишите боту: "У меня есть идея..." или "Хочу запомнить..."
            </p>
          </div>

          <div style={{ padding: '15px', background: 'rgba(0, 242, 255, 0.05)', borderRadius: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
              <div style={{ 
                width: '30px', 
                height: '30px', 
                background: 'rgba(0, 242, 255, 0.2)', 
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <span style={{ fontSize: '18px' }}>2</span>
              </div>
              <h4 style={{ fontSize: '14px', margin: 0 }}>AI анализирует текст</h4>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--text-dim)', lineHeight: '1.5' }}>
              Система автоматически определяет, что это идея и сохраняет ее
            </p>
          </div>

          <div style={{ padding: '15px', background: 'rgba(0, 242, 255, 0.05)', borderRadius: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
              <div style={{ 
                width: '30px', 
                height: '30px', 
                background: 'rgba(0, 242, 255, 0.2)', 
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <span style={{ fontSize: '18px' }}>3</span>
              </div>
              <h4 style={{ fontSize: '14px', margin: 0 }}>Идея сохраняется</h4>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--text-dim)', lineHeight: '1.5' }}>
              Все идеи хранятся здесь и никогда не теряются
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IdeasSection;