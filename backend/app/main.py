from pathlib import Path
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Request

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.services.email import send_contact_email
from app.core.config import settings
from app.core.auth import login, require_admin
from app.db.session import Base, engine, get_db
from app.models.entities import (
    Profile,
    Skill,
    Project,
    Experience,
    Education,
    Certificate,
    Media,
    ContactMessage,
)
from app.schemas.all import LoginIn, TokenOut, ProfileIn, SkillIn, ProjectIn, ExperienceIn, EducationIn, CertificateIn
from app.services.storage import save_upload
from app.rag.ingest import rebuild
from app.rag.service import retrieve
from app.services.llm import answer

Base.metadata.create_all(bind=engine)
ROOT = Path(__file__).resolve().parents[1]
(ROOT / settings.upload_dir).mkdir(parents=True, exist_ok=True)

app = FastAPI(title=settings.app_name, version="1.0.0")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
origins = [x.strip() for x in settings.cors_origins.split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins or ["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/uploads", StaticFiles(directory=str(ROOT / settings.upload_dir)), name="uploads")

@app.get("/health")
def health(): return {"status":"healthy","service":settings.app_name}

@app.post("/api/auth/login", response_model=TokenOut)
def auth(data: LoginIn): return {"access_token":login(data.username, data.password)}

def serialize(x): return {c.name:getattr(x,c.name) for c in x.__table__.columns}

@app.get("/api/portfolio")
def portfolio(db: Session = Depends(get_db)):
    return {"profile": serialize(db.query(Profile).first()) if db.query(Profile).first() else None,
            "skills":[serialize(x) for x in db.query(Skill).order_by(Skill.sort_order).all()],
            "projects":[serialize(x) for x in db.query(Project).order_by(Project.sort_order).all()],
            "experience":[serialize(x) for x in db.query(Experience).order_by(Experience.sort_order).all()],
            "education":[serialize(x) for x in db.query(Education).all()],
            "certificates":[serialize(x) for x in db.query(Certificate).all()]}

@app.get("/api/admin/stats")
def stats(_: str = Depends(require_admin), db: Session = Depends(get_db)):
    return {"projects":db.query(Project).count(),"skills":db.query(Skill).count(),"certificates":db.query(Certificate).count(),"experience":db.query(Experience).count(),"media":db.query(Media).count(),"messages": db.query(ContactMessage).count()}

MODEL_MAP = {"skills":Skill,"projects":Project,"experience":Experience,"education":Education,"certificates":Certificate}

def crud_create(table, data, db):
    obj=table(**data); db.add(obj); db.commit(); db.refresh(obj); return serialize(obj)

def crud_update(table, item_id, data, db):
    obj=db.get(table,item_id)
    if not obj: raise HTTPException(404,"Item not found")
    for k,v in data.items():
        if hasattr(obj,k): setattr(obj,k,v)
    db.commit(); db.refresh(obj); return serialize(obj)

def crud_delete(table,item_id,db):
    obj=db.get(table,item_id)
    if not obj: raise HTTPException(404,"Item not found")
    db.delete(obj); db.commit(); return {"ok":True}

for path, table in MODEL_MAP.items():
    def make_create(t):
        def create(data: dict, _: str=Depends(require_admin), db: Session=Depends(get_db)): return crud_create(t,data,db)
        return create
    def make_update(t):
        def update(item_id:int,data:dict, _: str=Depends(require_admin), db:Session=Depends(get_db)): return crud_update(t,item_id,data,db)
        return update
    def make_delete(t):
        def delete(item_id:int, _: str=Depends(require_admin), db:Session=Depends(get_db)): return crud_delete(t,item_id,db)
        return delete
    app.add_api_route(f"/api/admin/{path}",make_create(table),methods=["POST"])
    app.add_api_route(f"/api/admin/{path}/{{item_id}}",make_update(table),methods=["PUT"])
    app.add_api_route(f"/api/admin/{path}/{{item_id}}",make_delete(table),methods=["DELETE"])

@app.put("/api/admin/profile")
def update_profile(data: dict, _: str=Depends(require_admin), db: Session=Depends(get_db)):
    obj=db.query(Profile).first()
    if not obj: obj=Profile(); db.add(obj)
    for k,v in data.items():
        if hasattr(obj,k): setattr(obj,k,v)
    db.commit(); db.refresh(obj); return serialize(obj)

@app.post("/api/admin/upload")
async def upload(files: list[UploadFile]=File(...), _: str=Depends(require_admin), db: Session=Depends(get_db)):
    saved=[]
    for f in files:
        url=await save_upload(f)
        kind=(f.content_type or "file").split("/")[0]
        m=Media(filename=f.filename or "file",url=url,media_type=kind)
        db.add(m); saved.append(m)
    db.commit()
    return {"files":[serialize(m) for m in saved]}

@app.get("/api/admin/media")
def media(_: str=Depends(require_admin), db:Session=Depends(get_db)):
    return [serialize(x) for x in db.query(Media).order_by(Media.created_at.desc()).all()]

@app.post("/api/admin/rebuild-rag")
def rebuild_rag(_: str=Depends(require_admin), db:Session=Depends(get_db)):
    return {"chunks_indexed":rebuild(db)}

@app.post("/api/assistant")
@limiter.limit("10/minute")
async def assistant(request: Request, data: dict, db:Session=Depends(get_db)):
    q=(data.get("question") or "").strip()
    if not q: raise HTTPException(400,"Question is required")
    context=retrieve(q,5)
    return {"answer":await answer(q,context),"sources":[x["source"] for x in context]}

from app.services.email import send_contact_email


@app.post("/api/contact")
def contact_message(data: dict, db: Session = Depends(get_db)):
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    subject = (data.get("subject") or "").strip()
    message = (data.get("message") or "").strip()

    if not name:
        raise HTTPException(status_code=400, detail="Name is required")

    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    contact = ContactMessage(
        name=name,
        email=email,
        subject=subject,
        message=message,
    )

    db.add(contact)
    db.commit()
    db.refresh(contact)

    try:
        send_contact_email(
            name=name,
            email=email,
            subject=subject,
            message=message,
        )
    except Exception as e:
        print(f"Contact email failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="Message saved, but email delivery failed."
        )

    return {
        "success": True,
        "message": "Your message has been sent successfully."
    }

@app.get("/api/admin/contact-messages")
def get_contact_messages(
    _: str = Depends(require_admin),
    db: Session = Depends(get_db)
):
    messages = (
        db.query(ContactMessage)
        .order_by(ContactMessage.created_at.desc())
        .all()
    )

    return [serialize(message) for message in messages]


@app.put("/api/admin/contact-messages/{message_id}/read")
def mark_contact_message_read(
    message_id: int,
    _: str = Depends(require_admin),
    db: Session = Depends(get_db)
):
    message = db.get(ContactMessage, message_id)

    if not message:
        raise HTTPException(404, "Contact message not found")

    message.is_read = True
    db.commit()
    db.refresh(message)

    return serialize(message)


@app.delete("/api/admin/contact-messages/{message_id}")
def delete_contact_message(
    message_id: int,
    _: str = Depends(require_admin),
    db: Session = Depends(get_db)
):
    message = db.get(ContactMessage, message_id)

    if not message:
        raise HTTPException(404, "Contact message not found")

    db.delete(message)
    db.commit()

    return {"ok": True}