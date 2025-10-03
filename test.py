import os
import ast
import openai

# --------------------------
# CONFIG
# --------------------------
LLM_API_KEY = "YOUR_API_KEY"  # Replace with your LLM API key
CODE_EXTENSIONS = [".py"]     # Languages to process

# --------------------------
# STEP 1: Get code files
# --------------------------
def get_code_files(folder, extensions=CODE_EXTENSIONS):
    files = []
    for root, _, filenames in os.walk(folder):
        for f in filenames:
            if any(f.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, f))
    return files

# --------------------------
# STEP 2: Extract functions/classes
# --------------------------
def extract_code_blocks(file_path):
    with open(file_path, "r") as f:
        source = f.read()
    tree = ast.parse(source)
    blocks = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            blocks.append({
                "type": "function" if isinstance(node, ast.FunctionDef) else "class",
                "name": node.name,
                "lineno": node.lineno,
                "end_lineno": node.body[-1].lineno,
                "indent": " " * node.col_offset,
                "code": "\n".join(source.splitlines()[node.lineno-1 : node.body[-1].lineno])
            })
    return blocks, source

# --------------------------
# STEP 3: Generate docstring using LLM
# --------------------------
def generate_docstring(code_block):
    prompt = f"""
    Write a Python docstring for this {code_block['type']}:
    - Short description
    - Parameters (if any)
    - Return value (if any)
    Code:
    {code_block['code']}
    """
    response = openai.ChatCompletion.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
        api_key=LLM_API_KEY
    )
    return response['choices'][0]['message']['content'].strip().replace('"""', '\"\"\"')  # avoid breaking quotes

# --------------------------
# STEP 4: Insert docstrings into code
# --------------------------
def insert_docstrings(file_path):
    blocks, source = extract_code_blocks(file_path)
    lines = source.splitlines()

    for block in reversed(blocks):  # reverse to avoid line number shifting
        docstring = generate_docstring(block)
        insert_line = block['lineno']
        indentation = block['indent'] + "    " if block["type"] == "function" else block['indent'] + "    "
        doc_lines = [indentation + line for line in docstring.splitlines()]
        docstring_block = [indentation + '"""'] + doc_lines + [indentation + '"""']
        lines.insert(insert_line, "\n".join(docstring_block))

    with open(file_path, "w") as f:
        f.write("\n".join(lines))
    print(f"[+] Updated docstrings in {file_path}")

# --------------------------
# STEP 5: Run tool
# --------------------------
def run_tool(folder):
    files = get_code_files(folder)
    for file in files:
        insert_docstrings(file)

# --------------------------
# USAGE
# --------------------------
if __name__ == "__main__":
    folder_to_process = "./my_project"  # replace with your folder
    run_tool(folder_to_process)
