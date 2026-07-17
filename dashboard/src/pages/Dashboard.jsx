import { useMemo } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Users, Award, TrendingUp } from 'lucide-react';
import db from '../data/db.json';

const COLORS = ['#10b981', '#ef4444', '#3b82f6', '#f59e0b', '#8b5cf6'];

export default function Dashboard() {
  const stats = useMemo(() => {
    const totalStudents = db.students.length;
    const passedStudents = db.students.filter(s => !s.failed).length;
    const passRate = ((passedStudents / totalStudents) * 100).toFixed(1);
    
    // Top 10 students
    const ranked = [...db.students].sort((a, b) => a.rank - b.rank);
    const topStudents = ranked.slice(0, 10);
    
    // Grade distribution (ignore P/NP for general distribution)
    const gradeCounts = {};
    db.grades.forEach(g => {
      if (g.is_pnp) return;
      const grade = g.grade;
      if (grade === 'F' || grade.startsWith('A') || grade.startsWith('B') || grade.startsWith('C') || grade.startsWith('D')) {
        const baseGrade = grade[0];
        gradeCounts[baseGrade] = (gradeCounts[baseGrade] || 0) + 1;
      }
    });
    const gradeData = Object.keys(gradeCounts).sort().map(k => ({
      name: k,
      value: gradeCounts[k]
    }));
    
    // Pass/Fail
    const passFailData = [
      { name: 'ناجح', value: passedStudents },
      { name: 'راسب', value: totalStudents - passedStudents }
    ];

    // Course Averages
    const courseStats = {};
    db.grades.forEach(g => {
      if (!courseStats[g.course]) {
        courseStats[g.course] = { total: 0, count: 0, passes: 0, is_pnp: g.is_pnp };
      }
      if (!g.is_pnp) {
        courseStats[g.course].total += g.score;
      }
      courseStats[g.course].count += 1;
      if (g.grade !== 'F' && g.grade !== 'NP') {
        courseStats[g.course].passes += 1;
      }
    });
    
    const courseData = Object.keys(courseStats).filter(code => !courseStats[code].is_pnp).map(code => {
      const c = courseStats[code];
      return {
        name: code,
        avg: c.total / c.count,
        passRate: (c.passes / c.count) * 100
      };
    }).sort((a, b) => b.passRate - a.passRate);
    
    const easiest = courseData.slice(0, 5);
    const hardest = [...courseData].sort((a, b) => a.passRate - b.passRate).slice(0, 5);

    return { totalStudents, passRate, topStudents, gradeData, passFailData, easiest, hardest };
  }, []);

  return (
    <div className="flex-column gap-4">
      <div className="flex-between">
        <div>
          <h1 className="text-gradient">نظرة عامة (Overview)</h1>
          <p className="subtitle">تحليل شامل لنتائج الدفعة الأولى - طب بنين الأزهر</p>
        </div>
      </div>
      
      {/* Stat Cards */}
      <div className="grid-cols-4">
        <div className="glass-panel flex-column">
          <div className="flex-between mb-2">
            <h3 style={{ margin: 0 }}>إجمالي الطلاب</h3>
            <Users color="var(--accent-primary)" />
          </div>
          <div className="stat-value">{stats.totalStudents}</div>
        </div>
        
        <div className="glass-panel flex-column">
          <div className="flex-between mb-2">
            <h3 style={{ margin: 0 }}>نسبة النجاح الكلية</h3>
            <TrendingUp color="var(--accent-success)" />
          </div>
          <div className="stat-value">{stats.passRate}%</div>
        </div>
        
        <div className="glass-panel flex-column">
          <div className="flex-between mb-2">
            <h3 style={{ margin: 0 }}>أعلى معدل (GPA)</h3>
            <Award color="var(--accent-secondary)" />
          </div>
          <div className="stat-value">{stats.topStudents[0]?.gpau.toFixed(2)}</div>
        </div>
      </div>
      
      {/* Charts */}
      <div className="grid-cols-2">
        <div className="glass-panel">
          <h3>نسبة النجاح والرسوب</h3>
          <div style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={stats.passFailData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                  label={({name, percent}) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  <Cell fill="var(--accent-success)" />
                  <Cell fill="var(--accent-danger)" />
                </Pie>
                <Tooltip contentStyle={{ background: 'var(--bg-color)', border: 'none', borderRadius: 8, color: '#fff' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="glass-panel">
          <h3>توزيع التقديرات (المواد ذات الدرجات)</h3>
          <div style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.gradeData}>
                <XAxis dataKey="name" stroke="var(--text-secondary)" />
                <YAxis stroke="var(--text-secondary)" />
                <Tooltip contentStyle={{ background: 'var(--bg-color)', border: 'none', borderRadius: 8, color: '#fff' }} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {stats.gradeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      {/* Top Students & Course Stats */}
      <div className="grid-cols-2">
        <div className="glass-panel">
          <div className="flex-between mb-3">
            <h3 style={{ margin: 0 }}>أوائل الدفعة (Top 10)</h3>
            <Award size={20} color="var(--accent-secondary)" />
          </div>
          <div className="glass-table-container">
            <table className="glass-table">
              <thead>
                <tr>
                  <th>الترتيب</th>
                  <th>الاسم</th>
                  <th>GPAU</th>
                </tr>
              </thead>
              <tbody>
                {stats.topStudents.map((s, i) => (
                  <tr key={s.seat}>
                    <td><span className="badge badge-primary">#{s.rank}</span></td>
                    <td style={{ fontSize: '0.9rem' }}>{s.name}</td>
                    <td style={{ fontWeight: 'bold', color: 'var(--accent-primary)' }}>{s.gpau.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        
        <div className="glass-panel">
          <div className="flex-between mb-3">
            <h3 style={{ margin: 0 }}>أصعب 5 مقررات (أقل نسبة نجاح)</h3>
            <TrendingUp size={20} color="var(--accent-danger)" />
          </div>
          <div style={{ height: 250, marginBottom: '2rem' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.hardest} layout="vertical">
                <XAxis type="number" domain={[0, 100]} hide />
                <YAxis dataKey="name" type="category" width={100} stroke="var(--text-secondary)" fontSize={12} />
                <Tooltip formatter={(val) => [`${val.toFixed(1)}%`, 'نسبة النجاح']} contentStyle={{ background: 'var(--bg-color)', border: 'none', borderRadius: 8 }} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
                <Bar dataKey="passRate" fill="var(--accent-danger)" radius={[0, 4, 4, 0]} barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          
          <div className="flex-between mb-3">
            <h3 style={{ margin: 0 }}>أسهل 5 مقررات (أعلى نسبة نجاح)</h3>
            <TrendingUp size={20} color="var(--accent-success)" />
          </div>
          <div style={{ height: 250 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.easiest} layout="vertical">
                <XAxis type="number" domain={[0, 100]} hide />
                <YAxis dataKey="name" type="category" width={100} stroke="var(--text-secondary)" fontSize={12} />
                <Tooltip formatter={(val) => [`${val.toFixed(1)}%`, 'نسبة النجاح']} contentStyle={{ background: 'var(--bg-color)', border: 'none', borderRadius: 8 }} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
                <Bar dataKey="passRate" fill="var(--accent-success)" radius={[0, 4, 4, 0]} barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
