
from app import create_app
import os

app = create_app()
print(f"App static folder: {app.static_folder}")
print(f"App static URL path: {app.static_url_path}")
print(f"Root path: {app.root_path}")

# Check if file exists relative to root
file_rel = "static/uploads/profile_pics/shkachu_fixed.png"
full_path = os.path.join(app.root_path, file_rel)
print(f"Computed file path: {full_path}")
print(f"Exists? {os.path.exists(full_path)}")
