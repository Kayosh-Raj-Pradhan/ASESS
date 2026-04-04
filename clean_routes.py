import os
import re

frontend_dir = r"c:\Users\ASUS\Documents\ASESS\frontend"

# Main landing pages that should be extension-less
PAGES = [
    "index", "login", "register", "history", "capture", "insights", 
    "test", "patients", "report", "eye-test-report", "about", "resources", "dashboard"
]

def fix_content(content):
    # Match href="/page.html" or href="/page.html?..."
    for page in PAGES:
        # href="/page.html" -> href="/page"
        content = re.sub(rf'href\s*=\s*(["\'])/{page}\.html\1', rf'href="/{page}"', content)
        # href="/page.html?..." -> href="/page?..."
        content = re.sub(rf'href\s*=\s*(["\'])/{page}\.html\?', rf'href="/{page}?', content)
        
        # window.location.href = "/page.html" -> window.location.href = "/page"
        content = re.sub(rf'location\.href\s*=\s*(["\'])/{page}\.html\1', rf'location.href = "/{page}"', content)
        # window.location.href = "/page.html?..." -> window.location.href = "/page?..."
        content = re.sub(rf'location\.href\s*=\s*(["\'])/{page}\.html\?', rf'location.href = "/{page}?', content)
        
    return content

for root, _, files in os.walk(frontend_dir):
    for f in files:
        if f.endswith(('.html', '.js')):
            if f == "server.py": continue
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            new_content = fix_content(content)
            
            if content != new_content:
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f"Cleaned {path}")
