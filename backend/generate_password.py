from werkzeug.security import generate_password_hash

password = "admin123456"
hashed = generate_password_hash(password)

print(hashed)