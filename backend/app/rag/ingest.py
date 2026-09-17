from sqlalchemy.orm import Session
from app.models.entities import Profile, Skill, Project, Experience, Education, Certificate
from app.rag.service import index_documents

def build_documents(db: Session):
    docs = []
    p = db.query(Profile).first()
    if p:
        docs.append({"id":"profile","source":"profile","text":f"Name: {p.name}. Title: {p.title}. Bio: {p.bio}. Location: {p.location}. Email: {p.email}. GitHub: {p.github_url}. LinkedIn: {p.linkedin_url}."})
    for x in db.query(Skill).all(): docs.append({"id":f"skill-{x.id}","source":"skills","text":f"Skill: {x.name}. Category: {x.category}."})
    for x in db.query(Project).all(): docs.append({"id":f"project-{x.id}","source":f"project:{x.name}","text":f"Project: {x.name}. Summary: {x.short_description}. Details: {x.description}. Tech stack: {x.tech_stack}. GitHub: {x.github_url}. Live demo: {x.live_url}."})
    for x in db.query(Experience).all(): docs.append({"id":f"experience-{x.id}","source":"experience","text":f"Role: {x.role}. Company: {x.company}. Duration: {x.duration}. Description: {x.description}."})
    for x in db.query(Education).all(): docs.append({"id":f"education-{x.id}","source":"education","text":f"Degree: {x.degree}. Institution: {x.institution}. Duration: {x.duration}. Details: {x.details}."})
    for x in db.query(Certificate).all(): docs.append({"id":f"certificate-{x.id}","source":"certificates","text":f"Certificate: {x.name}. Issuer: {x.issuer}. Issue date: {x.issue_date}. Credential: {x.credential_url}."})
    return docs

def rebuild(db: Session):
    docs = build_documents(db)
    # Re-create collection cleanly by deleting all records through IDs when available.
    from app.rag.service import collection
    existing = collection.get().get("ids", [])
    if existing: collection.delete(ids=existing)
    return index_documents(docs)
