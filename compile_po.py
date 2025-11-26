import os
import struct
import sys

def generate_mo_file(po_file_path, mo_file_path):
    messages = {}
    
    try:
        with open(po_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        print("UTF-8 decode failed, trying cp950")
        with open(po_file_path, 'r', encoding='cp950') as f:
            lines = f.readlines()

    current_msgid = None
    current_msgstr = None
    in_msgid = False
    in_msgstr = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):
            continue
            
        if line.startswith('msgid "'):
            if current_msgid is not None and current_msgstr is not None:
                messages[current_msgid] = current_msgstr
            current_msgid = line[7:-1]
            current_msgstr = ""
            in_msgid = True
            in_msgstr = False
        elif line.startswith('msgstr "'):
            current_msgstr = line[8:-1]
            in_msgid = False
            in_msgstr = True
        elif line.startswith('"'):
            content = line[1:-1]
            if in_msgid:
                current_msgid += content
            elif in_msgstr:
                current_msgstr += content

    # Add the last one
    if current_msgid is not None and current_msgstr is not None:
        messages[current_msgid] = current_msgstr

    # Remove empty msgid (header) if we don't want to process it specially, 
    # but usually the header is stored with empty string key.
    # We'll keep it as is.

    # Sort messages
    sorted_messages = sorted(messages.items())
    count = len(sorted_messages)
    
    # MO file format
    # magic number: 0x950412de
    # version: 0
    # number of strings
    # offset of original string table
    # offset of translation string table
    # size of hashing table (0)
    # offset of hashing table (0)
    
    magic = 0x950412de
    version = 0
    
    # Calculate offsets
    header_size = 7 * 4
    
    # We need to build the string tables
    # OTable: (length, offset) for msgid
    # TTable: (length, offset) for msgstr
    # Data: null-terminated strings
    
    ids_content = b''
    strs_content = b''
    
    otable = []
    ttable = []
    
    # We'll put data after the tables
    # Tables size: count * 8 bytes each
    
    start_of_data = header_size + (count * 8) * 2
    
    current_offset = start_of_data
    
    for msgid, msgstr in sorted_messages:
        # Encode strings
        # We need to unescape them first if they have \n etc.
        # Simple unescape
        def unescape(s):
            return s.replace('\\n', '\n').replace('\\"', '"').replace('\\t', '\t')
            
        id_bytes = unescape(msgid).encode('utf-8') + b'\0'
        str_bytes = unescape(msgstr).encode('utf-8') + b'\0'
        
        otable.append((len(id_bytes) - 1, current_offset))
        ids_content += id_bytes
        current_offset += len(id_bytes)
        
        ttable.append((len(str_bytes) - 1, current_offset))
        strs_content += str_bytes
        current_offset += len(str_bytes)
        
    # Write file
    with open(mo_file_path, 'wb') as f:
        f.write(struct.pack('I', magic))
        f.write(struct.pack('I', version))
        f.write(struct.pack('I', count))
        f.write(struct.pack('I', header_size))
        f.write(struct.pack('I', header_size + count * 8))
        f.write(struct.pack('I', 0))
        f.write(struct.pack('I', 0))
        
        for length, offset in otable:
            f.write(struct.pack('II', length, offset))
            
        for length, offset in ttable:
            f.write(struct.pack('II', length, offset))
            
        f.write(ids_content)
        f.write(strs_content)
        
    print(f"Compiled {count} messages to {mo_file_path}")

if __name__ == "__main__":
    po_path = r"c:\Users\user\Documents\code\python\ExpressDeliverySystem\locale\zh_Hant\LC_MESSAGES\django.po"
    mo_path = r"c:\Users\user\Documents\code\python\ExpressDeliverySystem\locale\zh_Hant\LC_MESSAGES\django.mo"
    generate_mo_file(po_path, mo_path)
