from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
hashed = pwd_context.hash("123ABC")
print(hashed)
print(pwd_context.verify("123ABC", hashed))
