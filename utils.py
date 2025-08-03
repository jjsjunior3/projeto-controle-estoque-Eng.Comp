from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
        return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

if __name__ == '__main__':
        senha_original = "minhasenha123"
        senha_hashed = hash_password(senha_original)
        print(f"Senha Original: {senha_original}")
        print(f"Senha Hashed: {senha_hashed}")

        print(f"Verificando 'minhasenha123': {verify_password('minhasenha123', senha_hashed)}")
        print(f"Verificando 'senhaerrada': {verify_password('senhaerada', senha_hashed)}")
