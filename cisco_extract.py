import PyPDF2
import re
import os

# Define a function to build and write a test
def build_test(level, name, text, config_to_mitigate, ref, folder_name):
    ref = ref.strip()
    sev = "low"
    if "1" in level:
        sev = "medium"
    
    # Define text patterns to be stripped from 'text'
    text_to_strip = ['hostname#show running -config | inc ', 'hostname#show running -config | incl', 'hostname#show run | incl', 'hostname#show run | inc']
    for t in text_to_strip:
        text = text.replace(t, "").strip()
    
    # Define the test content template
    test_content = f'''import pytest
from comfy.compliance import *

@{sev}(
  name = '{name}',
  platform = ['cisco_ios']
)
def {name}(configuration, commands, device):
    assert '{text}' in configuration

# Remediation: {config_to_mitigate}

# References: {ref}
'''
    
    # Create the folder if it doesn't exist
    os.makedirs(folder_name, exist_ok=True)
    
    # Build the file path within the folder
    file_path = os.path.join(folder_name, f"{name}.py")
    
    # Write the test content to the file within the folder
    with open(file_path, 'w') as file:
        file.write(test_content)
    
    print(f"Test written to {name}.py in {file_path}")

# Define a function to convert text to a rule name
def convert_to_rule_format(text):
    parts = text.split()
    section_number = ''
    command_description = ''

    for part in parts:
        if '.' in part and part.replace('.', '').isdigit():
            section_number = part.replace('.', '')
        elif section_number and '(' not in part:
            command_description += part + ' '

    command_description = command_description.strip()
    command_description = ''.join(e for e in command_description if e.isalnum() or e.isspace()).lower()
    command_description = command_description.replace(' ', '_')

    rule_name = f"rule_{section_number}_{command_description}"
    return rule_name

# Define text patterns to search for in the PDF
page_pattern = r"Page\s+(\d+)\s+(\d+(?:\.\d+)*\s+.+)"
hostname_config_pattern = r"hostname\(config\)#"
hostname_show_pattern = r"hostname#show"
severity = r"•  Level"
ref_pattern = r" https?://"

name = ""
level = ""
show_pattern = ""
config_pattern = ""
ref = ""
folder_name = "default"

# Open the PDF file
with open('cis_cisco.pdf', 'rb') as pdfFileObj:
    for i in range(14, 214):  # Loop through pages
        pdfReader = PyPDF2.PdfReader(pdfFileObj)
        pageObj = pdfReader.pages[i]
        
        for line in pageObj.extract_text().splitlines():
            if re.search(page_pattern, line):
                if name != "" and level != "":
                    build_test(level, name, show_pattern, config_pattern, ref, folder_name)
                    name = ""
                    level = ""
                    show_pattern = ""
                    config_pattern = ""
                    ref = ""
                
                name = convert_to_rule_format(line)
                if re.match(r"rule_\d{2}_\w+", name):
                    folder_name = re.sub(r"rule_\d{2}_", "", name)
            if re.search(hostname_config_pattern, line):
                config_pattern = line
            if re.search(hostname_show_pattern, line):
                show_pattern = line
            if re.search(severity, line):
                level = line
            if re.search(ref_pattern, line):
                ref = line
