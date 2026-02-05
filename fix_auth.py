from backend.core.database import engine
from sqlmodel import Session, select
from backend.models.models import Usuario
from backend.core.security import get_password_hash

def fix():
    with Session(engine) as session:
        u = session.exec(select(Usuario).where(Usuario.email == 'fer@3f.com')).first()
        if not u:
            u = Usuario(email='fer@3f.com', password=get_password_hash('admin123'))
            session.add(u)
        else:
            u.password = get_password_hash('admin123')
            session.add(u)
        session.commit()
        print("DONE")

if __name__ == "__main__":
    fix()
