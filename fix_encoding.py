import codecs

def fix_encoding(file_path):
    # Read as CP950 (Traditional Chinese)
    try:
        with open(file_path, 'r', encoding='cp950') as f:
            content = f.read()
    except UnicodeDecodeError:
        print("Failed to read as cp950, trying cp936 (Simplified)")
        with open(file_path, 'r', encoding='cp936') as f:
            content = f.read()
            
    # The content might have "charset=UTF-8" in it, which is what we want for the output.
    # We don't need to change the header if we are saving as UTF-8.
    
    # Save as UTF-8
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Converted {file_path} to UTF-8")

if __name__ == "__main__":
    fix_encoding(r"c:\Users\user\Documents\code\python\ExpressDeliverySystem\locale\zh_Hant\LC_MESSAGES\django.po")
