from app.db.session import Base, engine, SessionLocal
from app.models.entities import Profile, Skill, Project, Experience, Education, Certificate
Base.metadata.create_all(bind=engine)
db=SessionLocal()
if not db.query(Profile).first():
    db.add(Profile(name='Subham Das',title='AI/ML Engineer | Data Scientist | Data Analyst',bio='B.Tech CSE student focused on Machine Learning, Data Science and AI/ML. I build real-world projects and continuously explore Deep Learning, NLP, LLMs, RAG and Generative AI.'))
if db.query(Skill).count()==0:
    for i,(n,c) in enumerate([('Python','Programming'),('SQL','Data'),('Power BI','Analytics'),('Machine Learning','AI/ML'),('Deep Learning','AI/ML'),('NLP','AI/ML'),('FastAPI','Backend'),('Docker','DevOps'),('MLflow','MLOps'),('Streamlit','Apps'),('Git/GitHub','Tools')]): db.add(Skill(name=n,category=c,sort_order=i))
if db.query(Project).count()==0:
    projects=[('FraudShield AI','ML-based fraud detection system','Machine learning project for detecting fraudulent transactions and surfacing risk insights.','Python, scikit-learn, Streamlit'),('DemandSense AI','LSTM demand forecasting','Deep learning project for time-series demand forecasting.','Python, TensorFlow, LSTM'),('ResumeIQ','NLP resume analyzer','NLP-based resume understanding and job matching assistant.','Python, NLP, TF-IDF'),('DevTutor-Lite','Fine-tuned coding assistant','A focused LLM fine-tuning/LoRA learning project.','Python, LoRA, Transformers'),('MultiGenAI','Multidomain AI assistant','General-purpose GenAI assistant built with an LLM API and Streamlit.','Python, Groq, Streamlit'),('KnowledgeVault AI','RAG knowledge assistant','Retrieval-Augmented Generation system over a private knowledge base.','Python, RAG, ChromaDB')]
    for i,x in enumerate(projects): db.add(Project(name=x[0],short_description=x[1],description=x[2],tech_stack=x[3],sort_order=i,featured=i<3))
if db.query(Education).count()==0: db.add(Education(degree='B.Tech in Computer Science Engineering',institution='Add your college name from Admin Panel',duration='2023 – 2027',details='Update education details from Admin Panel.'))
if db.query(Experience).count()==0: db.add(Experience(role='Data Analytics Virtual Experience',company='Forage / Geldium',duration='Update dates from Admin Panel',description='Performed EDA and analyzed customer delinquency-risk data.'))
db.commit(); db.close(); print('Seed complete')
