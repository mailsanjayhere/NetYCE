import PyPDF2
import re
import os
test1234

# Define a function to build and write a test
def build_test(level, name, text, config_to_mitigate, ref, folder_name):
    ref = ref.strip().replace("1.", " ").replace("2.", " ").replace(" ", "")
    ref1 = ref[:90]  # First 100 characters
    ref2 = ref[90:]  # The rest of the characters
    config_to_mitigate = config_to_mitigate.replace("\\_", "_")
    if config_to_mitigate == "":
        config_to_mitigate = "-"
    sev = "low"
    if "1" in level:
        sev = "medium"
    # Define text patterns to be stripped from 'text'
    text_to_strip = ['(Cisco Controller) ><strong>', '</strong>']
    for t in text_to_strip:
        text = text.replace(t, "").strip()

    # Define the test content template
    if "show" in text:
        assert_text = text
        test_content = f'''from comfy.compliance import {sev}


@{sev}(
  name='{name}',
  platform=['cisco_wlc'],
  commands=dict(chk_cmd='{text}')
)
def {name}(commands):
    uri = (
        "{ref1}"
        "{ref2}"
    )

    remediation = (f"""
    Remediation: {config_to_mitigate}

    References: {{uri}}

    """)

    assert '{assert_text}' in commands.chk_cmd, remediation
'''
    else:
        test_content = f'''from comfy.compliance import {sev}


@{sev}(
  name='{name}',
  platform=['cisco_wlc']
)
def {name}(configuration):
    uri = (
        "{ref1}"
        "{ref2}"
    )

    remediation = (f"""
    Remediation: {config_to_mitigate}

    References: {{uri}}

    """)

    assert '{text}' in configuration, remediation
'''

    # Create the "tests" folder if it doesn't exist
    tests_folder = "wlc_tests"
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
    cmd_desc = ''

    for part in parts:
        if '.' in part and part.replace('.', '').isdigit():
            section_number = part.replace('.', '')
        elif section_number and '(' not in part:
            cmd_desc += part + ' '

    cmd_desc = cmd_desc.strip()
    cmd_desc = ''.join(e for e in cmd_desc if e.isalnum() or e.isspace()).lower()
    cmd_desc = cmd_desc.replace(' ', '_')

    rule_name = f"rule_{section_number}_{cmd_desc}"
    return rule_name


def fix_typo(text):
    if "l ogin" in text:
        text = text.replace("l ogin", "login")
    if "aa a" in text:
        text = text.replace("aa a", "aaa")
    return text


# Define text patterns to search for in the PDF
page_pattern = r"Page\s+(\d+)\s+(\d+(?:\.\d+)*\s+.+)"
# Regex to match 'Hostname' or 'hostname' or 'hostname(config)#' or
# 'hostname#(config)' or 'hostname (config)' or 'hostname(config-')
hostname_config_pattern = r"ostname\s?\(config|\#\(config"
hostname_show_pattern = r"\(Cisco Controller\) ><strong>show"
severity = r"•  Level"
ref_pattern = r" https?://"

name = ""
level = ""
show_pattern = ""
config_pattern = ""
ref = ""
folder_name = "default"
show_run_pattern = ["hostname#show running-config | incl ", "hostname#show run ning-config | inc ",
                    "hostname#sh run | incl ", "hostname#show running-config | inc",
                    "hostname#show run | i ", "hostname#show run | include"]

# Open the  PDF file
with open('cis_wlc.pdf', 'rb') as pdfFileObj:
    for i in range(11, 44):  # Loop through pages
        pdfReader = PyPDF2.PdfReader(pdfFileObj)
        pageObj = pdfReader.pages[i]
        print(pageObj.extract_text())
        for line in pageObj.extract_text().splitlines():
            # Reference URLs are broken lines in PDF,
            # below two lines is to concatenate them in single line and cleaning up spaces
            if ref.endswith("-"):
                ref = ref + line.strip()
            if re.search(page_pattern, line):
                if name != "" and level != "":
                    ref = ref.replace(" ", "")
                    for patt in show_run_pattern:
                        if patt in show_pattern:
                            show_pattern = show_pattern.replace(patt, "")
                    show_pattern = fix_typo(show_pattern)
                    build_test(level, name, show_pattern, config_pattern, ref, folder_name)
                    name = ""
                    level = ""
                    show_pattern = ""
                    config_pattern = ""
                    ref = ""

                name = remove_space_before_hyphen(convert_to_rule_format(line))
                if re.match(r"rule_\d{2}_\w+", name):
                    folder_name = re.sub(r"rule_", "", name)
            if re.search(hostname_config_pattern, line):
                config_pattern = remove_space_before_hyphen(line).strip()
                config_pattern = config_pattern.replace("{", "{{").replace("}", "}}")
            if re.search(hostname_show_pattern, line):
                show_pattern = remove_space_before_hyphen(line)
            if re.search(severity, line):
                level = remove_space_before_hyphen(line)
            if re.search(ref_pattern, line):
                ref = remove_space_before_hyphen(line)
