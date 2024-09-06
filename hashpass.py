from werkzeug.security import generate_password_hash

# Replace 'your_secure_admin_password' with the actual password you want to hash
admin_password = 'Digi@1991'
hashed_admin_password = generate_password_hash(admin_password)

print(hashed_admin_password)
