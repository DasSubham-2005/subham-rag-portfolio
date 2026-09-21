import { useEffect, useState } from "react";
import { Routes, Route, Link, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  UserRound,
  Code2,
  FolderKanban,
  Briefcase,
  GraduationCap,
  Award,
  Image,
  Brain,
  LogOut,
  Plus,
  Trash2,
  Save,
  Upload,
  RefreshCw,
  ExternalLink,
  Menu,
  ShieldCheck,
  MessageSquare,
} from "lucide-react";
import { api, asset } from "../../api";
import "./Admin.css";
const TOKEN_KEY = "subham_admin_token";
const empty = {
  skills: { name: "", category: "Tools", icon_url: "", sort_order: 0 },
  projects: {
    name: "",
    short_description: "",
    description: "",
    tech_stack: "",
    github_url: "",
    live_url: "",
    thumbnail_url: "",
    video_url: "",
    featured: false,
    sort_order: 0,
  },
  experience: {
    role: "",
    company: "",
    duration: "",
    description: "",
    sort_order: 0,
  },
  education: { degree: "", institution: "", duration: "", details: "" },
  certificates: {
    name: "",
    issuer: "",
    issue_date: "",
    credential_url: "",
    file_url: "",
  },
};
const labels = {
  skills: "Skills",
  projects: "Projects",
  experience: "Experience",
  education: "Education",
  certificates: "Certificates",
  contacts: "Contact Messages",
};
function Login({ onLogin }) {
  const [u, setU] = useState("");
  const [p, setP] = useState("");
  const [err, setErr] = useState("");
  const submit = async (e) => {
    e.preventDefault();
    try {
      const r = await api("/api/auth/login", {
        method: "POST",
        body: { username: u, password: p },
      });
      sessionStorage.setItem(TOKEN_KEY, r.access_token);
      onLogin(r.access_token);
    } catch (e) {
      setErr(e.message);
    }
  };
  return (
    <div className="admin-login">
      <form className="login-box" onSubmit={submit}>
        <ShieldCheck />
        <h1>
          Admin <span>Control</span>
        </h1>
        <p>
          Manage your portfolio content, media and RAG knowledge without editing
          code.
        </p>
        <input
          value={u}
          onChange={(e) => setU(e.target.value)}
          placeholder="Admin username"
        />
        <input
          value={p}
          onChange={(e) => setP(e.target.value)}
          type="password"
          placeholder="Password"
        />
        <button className="btn primary">
          <ShieldCheck /> Sign in
        </button>
        {err && <small>{err}</small>}
      </form>
    </div>
  );
}
function Layout({ section, setSection, onLogout }) {
  const items = [
    ["dashboard", "Dashboard", LayoutDashboard],
    ["profile", "Profile", UserRound],
    ["projects", "Projects", FolderKanban],
    ["skills", "Skills", Code2],
    ["experience", "Experience", Briefcase],
    ["education", "Education", GraduationCap],
    ["certificates", "Certificates", Award],
    ["contacts", "Messages", MessageSquare],
    ["media", "Media Library", Image],
    ["rag", "AI Knowledge", Brain],
  ];
  return (
    <div className="admin-shell">
      <aside>
        <div className="admin-brand">
          <ShieldCheck /> Subham CMS
        </div>
        {items.map(([id, n, I]) => (
          <button
            key={id}
            className={section === id ? "active" : ""}
            onClick={() => setSection(id)}
          >
            <I />
            {n}
          </button>
        ))}
        <button className="logout" onClick={onLogout}>
          <LogOut />
          Logout
        </button>
      </aside>
      <div className="admin-main">
        <header>
          <div>
            <span>Admin Panel</span>
            <h1>{labels[section] || section}</h1>
          </div>
          <Link to="/" className="btn">
            <ExternalLink /> View Site
          </Link>
        </header>
        <AdminSection section={section} />
      </div>
    </div>
  );
}
function AdminSection({ section }) {
  const token = sessionStorage.getItem(TOKEN_KEY);
  const [data, setData] = useState(null);
  const [stats, setStats] = useState(null);
  const [message, setMessage] = useState("");
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({});

  const [contactMessages, setContactMessages] = useState([]);

  const load = () =>
    api("/api/portfolio")
      .then(setData)
      .catch((e) => setMessage(e.message));

  const loadContactMessages = () =>
    api("/api/admin/contact-messages", { token })
      .then(setContactMessages)
      .catch((e) => setMessage(e.message));

  useEffect(() => {
    load();

    if (section === "contacts") loadContactMessages();

    if (section === "dashboard")
      api("/api/admin/stats", { token })
        .then((result) => {
          console.log("ADMIN STATS:", result);
          setStats(result);
        })
        .catch((e) => {
          console.error("ADMIN STATS ERROR:", e);
          setMessage(e.message);
        });
  }, [section]);

  const save = async () => {
    try {
      if (section === "profile")
        await api("/api/admin/profile", { method: "PUT", token, body: form });
      else if (editing?.id)
        await api(`/api/admin/${section}/${editing.id}`, {
          method: "PUT",
          token,
          body: form,
        });
      else
        await api(`/api/admin/${section}`, {
          method: "POST",
          token,
          body: form,
        });
      setMessage("Saved successfully");
      setEditing(null);
      setForm({});
      load();
    } catch (e) {
      setMessage(e.message);
    }
  };
  const remove = async (id) => {
    if (!confirm("Delete this item?")) return;
    try {
      await api(`/api/admin/${section}/${id}`, { method: "DELETE", token });
      setMessage("Deleted");
      load();
    } catch (e) {
      setMessage(e.message);
    }
  };
  const upload = async (files) => {
    const fd = new FormData();
    [...files].forEach((f) => fd.append("files", f));
    const r = await api("/api/admin/upload", {
      method: "POST",
      token,
      body: fd,
    });
    return r.files;
  };
  if (section === "dashboard") return <Dashboard stats={stats} />;
  if (section === "profile")
    return (
      <ProfileEditor
        value={data?.profile}
        token={token}
        onSave={async (v) => {
          await api("/api/admin/profile", { method: "PUT", token, body: v });
          setMessage("Profile saved");
          load();
        }}
        upload={upload}
        message={message}
      />
    );

  if (section === "contacts")
    return (
      <ContactMessages
        messages={contactMessages}
        token={token}
        reload={loadContactMessages}
      />
    );
  if (section === "media")
    return <MediaManager token={token} upload={upload} />;
  if (section === "rag") return <RagManager token={token} />;
  const items = data?.[section] || [];
  return (
    <div className="manager">
      <div className="manager-top">
        <p>
          Manage {labels[section].toLowerCase()} directly from the dashboard.
        </p>
        <button
          className="btn primary"
          onClick={() => {
            setEditing({});
            setForm({ ...empty[section] });
          }}
        >
          <Plus /> Add New
        </button>
      </div>
      {message && <div className="admin-message">{message}</div>}
      {editing && (
        <Editor
          section={section}
          form={form}
          setForm={setForm}
          save={save}
          cancel={() => setEditing(null)}
          upload={upload}
        />
      )}
      <div className="admin-list">
        {items.map((x) => (
          <div className="admin-item" key={x.id}>
            <div>
              <b>{x.name || x.role || x.degree}</b>
              <span>
                {x.short_description ||
                  x.issuer ||
                  x.company ||
                  x.institution ||
                  x.category}
              </span>
            </div>
            <div className="row-actions">
              <button
                onClick={() => {
                  setEditing(x);
                  setForm({ ...x });
                }}
              >
                <Save />
              </button>
              <button className="danger" onClick={() => remove(x.id)}>
                <Trash2 />
              </button>
            </div>
          </div>
        ))}
        {!items.length && <div className="empty">Nothing added yet.</div>}
      </div>
    </div>
  );
}
function Dashboard({ stats }) {
  return (
    <div className="dash">
      <p>Welcome back. Your portfolio is controlled from here.</p>
      <div className="stat-grid">
        {[
          ["Projects", stats?.projects],
          ["Skills", stats?.skills],
          ["Certificates", stats?.certificates],
          ["Experience", stats?.experience],
          ["Media", stats?.media],
          ["Messages", stats?.messages],
        ].map(([a, b]) => (
          <div key={a}>
            <span>{a}</span>
            <b>{b ?? "—"}</b>
          </div>
        ))}
      </div>
      <div className="admin-info">
        <h3>CMS + RAG workflow</h3>
        <p>
          Update profile, projects, certificates or media here. Then rebuild the
          RAG knowledge base from the AI Knowledge tab so Ask Subham AI uses the
          latest information.
        </p>
      </div>
    </div>
  );
}
function ProfileEditor({ value, token, onSave, upload, message }) {
  const [f, setF] = useState(value || {});
  useEffect(() => setF(value || {}), [value]);
  const up = async (e, key) => {
    try {
      const r = await upload(e.target.files);
      if (r[0]) setF((x) => ({ ...x, [key]: r[0].url }));
    } catch (err) {
      alert(err.message);
    }
  };
  const field = (k, label, type = "text") => (
    <label>
      {label}
      <input
        type={type}
        value={f[k] || ""}
        onChange={(e) => setF({ ...f, [k]: e.target.value })}
      />
    </label>
  );
  return (
    <div className="profile-editor">
      <div className="form-grid">
        {field("name", "Name")}
        {field("title", "Professional Title")}
        {field("email", "Email", "email")}
        {field("location", "Location")}
        {field("github_url", "GitHub URL")}
        {field("linkedin_url", "LinkedIn URL")}
      </div>
      <label>
        Bio
        <textarea
          value={f.bio || ""}
          onChange={(e) => setF({ ...f, bio: e.target.value })}
        />
      </label>
      <div className="upload-row">
        <label>
          Profile Photo
          <input
            type="file"
            accept="image/*"
            onChange={(e) => up(e, "photo_url")}
          />
        </label>
        <label>
          Resume PDF
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => up(e, "resume_url")}
          />
        </label>
      </div>
      <div className="url-preview">
        Photo: {f.photo_url || "Not uploaded"}
        <br />
        Resume: {f.resume_url || "Not uploaded"}
      </div>
      <button className="btn primary" onClick={() => onSave(f)}>
        <Save /> Save Profile
      </button>
      {message && <div className="admin-message">{message}</div>}
    </div>
  );
}
function Editor({ section, form, setForm, save, cancel, upload }) {
  const common = (k, label, type = "text") => (
    <label>
      {label}
      <input
        type={type}
        value={form[k] ?? ""}
        onChange={(e) =>
          setForm({
            ...form,
            [k]: type === "checkbox" ? e.target.checked : e.target.value,
          })
        }
      />
    </label>
  );
  return (
    <div className="editor-box">
      <div className="editor-head">
        <h3>
          {form.id ? "Edit" : "Add"} {labels[section]}
        </h3>
        <button onClick={cancel}>×</button>
      </div>
      {section === "skills" && (
        <div className="form-grid">
          {common("name", "Skill Name")}
          {common("category", "Category")}
          {common("icon_url", "Icon URL")}
          {common("sort_order", "Order", "number")}
        </div>
      )}
      {section === "projects" && (
        <>
          <div className="form-grid">
            {common("name", "Project Name")}
            {common("short_description", "Short Description")}
            {common("tech_stack", "Tech Stack")}
            {common("github_url", "GitHub URL")}
            {common("live_url", "Live Demo URL")}
            {common("sort_order", "Order", "number")}
          </div>
          {common("description", "Full Description")}
          <div className="upload-row">
            <label>
              Thumbnail Image
              <input
                type="file"
                accept="image/*"
                onChange={async (e) => {
                  const r = await upload(e.target.files);
                  if (r[0]) setForm((x) => ({ ...x, thumbnail_url: r[0].url }));
                }}
              />
            </label>
            <label>
              Project Video
              <input
                type="file"
                accept="video/*"
                onChange={async (e) => {
                  const r = await upload(e.target.files);
                  if (r[0]) setForm((x) => ({ ...x, video_url: r[0].url }));
                }}
              />
            </label>
          </div>
          <label className="check">
            <input
              type="checkbox"
              checked={!!form.featured}
              onChange={(e) => setForm({ ...form, featured: e.target.checked })}
            />{" "}
            Featured project
          </label>
        </>
      )}
      {section === "experience" && (
        <>
          <div className="form-grid">
            {common("role", "Role")}
            {common("company", "Company")}
            {common("duration", "Duration")}
            {common("sort_order", "Order", "number")}
          </div>
          {common("description", "Description")}
        </>
      )}
      {section === "education" && (
        <>
          <div className="form-grid">
            {common("degree", "Degree")}
            {common("institution", "Institution")}
            {common("duration", "Duration")}
          </div>
          {common("details", "Details")}
        </>
      )}
      {section === "certificates" && (
        <>
          <div className="form-grid">
            {common("name", "Certificate Name")}
            {common("issuer", "Issuer")}
            {common("issue_date", "Issue Date")}
            {common("credential_url", "Credential URL")}
          </div>
          <label>
            Certificate PDF/Image
            <input
              type="file"
              accept="image/*,.pdf"
              onChange={async (e) => {
                const r = await upload(e.target.files);
                if (r[0]) setForm((x) => ({ ...x, file_url: r[0].url }));
              }}
            />
          </label>
          {common("file_url", "Uploaded File URL")}
        </>
      )}
      <div className="editor-actions">
        <button className="btn primary" onClick={save}>
          <Save /> Save
        </button>
        <button className="btn" onClick={cancel}>
          Cancel
        </button>
      </div>
    </div>
  );
}

