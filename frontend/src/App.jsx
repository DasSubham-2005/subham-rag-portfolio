import { useEffect, useState } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar/Navbar';
import Footer from './components/Footer/Footer';
import AskSubhamAI from './components/AskSubhamAI/AskSubhamAI';
import Home from './pages/Home/Home';
import About from './pages/About/About';
import Projects from './pages/Projects/Projects';
import ProjectDetails from './pages/ProjectDetails/ProjectDetails';
import Skills from './pages/Skills/Skills';
import Experience from './pages/Experience/Experience';
import Education from './pages/Education/Education';
import Certificates from './pages/Certificates/Certificates';
import Contact from './pages/Contact/Contact';
import Admin from './pages/Admin/Admin';
import { api } from './api';

function PortfolioPage({ data }) {
  return (
    <>
      <Home profile={data.profile} projects={data.projects} />
      <About profile={data.profile} />
      <Projects projects={data.projects} />
      <Skills skills={data.skills} />
      <Experience items={data.experience} />
      <Education items={data.education} />
      <Certificates items={data.certificates} />
      <Contact profile={data.profile} />
    </>
  );
}

function AppContent() {
  const location = useLocation();
  const [data, setData] = useState({ profile: null, skills: [], projects: [], experience: [], education: [], certificates: [] });
  const [dark, setDark] = useState(true);
  const load = () => api('/api/portfolio').then(setData).catch(console.error);

  useEffect(() => { load(); }, []);
  useEffect(() => { document.documentElement.dataset.theme = dark ? 'dark' : 'light'; }, [dark]);

  const isAdmin = location.pathname.startsWith('/admin');
  const isProjectDetails = location.pathname.startsWith('/projects/');

  if (isAdmin) return <Routes><Route path="/admin/*" element={<Admin onChanged={load} />} /></Routes>;

  return (
    <>
      <Navbar profile={data.profile} dark={dark} setDark={setDark} />
      <main>
        <Routes>
          <Route path="/projects/:id" element={<ProjectDetails projects={data.projects} />} />
          <Route path="*" element={<PortfolioPage data={data} />} />
        </Routes>
      </main>
      <Footer profile={data.profile} />
      <AskSubhamAI />
    </>
  );
}

export default function App() {
  return <AppContent />;
}
