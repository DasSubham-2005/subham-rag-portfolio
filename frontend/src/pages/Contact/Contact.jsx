import { useState } from 'react';
import { Mail, MapPin, Send } from 'lucide-react';
import {
  GithubIcon,
  LinkedinIcon
} from '../../components/BrandIcons/BrandIcons';
import './Contact.css';

const API = (
  import.meta.env.VITE_API_URL || 'http://localhost:8000'
).replace(/\/$/, '');

export default function Contact({ profile }) {
  const [status, setStatus] = useState('');
  const [sending, setSending] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const form = e.currentTarget;

    const data = {
      name: form.name.value.trim(),
      email: form.email.value.trim(),
      subject: form.subject.value.trim(),
      message: form.message.value.trim()
    };

    setSending(true);
    setStatus('');

    try {
      const response = await fetch(`${API}/api/contact`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || 'Failed to send message');
      }

      setStatus('Message sent successfully!');

      form.reset();
    } catch (error) {
      setStatus(
        error.message || 'Something went wrong. Please try again.'
      );
    } finally {
      setSending(false);
    }
  };

  return (
    <section id="contact" className="page contact-page">
      <div>
        <span className="pill">Let's Connect</span>

        <h2 className="section-title">
          Get In <span>Touch</span>
        </h2>

        <p className="muted">
          Have a project, internship opportunity or collaboration in mind?
          Let's talk.
        </p>

        <div className="contact-info">
          <a href={`mailto:${profile?.email || ''}`}>
            <Mail />
            {profile?.email || 'Email available in Admin'}
          </a>

          <span>
            <MapPin />
            {profile?.location || 'West Bengal, India'}
          </span>

          <a
            href={profile?.github_url || '#'}
            target="_blank"
            rel="noreferrer"
          >
            <GithubIcon />
            GitHub
          </a>

          <a
            href={profile?.linkedin_url || '#'}
            target="_blank"
            rel="noreferrer"
          >
            <LinkedinIcon />
            LinkedIn
          </a>
        </div>
      </div>

      <form className="contact-form" onSubmit={handleSubmit}>
        <input
          name="name"
          placeholder="Your name"
          required
        />

        <input
          type="email"
          name="email"
          placeholder="Your email"
          required
        />

        <input
          name="subject"
          placeholder="Subject"
          required
        />

        <textarea
          name="message"
          placeholder="Your message"
          required
        />

        <button
          type="submit"
          className="btn primary"
          disabled={sending}
        >
          {sending ? 'Sending...' : 'Send Message'}
          <Send />
        </button>

        {status && (
          <p className="contact-status">
            {status}
          </p>
        )}
      </form>
    </section>
  );
}