function ContactMessages({ messages, token, reload }) {
  const markRead = async (id) => {
    try {
      await api(`/api/admin/contact-messages/${id}/read`, {
        method: "PUT",
        token,
      });
      reload();
    } catch (e) {
      alert(e.message);
    }
  };

  const removeMessage = async (id) => {
    if (!window.confirm("Delete this message?")) return;

    try {
      await api(`/api/admin/contact-messages/${id}`, {
        method: "DELETE",
        token,
      });
      reload();
    } catch (e) {
      alert(e.message);
    }
  };

  return (
    <div className="admin-section">
      <div className="section-head">
        <div>
          <h2>Contact Messages</h2>
          <p>Messages received from your portfolio website.</p>
        </div>

        <button className="btn secondary" onClick={reload}>
          Refresh
        </button>
      </div>

      {!messages.length ? (
        <div className="empty-state">
          <MessageSquare size={32} />
          <p>No contact messages yet.</p>
        </div>
      ) : (
        <div className="contact-messages">
          {messages.map((item) => (
            <div
              className={`contact-message-card ${
                item.is_read ? "read" : "unread"
              }`}
              key={item.id}
            >
              <div className="contact-message-top">
                <div>
                  <h3>{item.subject || "No Subject"}</h3>
                  <strong>{item.name}</strong>
                  <a href={`mailto:${item.email}`}>{item.email}</a>
                </div>

                <span>
                  {item.created_at
                    ? new Date(item.created_at).toLocaleString()
                    : ""}
                </span>
              </div>

              <div className="contact-message-body">{item.message}</div>

              <div className="contact-message-actions">
                {!item.is_read && (
                  <button
                    className="btn secondary"
                    onClick={() => markRead(item.id)}
                  >
                    Mark as Read
                  </button>
                )}

                <button
                  className="btn danger"
                  onClick={() => removeMessage(item.id)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function MediaManager({ token, upload }) {
  const [items, setItems] = useState([]);

  const load = () => {
    api("/api/admin/media", { token })
      .then(setItems)
      .catch((e) => console.error("MEDIA LOAD ERROR:", e));
  };

  useEffect(() => {
    load();
  }, []);
  const add = async (e) => {
    if (e.target.files?.length) {
      await upload(e.target.files);
      load();
    }
  };
  return (
    <div className="media-manager">
      <label className="upload-big">
        <Upload />
        <b>Upload images, videos or PDFs</b>
        <span>Select multiple files at once</span>
        <input
          type="file"
          multiple
          accept="image/*,video/*,.pdf"
          onChange={add}
        />
      </label>
      <div className="media-grid">
        {items.map((x) => (
          <article key={x.id}>
            <span>{x.media_type}</span>
            {x.media_type === "image" && <img src={asset(x.url)} alt="" />}
            <b>{x.filename}</b>
            <a href={asset(x.url)} target="_blank" rel="noreferrer">
              Open file <ExternalLink />
            </a>
          </article>
        ))}
      </div>
    </div>
  );
}
function RagManager({ token }) {
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState("");
  const rebuild = async () => {
    setBusy(true);
    try {
      const r = await api("/api/admin/rebuild-rag", { method: "POST", token });
      setResult(
        `Knowledge base rebuilt. ${r.chunks_indexed || 0} chunks indexed.`,
      );
    } catch (e) {
      setResult(e.message);
    } finally {
      setBusy(false);
    }
  };
  return (
    <div className="rag-manager">
      <div className="rag-hero">
        <Brain />
        <h2>Portfolio RAG Knowledge Base</h2>
        <p>
          The assistant retrieves your portfolio information from the vector
          database before generating an answer.
        </p>
        <button className="btn primary" onClick={rebuild} disabled={busy}>
          {busy ? (
            <>
              <RefreshCw className="spin" /> Rebuilding…
            </>
          ) : (
            <>
              <RefreshCw /> Rebuild Knowledge Base
            </>
          )}
        </button>
        {result && <div className="admin-message">{result}</div>}
      </div>
      <div className="rag-pipeline">
        <span>Portfolio DB</span>
        <i>→</i>
        <span>Document chunks</span>
        <i>→</i>
        <span>Embeddings</span>
        <i>→</i>
        <span>ChromaDB</span>
        <i>→</i>
        <span>Retriever</span>
        <i>→</i>
        <span>LLM</span>
      </div>
    </div>
  );
}
export default function Admin() {
  const [token, setToken] = useState(sessionStorage.getItem(TOKEN_KEY));
  const [section, setSection] = useState("dashboard");
  const logout = () => {
    sessionStorage.removeItem(TOKEN_KEY);
    setToken(null);
  };
  if (!token) return <Login onLogin={setToken} />;
  return <Layout section={section} setSection={setSection} onLogout={logout} />;
}
