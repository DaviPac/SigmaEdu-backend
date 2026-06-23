from sqlalchemy.orm import Session
from models import User
import bcrypt

class UserService():
    db: Session
    def __init__(self, db: Session):
        self.db = db
    
    def register(self, username: str, password: str):
        existing_user = self.db.query(User).filter(User.username == username).first()
        if existing_user:
            raise Exception("Usuario ja existente")
        new_user = User()
        new_user.name = username
        new_user.password_hash = bcrypt.hashpw(password, bcrypt.gensalt())
        self.db.add(new_user)

    def login(self, username: str, password: str) -> bool:
        existing_user = self.db.query(User).filter(User.username == username).first()
        if existing_user is None:
            raise Exception("Usuario inexistente")
        if not bcrypt.checkpw(password, existing_user.password_hash):
            raise Exception("Senha incorreta")
        return True