import { useMemo, useState } from "react";
import ProjectCard from "../../components/ProjectCard/ProjectCard";
import "./Projects.css";
export default function Projects({ projects = [] }) {
  const [cat, setCat] = useState("All");
  const cats = ["All", "ML", "Deep Learning", "NLP", "Generative AI", "RAG"];
  const filtered = useMemo(
    () =>
      cat === "All"
        ? projects
        : projects.filter((p) =>
            `${p.name} ${p.description} ${p.tech_stack}`
              .toLowerCase()
              .includes(cat.toLowerCase().replace(" ", " ")),
          ),
    [projects, cat],
  );
  return (
    <section id="projects" className="page">
      <div className="center">
        <span className="pill">Selected Work</span>
        <h2 className="section-title">
          My <span>Projects</span>
        </h2>
        <p className="muted">
          Real-world AI, ML and data projects built while learning by doing.
        </p>
      </div>
      <div className="filters">
        {cats.map((c) => (
          <button
            key={c}
            className={cat === c ? "active" : ""}
            onClick={() => setCat(c)}
          >
            {c}
          </button>
        ))}
      </div>
      <div className="project-grid">
        {filtered.map((p) => (
          <ProjectCard key={p.id} project={p} />
        ))}
      </div>
      {!filtered.length && (
        <div className="empty">No projects in this category yet.</div>
      )}
    </section>
  );
}
