import { Award, ExternalLink } from "lucide-react";
import { asset } from "../../api";
import "./Certificates.css";
export default function Certificates({ items = [] }) {
  return (
    <section id="certificates" className="page">
      <div className="center">
        <span className="pill">Credentials</span>
        <h2 className="section-title">
          My <span>Certificates</span>
        </h2>
        <p className="muted">Certifications and learning achievements.</p>
      </div>
      <div className="cert-grid">
        {items.map((x) => (
          <article className="cert-card" key={x.id}>
            <div className="cert-icon">
              <Award />
            </div>
            <span>{x.issue_date}</span>
            <h3>{x.name}</h3>
            <b>{x.issuer}</b>
            {(x.file_url || x.credential_url) && (
              <div className="cert-links">
                {x.file_url && (
                  <a href={asset(x.file_url)} target="_blank" rel="noreferrer">
                    View File <ExternalLink />
                  </a>
                )}
                {x.credential_url && (
                  <a href={x.credential_url} target="_blank" rel="noreferrer">
                    Credential <ExternalLink />
                  </a>
                )}
              </div>
            )}
          </article>
        ))}
      </div>
      {!items.length && <div className="empty">No certificates added yet.</div>}
    </section>
  );
}
