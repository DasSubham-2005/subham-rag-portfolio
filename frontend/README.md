# Subham AI Portfolio — Frontend

Standalone React/Vite frontend for the Subham AI Portfolio. Replace your existing `frontend` folder with this folder.

## Run

```powershell
npm install
npm run dev
```

Create `.env` from `.env.example` if the API is not running at `http://localhost:8000`:

```env
VITE_API_URL=http://localhost:8000
```

## Pages
- Home + 3D/glowing hero
- About
- Projects
- Project Details
- Skills
- Experience
- Education
- Certificates
- Contact
- Admin CMS
- Ask Subham AI RAG chat

The frontend expects the FastAPI endpoints included in the project backend.

## UI behavior
- Public portfolio is a single-page experience with smooth anchor navigation.
- Navbar uses scroll-spy active states and highlights the currently visible section.
- Skills use responsive floating 3D/glowing cards with reduced-motion support.
