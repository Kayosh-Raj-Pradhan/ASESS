import os
import sys

target = r"c:\Users\ASUS\Documents\ASESS\frontend"
count = 0

for root, dirs, files in os.walk(target):
    for f in files:
        if f.endswith(('.html', '.js', '.css')):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                try:
                    content = file.read()
                except UnicodeDecodeError:
                    print(f"Skipping {path} due to encoding error")
                    continue
            
            new_content = content.replace('"/static/', '"/').replace("'/static/", "'/").replace('"/users/login"', '"/login.html"').replace("'/users/login'", "'/login.html'")
            
            if content != new_content:
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                count += 1
                
print(f"Fixed {count} files.")
