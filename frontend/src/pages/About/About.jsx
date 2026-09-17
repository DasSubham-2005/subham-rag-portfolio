
import {
  Brain,
  MessageSquare,
  BarChart3,
  Code2,
  Lightbulb,
  Infinity,
  MapPin,
  Mail,
  GraduationCap,
  Sparkles,
  ArrowUpRight,
} from "lucide-react";

import { asset } from "../../api";
import "./About.css";

export default function About({ profile }) {
  const cards = [
    {
      icon: Brain,
      title: "Machine Learning",
      subtitle: "& Deep Learning",
    },
    {
      icon: MessageSquare,
      title: "NLP & LLMs",
      subtitle: "Exploring",
    },
    {
      icon: BarChart3,
      title: "Data Analysis",
      subtitle: "& Visualization",
    },
    {
      icon: Code2,
      title: "Full Stack",
      subtitle: "Secondary",
    },
    {
      icon: Lightbulb,
      title: "Problem Solving",
      subtitle: "& DSA",
    },
    {
      icon: Infinity,
      title: "Continuous Learning",
      subtitle: "Always",
    },
  ];

  return (
    <section id="about" className="page about">
      {/* LEFT CONTENT */}
      <div className="about-content">
        <span className="pill">
          <Sparkles size={14} />
          About Me
        </span>

        <h2 className="section-title">
          Turning Curiosity Into <span>Intelligent Solutions</span>
        </h2>

        <p className="lead">
          A curious mind, a problem solver, and a lifelong learner focused on
          building meaningful technology.
        </p>

        <p className="muted">
          {profile?.bio ||
            "I am a Computer Science Engineering student focused on Machine Learning, Data Science and AI/ML. I enjoy building real-world projects, exploring emerging technologies, and continuously improving my skills through hands-on development."}
        </p>

        <div className="about-cards">
          {cards.map(({ icon: Icon, title, subtitle }) => (
            <div className="about-card" key={title}>
              <div className="about-card-icon">
                <Icon />
              </div>

              <span>
                {title}
                <small>{subtitle}</small>
              </span>

              <ArrowUpRight className="about-card-arrow" size={16} />
            </div>
          ))}
        </div>
      </div>

      {/* PROFILE CARD */}
      <div className="glow-profile">
        <div className="profile-glow" />

        <div className="profile-image-wrap">
          {profile?.photo_url ? (
            <img
              src={asset(profile.photo_url)}
              alt={profile?.name || "Subham Das"}
            />
          ) : (
            <div className="profile-avatar">SD</div>
          )}
        </div>

        <div className="profile-status">
          <span />
          Open to opportunities
        </div>

        <h3>{profile?.name || "Subham Das"}</h3>

        <b>
          {profile?.title ||
            "AI/ML Engineer | Data Scientist | Data Analyst"}
        </b>

        <div className="profile-info">
          <span>
            <MapPin />
            {profile?.location || "India"}
          </span>

          <span>
            <Mail />
            {profile?.email || "Email available in Contact"}
          </span>

          <span>
            <GraduationCap />
            B.Tech in Computer Science Engineering
          </span>
        </div>

        <div className="focus-card">
          <div>
            <span>Primary Focus</span>
            <strong>Machine Learning / AI</strong>
          </div>

          <div>
            <span>Secondary</span>
            <strong>Full Stack Development</strong>
          </div>
        </div>
      </div>
    </section>
  );
}