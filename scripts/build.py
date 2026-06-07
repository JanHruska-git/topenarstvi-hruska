import os
import re
import sys

def minify_css(css_content):
    # Remove block comments
    css = re.sub(r'/\*[\s\S]*?\*/', '', css_content)
    # Remove unnecessary spaces around selectors and properties
    css = re.sub(r'\s*([\{\}:;,])\s*', r'\1', css)
    # Collapse multiple spaces/newlines
    css = re.sub(r'\s+', ' ', css)
    return css.strip()

def minify_js(js_content):
    # A simple but safe JS minifier that respects quotes
    result = []
    i = 0
    length = len(js_content)
    in_string = False
    string_char = None
    in_line_comment = False
    in_block_comment = False
    
    while i < length:
        char = js_content[i]
        
        # Handle block comment end
        if in_block_comment:
            if char == '*' and i + 1 < length and js_content[i+1] == '/':
                in_block_comment = False
                i += 2
            else:
                i += 1
            continue
            
        # Handle line comment end
        if in_line_comment:
            if char == '\n' or char == '\r':
                in_line_comment = False
                # Keep the newline as it can act as a semicolon in JS
                result.append('\n')
            i += 1
            continue
            
        # Handle string literals (skip minification inside quotes)
        if in_string:
            if char == '\\' and i + 1 < length:
                result.append(js_content[i:i+2])
                i += 2
                continue
            if char == string_char:
                in_string = False
            result.append(char)
            i += 1
            continue
            
        # Check for comments start
        if char == '/' and i + 1 < length:
            next_char = js_content[i+1]
            if next_char == '/':
                in_line_comment = True
                i += 2
                continue
            elif next_char == '*':
                in_block_comment = True
                i += 2
                continue
                
        # Check for string literals start
        if char in ["'", '"', '`']:
            in_string = True
            string_char = char
            result.append(char)
            i += 1
            continue
            
        result.append(char)
        i += 1

    js = "".join(result)
    
    # Post-process whitespace (collapse multiple spaces, remove leading/trailing space around operators)
    # Collapse multiple spaces (but keep single space between words)
    js = re.sub(r'[ \t]+', ' ', js)
    # Remove space around punctuation/operators where safe
    js = re.sub(r'\s*([\{\}\(\)\[\]\+\-\*\/=\?:;,\!\|&<>])\s*', r'\1', js)
    # Clean up empty lines
    js = re.sub(r'\n+', '\n', js)
    
    return js.strip()

def optimize_images():
    img_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../assets/img'))
    if not os.path.exists(img_dir):
        print(f"Adresář s obrázky nenalezen: {img_dir}")
        return
        
    try:
        from PIL import Image
        print("Knihovna Pillow (PIL) nalezena. Zahajuji optimalizaci obrázků do formátu WebP...")
    except ImportError:
        print("\n[UPOZORNĚNÍ] Knihovna Pillow není nainstalována. Obrázky nebyly převedeny do WebP.")
        print("Pro instalaci spusťte: pip install Pillow")
        return

    for filename in os.listdir(img_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            filepath = os.path.join(img_dir, filename)
            basename, _ = os.path.splitext(filename)
            webp_path = os.path.join(img_dir, f"{basename}.webp")
            
            try:
                img = Image.open(filepath)
                # Convert to RGB if saving as WebP requires it (WebP supports RGBA too)
                img.save(webp_path, 'WEBP', quality=85)
                orig_size = os.path.getsize(filepath)
                webp_size = os.path.getsize(webp_path)
                reduction = (orig_size - webp_size) / orig_size * 100
                print(f"Optimalizováno: {filename} ({orig_size/1024:.1f} KB) -> {basename}.webp ({webp_size/1024:.1f} KB) | Úspora: {reduction:.1f}%")
            except Exception as e:
                print(f"Chyba při konverzi {filename}: {e}")

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Paths
    css_src = os.path.join(base_dir, 'assets/css/style.css')
    css_min = os.path.join(base_dir, 'assets/css/style.min.css')
    js_src = os.path.join(base_dir, 'assets/js/main.js')
    js_min = os.path.join(base_dir, 'assets/js/main.min.js')
    
    print("=== SPUŠTĚNÍ BUILD SKRIPTU ===")
    
    # Minify CSS
    if os.path.exists(css_src):
        with open(css_src, 'r', encoding='utf-8') as f:
            content = f.read()
        minified = minify_css(content)
        with open(css_min, 'w', encoding='utf-8') as f:
            f.write(minified)
        orig_size = len(content.encode('utf-8'))
        min_size = len(minified.encode('utf-8'))
        reduction = (orig_size - min_size) / orig_size * 100 if orig_size > 0 else 0
        print(f"CSS Minifikace: {orig_size/1024:.2f} KB -> {min_size/1024:.2f} KB | Úspora: {reduction:.1f}%")
    else:
        print(f"Chyba: Zdrojový CSS soubor nenalezen: {css_src}")
        
    # Minify JS
    if os.path.exists(js_src):
        with open(js_src, 'r', encoding='utf-8') as f:
            content = f.read()
        minified = minify_js(content)
        with open(js_min, 'w', encoding='utf-8') as f:
            f.write(minified)
        orig_size = len(content.encode('utf-8'))
        min_size = len(minified.encode('utf-8'))
        reduction = (orig_size - min_size) / orig_size * 100 if orig_size > 0 else 0
        print(f"JS Minifikace: {orig_size/1024:.2f} KB -> {min_size/1024:.2f} KB | Úspora: {reduction:.1f}%")
    else:
        print(f"Upozornění: Zdrojový JS soubor nenalezen (bude vytvořen v dalším kroku): {js_src}")
        
    # Optimize Images
    optimize_images()
    print("=== BUILD DOKONČEN ===")

if __name__ == '__main__':
    main()
