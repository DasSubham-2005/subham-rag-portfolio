import { Mail } from "lucide-react";
import { GithubIcon, LinkedinIcon } from "../BrandIcons/BrandIcons";
import "./Footer.css";
export default function Footer({ profile }) {
  return (
    <footer>
      <div>
        <b>Subham Das</b>
        <span>
          {profile?.title || "AI/ML Engineer | Data Scientist | Data Analyst"}
        </span>
      </div>
      <div className="footer-links">
        <a href={profile?.github_url || "#"} target="_blank" rel="noreferrer">
          <GithubIcon />
        </a>
        <a href={profile?.linkedin_url || "#"} target="_blank" rel="noreferrer">
          <LinkedinIcon />
        </a>
        <a href={`mailto:${profile?.email }`} aria-label="Email">
          <Mail />
        </a>
      </div>
      <small>
        © {new Date().getFullYear()} Subham Das. Built with AI, ML & curiosity.
      </small>
    </footer>
  );
}
