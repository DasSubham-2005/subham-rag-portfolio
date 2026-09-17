import { Code2, Database, BarChart3, Brain, Server, Cpu, Wrench, Sparkles } from 'lucide-react';
import './Skills.css';

const icons = {
  Programming: Code2,
  Data: Database,
  Analytics: BarChart3,
  'AI/ML': Brain,
  Backend: Server,
  DevOps: Cpu,
  Tools: Wrench,
};

const fallbackSkills = [
  { id: 'python', name: 'Python', category: 'Programming' },
  { id: 'sql', name: 'SQL', category: 'Data' },
  { id: 'ml', name: 'Machine Learning', category: 'AI/ML' },
  { id: 'tensorflow', name: 'TensorFlow', category: 'AI/ML' },
  { id: 'nlp', name: 'NLP', category: 'AI/ML' },
  { id: 'llm', name: 'LLMs', category: 'AI/ML' },
  { id: 'rag', name: 'RAG', category: 'AI/ML' },
  { id: 'powerbi', name: 'Power BI', category: 'Analytics' },
  { id: 'fastapi', name: 'FastAPI', category: 'Backend' },
  { id: 'docker', name: 'Docker', category: 'DevOps' },
  { id: 'mlflow', name: 'MLflow', category: 'Tools' },
  { id: 'git', name: 'Git & GitHub', category: 'Tools' },
];

const desktopSlots = [
  [6, 10, 20], [31, 5, 60], [61, 10, 35], [80, 28, 20],
  [64, 45, 70], [80, 63, 35], [59, 75, 50], [31, 79, 25],
  [6, 66, 55], [1, 43, 30], [20, 54, 80], [20, 24, 40],
];

const mobileSlots = [
  [4, 3], [53, 10], [4, 19], [53, 27],
  [4, 35], [53, 43], [4, 51], [53, 59],
  [4, 67], [53, 75], [4, 83], [53, 91],
];

export default function Skills({ skills = [] }) {
  const list = skills.length ? skills : fallbackSkills;
  const groups = [...new Set(list.map((s) => s.category || 'Tools'))];
  const orbitSkills = list.slice(0, 12);

  return (
    <section id="skills" className="page skills-section">
      <div className="center skills-heading">
        <span className="pill"><Sparkles size={13} /> Technical Arsenal</span>
        <h2 className="section-title">My <span>Skills</span></h2>
        <p className="muted">A living stack of technologies I use to build intelligent, data-driven products.</p>
      </div>

      <div className="skills-stage" aria-label="Floating 3D skills">
        <div className="stage-grid" />
        <div className="stage-glow" />
        <div className="stage-core"><span>AI</span><small>STACK</small></div>
        <div className="orbit-line orbit-line-a" />
        <div className="orbit-line orbit-line-b" />

        {orbitSkills.map((skill, index) => {
          const Icon = icons[skill.category] || Code2;
          const [left, top, depth] = desktopSlots[index];
          const [mLeft, mTop] = mobileSlots[index];

          return (
            <div
              className="floating-skill"
              key={skill.id || skill.name}
              style={{
                '--left': `${left}%`,
                '--top': `${top}%`,
                '--depth': `${depth}px`,
                '--m-left': `${mLeft}%`,
                '--m-top': `${mTop}%`,
                '--delay': `${index * -0.38}s`,
              }}
            >
              <div className="skill-card-3d">
                <span className="skill-icon"><Icon /></span>
                <span className="skill-name">{skill.name}</span>
                <span className="skill-shine" />
              </div>
            </div>
          );
        })}
      </div>

      <div className="skill-groups">
        {groups.map((group) => {
          const Icon = icons[group] || Code2;
          return (
            <div className="skill-group" key={group}>
              <div className="skill-group-title"><Icon /><h3>{group}</h3></div>
              <div className="skill-grid">
                {list.filter((s) => (s.category || 'Tools') === group).map((s) => (
                  <span className="skill-chip" key={s.id || s.name}>{s.name}</span>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      <div className="learning-path">
        <span>Learning Path</span><b>Machine Learning</b><i>→</i><b>Deep Learning</b><i>→</i><b>NLP</b><i>→</i><b>LLMs</b><i>→</i><b>RAG</b><i>→</i><b>Generative AI</b>
      </div>
    </section>
  );
}
