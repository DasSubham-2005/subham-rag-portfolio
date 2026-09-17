import { GraduationCap, Calendar } from "lucide-react";
import "./Education.css";
export default function Education({ items = [] }) {
  return (
    <section id="education" className="page">
      <div className="center">
        <span className="pill">Academic Journey</span>
        <h2 className="section-title">
          My <span>Education</span>
        </h2>
      </div>
      <div className="edu-grid">
        {items.map((x) => (
          <article className="edu-card" key={x.id}>
            <div className="edu-icon">
              <GraduationCap />
            </div>
            <div>
              <span>{x.duration}</span>
              <h3>{x.degree}</h3>
              <b>{x.institution}</b>
              <p>{x.details}</p>
            </div>
          </article>
        ))}
      </div>
      {!items.length && <div className="empty">No education entries yet.</div>}
    </section>
  );
}
