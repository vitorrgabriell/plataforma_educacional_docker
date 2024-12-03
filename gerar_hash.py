import bcrypt

senha = "admin123"

senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

print(f"Hash gerado: {senha_hash.decode('utf-8')}")
