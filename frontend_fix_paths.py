import os
import glob

frontend_dir = r"c:\Users\ASUS\Documents\ASESS\frontend"

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = content.replace('"/static/', '"/')
    new_content = new_content.replace('\'/static/', '\'/')
    new_content = new_content.replace('"/users/login"', '"/login.html"')
    new_content = new_content.replace("'/users/login'", "'/login.html'")

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {filepath}")

for root, _, files in os.walk(frontend_dir):
    for file in files:
        if file.endswith('.html') or file.endswith('.js') or file.endswith('.css'):
            fix_file(os.path.join(root, file))
