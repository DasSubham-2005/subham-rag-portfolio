import { useEffect, useState } from "react";
import { Moon, Sun, Menu, X } from "lucide-react";
import { GithubIcon, LinkedinIcon } from "../BrandIcons/BrandIcons";
// import { Link } from 'react-router-dom';
import "./Navbar.css";

const items = [
  ["Home", "home"],
  ["About", "about"],
  ["Projects", "projects"],
  ["Skills", "skills"],
  ["Experience", "experience"],
  ["Education", "education"],
  ["Certificates", "certificates"],
  ["Contact", "contact"],
];

export default function Navbar({ profile, dark, setDark }) {
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState("home");

  useEffect(() => {
    const sections = items
      .map(([, id]) => document.getElementById(id))
      .filter(Boolean);

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (visible) setActive(visible.target.id);
      },
      { rootMargin: "-25% 0px -55% 0px", threshold: [0.05, 0.2, 0.5] },
    );

    sections.forEach((section) => observer.observe(section));
    return () => observer.disconnect();
  }, []);

  const go = (id) => {
    const el = document.getElementById(id);
    if (el) {
      setActive(id);
      el.scrollIntoView({ behavior: "smooth", block: "start" });
      window.history.replaceState(null, "", `#${id}`);
    }
    setOpen(false);
  };

  return (
    <header className={`navbar ${open ? "menu-open" : ""}`}>
      <button
        className="brand"
        onClick={() => go("home")}
        aria-label="Go to Home"
      >
        <span className="brand-logo">
          <img src="/logo.png" alt="SD" />
        </span>
        Subham Das
      </button>

      <nav className="desktop-nav" aria-label="Primary navigation">
        {items.map(([name, id]) => (
          <a
            key={id}
            className={active === id ? "active" : ""}
            href={`#${id}`}
            onClick={(e) => {
              e.preventDefault();
              go(id);
            }}
          >
            {name}
          </a>
        ))}
      </nav>

      <div className="nav-actions">
        <a
          href={profile?.github_url || "https://github.com/DasSubham-2005"}
          target="_blank"
          rel="noreferrer"
          aria-label="GitHub"
        >
          <GithubIcon />
        </a>
        <a
          href={
            profile?.linkedin_url ||
            "https://linkedin.com/in/subham-das-a316422b"
          }
          target="_blank"
          rel="noreferrer"
          aria-label="LinkedIn"
        >
          <LinkedinIcon />
        </a>
        <button
          className="icon-btn"
          onClick={() => setDark(!dark)}
          aria-label="Toggle theme"
        >
          {dark ? <Sun /> : <Moon />}
        </button>
        {/* <Link className="admin-btn" to="/admin"><UserRound />Admin</Link> */}
        <button
          className="mobile-menu-btn"
          onClick={() => setOpen(!open)}
          aria-label={open ? "Close menu" : "Open menu"}
          aria-expanded={open}
        >
          {open ? <X /> : <Menu />}
        </button>
      </div>

      <nav className="mobile-nav" aria-label="Mobile navigation">
        {items.map(([name, id]) => (
          <a
            key={id}
            className={active === id ? "active" : ""}
            href={`#${id}`}
            onClick={(e) => {
              e.preventDefault();
              go(id);
            }}
          >
            <span>{name}</span>
            <i />
          </a>
        ))}
      </nav>
    </header>
  );
}
