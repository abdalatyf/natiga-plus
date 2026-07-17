import { useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Search, User, FileText, ChevronLeft, Award } from 'lucide-react';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Tooltip } from 'recharts';
import db from '../data/db.json';

export default function Students() {
  const { seat } = useParams();
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');

  const student = useMemo(() => {
    if (!seat) return null;
    return db.students.find(s => s.seat === seat);
  }, [seat]);

  const studentGrades = useMemo(() => {
    if (!seat) return [];
    return db.grades.filter(g => g.seat === seat).map(g => ({
      ...g,
      fullCourseName: db.courses[g.course] || g.course
    }));
  }, [seat]);

  const radarData = useMemo(() => {
    return studentGrades.filter(g => !g.is_pnp).map(g => ({
      subject: g.course,
      points: g.points
    }));
  }, [studentGrades]);

  const searchResults = useMemo(() => {
    if (searchTerm.length < 2) return [];
    const term = searchTerm.toLowerCase();
    return db.students.filter(s => 
      s.name.toLowerCase().includes(term) || s.seat.includes(term)
    ).slice(0, 10);
  }, [searchTerm]);

  if (student) {
    const sem1Grades = studentGrades.filter(g => g.semester === 1);
    const sem2Grades = studentGrades.filter(g => g.semester === 2);

    return (
      <div className="flex-column gap-4">
        <button 
          onClick={() => navigate('/students')} 
          style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem', width: 'fit-content' }}
        >
          <ChevronLeft size={20} />
          العودة للبحث
        </button>
        
        <div className="grid-cols-2">
          {/* Profile Card */}
          <div className="glass-panel flex-column gap-3">
            <div className="flex-center" style={{ flexDirection: 'column', gap: '1rem', padding: '1rem 0' }}>
              <div style={{ width: 80, height: 80, borderRadius: '50%', background: 'var(--accent-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <User size={40} color="white" />
              </div>
              <h2 style={{ textAlign: 'center', margin: 0 }}>{student.name}</h2>
              <span className={`badge ${student.failed ? 'badge-danger' : 'badge-success'}`}>
                {student.failed ? 'راسب' : 'ناجح'}
              </span>
            </div>
            
            <div className="flex-column gap-2" style={{ borderTop: '1px solid var(--card-border)', paddingTop: '1.5rem' }}>
              <div className="flex-between">
                <span className="subtitle">رقم الجلوس</span>
                <strong>{student.seat}</strong>
              </div>
              <div className="flex-between">
                <span className="subtitle">الترتيب العام</span>
                <strong style={{ color: 'var(--accent-secondary)', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                  <Award size={16} /> #{student.rank} من {db.students.length}
                </strong>
              </div>
              <div className="flex-between">
                <span className="subtitle">الجنسية</span>
                <strong>{student.nationality}</strong>
              </div>
              <div className="flex-between">
                <span className="subtitle">المعدل التراكمي (GPAU)</span>
                <strong style={{ color: 'var(--accent-primary)', fontSize: '1.2rem' }}>{student.gpau.toFixed(2)}</strong>
              </div>
              <div className="flex-between">
                <span className="subtitle">معدل الترم الأول</span>
                <strong>{student.gpa_sem1.toFixed(2)}</strong>
              </div>
              <div className="flex-between">
                <span className="subtitle">معدل الترم الثاني</span>
                <strong>{student.gpa_sem2.toFixed(2)}</strong>
              </div>
            </div>
          </div>
          
          {/* Radar Chart */}
          <div className="glass-panel">
            <h3 className="mb-3">تحليل الأداء (Points 0-4)</h3>
            <div style={{ height: 350 }}>
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                  <PolarGrid stroke="rgba(255,255,255,0.1)" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: 'var(--text-secondary)', fontSize: 12 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 4]} tick={{ fill: 'rgba(255,255,255,0.5)' }} />
                  <Radar name="النقاط (Points)" dataKey="points" stroke="var(--accent-primary)" fill="var(--accent-primary)" fillOpacity={0.5} />
                  <Tooltip contentStyle={{ background: 'var(--bg-color)', border: 'none', borderRadius: 8 }} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
        
        {/* Grades Table */}
        <div className="glass-panel">
          <div className="flex-between mb-3">
            <h3 style={{ margin: 0 }}>سجل الدرجات (Grades)</h3>
            <FileText size={20} color="var(--text-secondary)" />
          </div>
          
          <h4 className="mb-2 mt-4" style={{ color: 'var(--accent-primary)' }}>الترم الأول</h4>
          <div className="glass-table-container mb-4">
            <table className="glass-table">
              <thead>
                <tr>
                  <th>المقرر</th>
                  <th>الدرجة</th>
                  <th>التقدير</th>
                  <th>النقاط</th>
                </tr>
              </thead>
              <tbody>
                {sem1Grades.map((g, i) => (
                  <tr key={i}>
                    <td>
                      <div><strong>{g.course}</strong></div>
                      <div className="subtitle" style={{ fontSize: '0.8rem' }}>{g.fullCourseName}</div>
                    </td>
                    <td>{g.is_pnp ? '-' : g.score}</td>
                    <td>
                      <span className={`badge ${['A+', 'A', 'A-'].includes(g.grade) ? 'badge-success' : g.grade === 'F' ? 'badge-danger' : 'badge-primary'}`}>
                        {g.grade}
                      </span>
                    </td>
                    <td>{g.is_pnp ? '-' : g.points.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <h4 className="mb-2 mt-4" style={{ color: 'var(--accent-primary)' }}>الترم الثاني</h4>
          <div className="glass-table-container">
            <table className="glass-table">
              <thead>
                <tr>
                  <th>المقرر</th>
                  <th>الدرجة</th>
                  <th>التقدير</th>
                  <th>النقاط</th>
                </tr>
              </thead>
              <tbody>
                {sem2Grades.map((g, i) => (
                  <tr key={i}>
                    <td>
                      <div><strong>{g.course}</strong></div>
                      <div className="subtitle" style={{ fontSize: '0.8rem' }}>{g.fullCourseName}</div>
                    </td>
                    <td>{g.is_pnp ? '-' : g.score}</td>
                    <td>
                      <span className={`badge ${['A+', 'A', 'A-'].includes(g.grade) ? 'badge-success' : g.grade === 'F' ? 'badge-danger' : 'badge-primary'}`}>
                        {g.grade}
                      </span>
                    </td>
                    <td>{g.is_pnp ? '-' : g.points.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-column gap-4">
      <div className="glass-panel flex-column gap-3" style={{ maxWidth: 600, margin: '2rem auto', textAlign: 'center' }}>
        <h2>البحث عن طالب</h2>
        <p className="subtitle">الاستعلام برقم الجلوس المكون من 5 أرقام (أو الاسم)</p>
        
        <div style={{ position: 'relative' }}>
          <Search size={20} style={{ position: 'absolute', right: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
          <input 
            type="text" 
            className="input-glass" 
            placeholder="أدخل رقم الجلوس أو الاسم..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ paddingRight: '3rem' }}
          />
        </div>
      </div>
      
      {searchResults.length > 0 && (
        <div className="glass-panel" style={{ maxWidth: 800, margin: '0 auto', width: '100%' }}>
          <h3 className="mb-3">نتائج البحث ({searchResults.length})</h3>
          <div className="flex-column gap-2">
            {searchResults.map(s => (
              <div 
                key={s.seat} 
                onClick={() => navigate(`/students/${s.seat}`)}
                className="flex-between" 
                style={{ 
                  padding: '1rem', 
                  background: 'rgba(255,255,255,0.03)', 
                  borderRadius: 8, 
                  cursor: 'pointer',
                  border: '1px solid var(--card-border)'
                }}
              >
                <div>
                  <strong>{s.name}</strong>
                  <div className="subtitle">رقم الجلوس: {s.seat} | الترتيب: #{s.rank}</div>
                </div>
                <div style={{ fontWeight: 'bold', color: 'var(--accent-primary)' }}>
                  {s.gpau.toFixed(2)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
