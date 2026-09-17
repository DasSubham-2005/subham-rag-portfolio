import { Link, useParams } from "react-router-dom";
import { ArrowLeft, ExternalLink, Play } from "lucide-react";
import { GithubIcon } from "../../components/BrandIcons/BrandIcons";
import { asset } from "../../api";
import "./ProjectDetails.css";
export default function ProjectDetails({ projects = [] }) {
  const { id } = useParams();
  const p = projects.find((x) => String(x.id) === String(id));
  if (!p)
    return (
      <section className="page">
        <div className="empty">
          Project not found.
          <br />
          <Link className="btn" to="/projects">
            Back to Projects
          </Link>
        </div>
      </section>
    );
  return (
    <section className="page detail-page">
      <Link className="back" to="/projects">
        <ArrowLeft /> Back to Projects
      </Link>
      <div className="detail-hero">
        {p.thumbnail_url ? (
          <img src={asset(p.thumbnail_url)} alt="" />
        ) : (
          <div className="detail-placeholder">AI</div>
        )}
        <div>
          <span className="pill">Project Details</span>
          <h1>{p.name}</h1>
          <p>{p.description || p.short_description}</p>
          <div className="detail-tags">
            {(p.tech_stack || "").split(",").map((t) => (
              <span key={t}>{t.trim()}</span>
            ))}
          </div>
          <div className="detail-actions">
            {p.live_url && (
              <a
                className="btn primary"
                href={p.live_url}
                target="_blank"
                rel="noreferrer"
              >
                <ExternalLink />
                Live Demo
              </a>
            )}
            {p.github_url && (
              <a
                className="btn"
                href={p.github_url}
                target="_blank"
                rel="noreferrer"
              >
                <GithubIcon />
                GitHub
              </a>
            )}
            {p.video_url && (
              <a
                className="btn"
                href={asset(p.video_url)}
                target="_blank"
                rel="noreferrer"
              >
                <Play />
                Video
              </a>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
