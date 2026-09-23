from sqlalchemy.orm import Session

from app.models.entities import (
    Profile,
    Skill,
    Project,
    Experience,
    Education,
    Certificate,
    CustomKnowledge,
)

from app.rag.service import index_documents


def build_documents(db: Session):
    docs = []

    p = db.query(Profile).first()

    if p:
        docs.append({
            "id": "profile",
            "source": "profile",
            "text": (
                f"Name: {p.name}. "
                f"Title: {p.title}. "
                f"Bio: {p.bio}. "
                f"Location: {p.location}. "
                f"Email: {p.email}. "
                f"GitHub: {p.github_url}. "
                f"LinkedIn: {p.linkedin_url}."
            ),
        })

    for x in db.query(Skill).all():
        docs.append({
            "id": f"skill-{x.id}",
            "source": "skills",
            "text": f"Skill: {x.name}. Category: {x.category}.",
        })

    for x in db.query(Project).all():
        docs.append({
            "id": f"project-{x.id}",
            "source": f"project:{x.name}",
            "text": (
                f"Project: {x.name}. "
                f"Summary: {x.short_description}. "
                f"Details: {x.description}. "
                f"Tech stack: {x.tech_stack}. "
                f"GitHub: {x.github_url}. "
                f"Live demo: {x.live_url}."
            ),
        })

    for x in db.query(Experience).all():
        docs.append({
            "id": f"experience-{x.id}",
            "source": "experience",
            "text": (
                f"Role: {x.role}. "
                f"Company: {x.company}. "
                f"Duration: {x.duration}. "
                f"Description: {x.description}."
            ),
        })

    for x in db.query(Education).all():
        docs.append({
            "id": f"education-{x.id}",
            "source": "education",
            "text": (
                f"Degree: {x.degree}. "
                f"Institution: {x.institution}. "
                f"Duration: {x.duration}. "
                f"Details: {x.details}."
            ),
        })

    for x in db.query(Certificate).all():
       docs.append({
           "id": f"certificate-{x.id}",
           "source": "certificates",
           "text": (
              f"Certification: {x.name}. "
              f"Issuing organization: {x.issuer}. "
              f"Issue date: {x.issue_date}. "
              f"Credential URL: {x.credential_url}. "
              f"Certificate file: {x.file_url}."
            ),
        })

    for x in db.query(CustomKnowledge).all():
        docs.append({
            "id": f"custom-knowledge-{x.id}",
            "source": f"custom:{x.title}",
           "text": (
              f"Knowledge title: {x.title}. "
              f"Knowledge content: {x.content}."
            ),
         })

    return docs


def rebuild(db: Session):
    docs = build_documents(db)

    from app.rag.service import get_collection

    collection = get_collection()

    existing = collection.get().get("ids", [])

    if existing:
        collection.delete(ids=existing)

    return index_documents(docs)