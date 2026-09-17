import { Briefcase, Calendar } from "lucide-react";
import "./Experience.css";
export default function Experience({ items = [] }) {
  return (
    <section id="experience" className="page">
      <div className="center">
        <span className="pill">Journey</span>
        <h2 className="section-title">
          Work <span>Experience</span>
        </h2>
        <p className="muted">
          Internships, virtual experiences and hands-on learning.
        </p>
      </div>
      <div className="timeline">
        {items.map((x) => (
          <article className="timeline-item" key={x.id}>
            <div className="timeline-dot">
              <Briefcase />
            </div>
            <div>
              <div className="timeline-title">
                <h3>{x.role}</h3>
                <span>
                  <Calendar />
                  {x.duration}
                </span>
              </div>
              <b>{x.company}</b>
              <p>{x.description}</p>
            </div>
          </article>
        ))}
      </div>
      {!items.length && <div className="empty">No experience added yet.</div>}
    </section>
  );
}
