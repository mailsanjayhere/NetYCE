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
    
    # Create the "tests" folder if it doesn't exist
    tests_folder = "tests"
    os.makedirs(tests_folder, exist_ok=True)

    # Create the folder for the current test if it doesn't exist
    os.makedirs(os.path.join(tests_folder, folder_name), exist_ok=True)

    # Build the file path within the folder
    file_path = os.path.join(tests_folder, folder_name, f"{name}.py")
    
    # Write the test content to the file within the folder
    with open(file_path, 'w') as file:
        file.write(test_content)
    
    print(f"Test written to {name}.py in {file_path}")


def remove_space_before_hyphen(input_string):
    # Define a regular expression pattern to match the specified pattern
    pattern = r'(\s-)([a-zA-Z])'

    # Use re.sub to remove the space before the hyphen
    modified_string = re.sub(pattern, r'-\2', input_string)
    return modified_string


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
hostname_show_pattern = r"hostname#sh"
severity = r"•  Level"
ref_pattern = r" https?://"

name = ""
level = ""
show_pattern = ""
config_pattern = ""
ref = ""
folder_name = "default"
show_run_pattern=["hostname#show running-config | incl ","hostname#show run ning-config | inc ","hostname#sh run | incl ","hostname#show running-config | inc","hostname#show run | i "]

# Open the  PDF file
with open('cis_cisco.pdf', 'rb') as pdfFileObj:
    for i in range(14, 214):  # Loop through pages
        pdfReader = PyPDF2.PdfReader(pdfFileObj)
        pageObj = pdfReader.pages[i]

        for line in pageObj.extract_text().splitlines():
# Reference URLs are broken lines in PDF, below two lines is to concatenate them in single line and cleaning up spaces
            if ref.endswith("-"):
                ref+=line.strip()
            if re.search(page_pattern, line):
                if name != "" and level != "":
                    ref=ref.replace(" ","")
                    for patt in show_run_pattern:
                      if patt in show_pattern:
                        show_pattern = show_pattern.replace(patt,"")
                    build_test(level, name, show_pattern, config_pattern, ref, folder_name)
                    name = ""
                    level = ""
                    show_pattern = ""
                    config_pattern = ""
                    ref = ""
                
                name = remove_space_before_hyphen(convert_to_rule_format(line))
                if re.match(r"rule_\d{2}_\w+", name):
                    folder_name = re.sub(r"rule_\d{2}_", "", name)
            if re.search(hostname_config_pattern, line):
                config_pattern = remove_space_before_hyphen(line)
            if re.search(hostname_show_pattern, line):
                show_pattern = remove_space_before_hyphen(line)
            if re.search(severity, line):
                level = remove_space_before_hyphen(line)
            if re.search(ref_pattern, line):
                ref = remove_space_before_hyphen(line)
