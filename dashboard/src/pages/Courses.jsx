import { useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { BookOpen, TrendingUp, Search, ChevronLeft } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import db from '../data/db.json';

const COLORS = ['#10b981', '#ef4444', '#3b82f6', '#f59e0b', '#8b5cf6'];

export default function Courses() {
  const { code } = useParams();
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');

  const courseStatsList = useMemo(() => {
    const stats = {};
    Object.keys(db.courses).forEach(c => {
      stats[c] = { name: c, fullCode: db.courses[c], total: 0, count: 0, passes: 0, grades: {}, is_pnp: false };
    });
    
    db.grades.forEach(g => {
      const s = stats[g.course];
      if (s) {
        if (g.is_pnp) s.is_pnp = true;
        if (!g.is_pnp) s.total += g.score;
        
        s.count += 1;
        if (g.grade !== 'F' && g.grade !== 'NP') s.passes += 1;
        
        // Grade distribution
        let baseGrade = g.grade;
        if (!g.is_pnp && (g.grade.startsWith('A') || g.grade.startsWith('B') || g.grade.startsWith('C') || g.grade.startsWith('D'))) {
          baseGrade = g.grade[0];
        }
        s.grades[baseGrade] = (s.grades[baseGrade] || 0) + 1;
      }
    });
    
    return Object.values(stats).map(s => ({
      ...s,
      passRate: s.count > 0 ? (s.passes / s.count) * 100 : 0,
      avgScore: (s.count > 0 && !s.is_pnp) ? s.total / s.count : 0
    }));
  }, []);

  const course = useMemo(() => {
    if (!code) return null;
    return courseStatsList.find(c => c.name === code);
  }, [code, courseStatsList]);

  const filteredCourses = useMemo(() => {
    if (!searchTerm) return courseStatsList;
    const term = searchTerm.toLowerCase();
    return courseStatsList.filter(c => 
      c.name.toLowerCase().includes(term) || c.fullCode.toLowerCase().includes(term)
    );
  }, [searchTerm, courseStatsList]);

  if (course) {
    const gradeData = Object.keys(course.grades).sort().map(k => ({
      name: k,
      value: course.grades[k]
    }));
    
    return (
      <div className="flex-column gap-4">
        <button 
          onClick={() => navigate('/courses')} 
          style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem', width: 'fit-content' }}
        >
          <ChevronLeft size={20} />
          العودة للمقررات
        </button>
        
        <div className="glass-panel">
          <div className="flex-between mb-2">
            <h2>{course.name}</h2>
            <BookOpen size={24} color="var(--accent-primary)" />
          </div>
          <p className="subtitle" style={{ fontSize: '1.1rem' }}>الكود: {course.fullCode}</p>
        </div>
        
        <div className="grid-cols-3">
          <div className="glass-panel flex-column">
            <span className="subtitle">إجمالي الطلاب</span>
            <div className="stat-value">{course.count}</div>
          </div>
          <div className="glass-panel flex-column">
            <span className="subtitle">نسبة النجاح</span>
            <div className="stat-value" style={{ color: course.passRate >= 50 ? 'var(--accent-success)' : 'var(--accent-danger)' }}>
              {course.passRate.toFixed(1)}%
            </div>
          </div>
          <div className="glass-panel flex-column">
            <span className="subtitle">متوسط الدرجات</span>
            <div className="stat-value">{course.is_pnp ? '-' : course.avgScore.toFixed(1)}</div>
          </div>
        </div>
        
        <div className="glass-panel">
          <h3>توزيع التقديرات في هذا المقرر</h3>
          <div style={{ height: 400 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={gradeData}>
                <XAxis dataKey="name" stroke="var(--text-secondary)" />
                <YAxis stroke="var(--text-secondary)" />
                <Tooltip contentStyle={{ background: 'var(--bg-color)', border: 'none', borderRadius: 8 }} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {gradeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-column gap-4">
      <div className="flex-between">
        <div>
          <h1 className="text-gradient">المقررات الدراسية</h1>
          <p className="subtitle">تصفح إحصائيات ونسب النجاح لكل مقرر</p>
        </div>
        
        <div style={{ position: 'relative', width: 300 }}>
          <Search size={20} style={{ position: 'absolute', right: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
          <input 
            type="text" 
            className="input-glass" 
            placeholder="بحث عن مقرر..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ paddingRight: '3rem' }}
          />
        </div>
      </div>
      
      <div className="grid-cols-3">
        {filteredCourses.map(c => (
          <div key={c.name} className="glass-panel flex-column gap-2" style={{ cursor: 'pointer' }} onClick={() => navigate(`/courses/${c.name}`)}>
            <div className="flex-between">
              <h3 style={{ margin: 0, fontSize: '1.1rem' }}>{c.name}</h3>
              <BookOpen size={18} color="var(--accent-primary)" />
            </div>
            <div className="subtitle" style={{ fontSize: '0.8rem' }}>{c.fullCode}</div>
            
            <div className="flex-between mt-2" style={{ borderTop: '1px solid var(--card-border)', paddingTop: '1rem' }}>
              <div className="flex-column">
                <span className="subtitle" style={{ fontSize: '0.7rem' }}>نسبة النجاح</span>
                <strong style={{ color: c.passRate >= 50 ? 'var(--accent-success)' : 'var(--accent-danger)' }}>
                  {c.passRate.toFixed(1)}%
                </strong>
              </div>
              <div className="flex-column">
                <span className="subtitle" style={{ fontSize: '0.7rem' }}>الطلاب</span>
                <strong>{c.count}</strong>
              </div>
            </div>
            
            {/* Progress bar */}
            <div style={{ width: '100%', height: 4, background: 'rgba(255,255,255,0.1)', borderRadius: 2, marginTop: '0.5rem', overflow: 'hidden' }}>
              <div style={{ width: `${c.passRate}%`, height: '100%', background: c.passRate >= 50 ? 'var(--accent-success)' : 'var(--accent-danger)' }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
