import { useState } from "react";
import { ArrowRight, Download } from "lucide-react";
import Hero3D from "../../components/Hero3D/Hero3D";
import ProjectCard from "../../components/ProjectCard/ProjectCard";
import { asset } from "../../api";
import "./Home.css";

export default function Home({ profile, projects }) {
  const [downloading, setDownloading] = useState(false);
  const downloadResume = async () => {
    if (!profile?.resume_url || downloading) return;

    try {
      setDownloading(true);

      const response = await fetch(asset(profile.resume_url));

      if (!response.ok) {
        throw new Error("Resume download failed");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = url;
      link.download = "Subham-Das-Resume.pdf";

      document.body.appendChild(link);
      link.click();
      link.remove();

      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Resume download error:", error);
      alert("Unable to download resume.");
    } finally {
      setDownloading(false);
    }
  };

  return (
    <>
      <section id="home" className="home page">
        <div className="home-copy">
          <span className="pill">👋 Hello! I'm</span>

          <h1>{profile?.name || "Subham Das"}</h1>

          <h2>
            {profile?.title || "AI/ML Engineer | Data Scientist | Data Analyst"}
          </h2>

          <p>
            {profile?.bio ||
              "I build intelligent solutions with Machine Learning, Deep Learning, NLP and Generative AI."}
          </p>

          <div className="home-actions">
            <a
              className="btn primary"
              href="#projects"
              onClick={(e) => {
                e.preventDefault();
                document
                  .getElementById("projects")
                  ?.scrollIntoView({ behavior: "smooth" });
              }}
            >
              View Projects <ArrowRight />
            </a>

            {profile?.resume_url && (
              <button
                className="btn"
                type="button"
                onClick={downloadResume}
                disabled={downloading}
              >
                <Download />
                {downloading ? "Downloading..." : "Download Resume"}
              </button>
            )}
          </div>

          <div className="tech-row">
            <span>Python</span>
            <span>SQL</span>
            <span>Power BI</span>
            <span>ML</span>
            <span>FastAPI</span>
            <span>Docker</span>
            <span>RAG</span>
          </div>

          <div className="home-stats">
            <div>
              <b>{projects?.length || 0}+</b>
              <span>Projects</span>
            </div>

            <div>
              <b>{profile?.location ? "Kolkata" : "—"}</b>
              <span>Based in</span>
            </div>

            <div>
              <b>AI/ML</b>
              <span>Primary Focus</span>
            </div>

            <div>
              <b>2027</b>
              <span>Graduation Year</span>
            </div>
          </div>
        </div>

        <Hero3D profile={profile} />
      </section>

      <section id="featured" className="featured page">
        <div className="section-head">
          <div>
            <span className="pill">Selected Work</span>

            <h2 className="section-title">
              Featured <span>Projects</span>
            </h2>
          </div>

          <a
            className="btn"
            href="#projects"
            onClick={(e) => {
              e.preventDefault();
              document
                .getElementById("projects")
                ?.scrollIntoView({ behavior: "smooth" });
            }}
          >
            View all
          </a>
        </div>

        <div className="project-grid">
          {(projects || [])
            .filter((p) => p.featured)
            .slice(0, 3)
            .map((p) => (
              <ProjectCard key={p.id} project={p} />
            ))}
        </div>
      </section>
    </>
  );
}
