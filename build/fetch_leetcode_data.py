import requests
import re, os
import json
import sys

def fetch_leetcode_data(title_slug):
    url = 'https://leetcode.com/graphql'
    query = """
    query questionData($titleSlug: String!) {
        question(titleSlug: $titleSlug) {
            questionFrontendId
            title
            difficulty
            content
        }
    }
    """
    variables = {
        "titleSlug": title_slug
    }

    # Initialize a session
    session = requests.Session()

    # Set headers
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': f'python/{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}',
        'Referer': f'https://leetcode.com/problems/{title_slug}/',
    }

    # Make the request
    response = session.post(url, json={'query': query, 'variables': variables}, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 403:
        raise Exception("Forbidden: Ensure you are logged in and your session is valid.")
    else:
        raise Exception(f"Query failed to run with a {response.status_code}. Response: {response.text}")

def extract_examples(content):
    examples = []
    pattern = re.compile(r'<strong>Input:</strong>\s*(.*?)\s*<strong>Output:</strong>\s*(.*?)\s*</pre>', re.DOTALL)
    matches = pattern.findall(content)
    for match in matches:
        input_data = re.sub(r'<.*?>', '', match[0]).strip()
        output_data = re.sub(r'<.*?>', '', match[1]).strip()
        input_data = format_data(input_data.replace('nums = ', '').replace('null', 'None'))
        output_data = format_data(output_data.replace('null', 'None'))
        examples.append((input_data, output_data))
    return examples


def format_text_with_line_breaks(text, line_length=80):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 <= line_length:
            if current_line:
                current_line += " "
            current_line += word
        else:
            lines.append(current_line)
            current_line = word
    if (current_line):
        lines.append(current_line)
    return "\n".join(lines)


def extract_test_info(content, line_length=80):
    # Convert html symbols to ascii
    content = content.replace('&lt;', '<').replace('&gt;', '>').replace('&nbsp;', ' ')

    # Extract description
    description_pattern = re.compile(r'<p>(.*?)</p>', re.DOTALL)
    description_match = description_pattern.search(content)
    description = re.sub(r'<.*?>', '', description_match.group(1)).strip() if description_match else ""
    description = re.sub(r'[^a-zA-Z0-9 .,]', '', description)
    description = format_text_with_line_breaks(description, line_length)
    
    # Extract constraints
    constraints_pattern = re.compile(r'<ul>(.*?)</ul>', re.DOTALL)
    constraints_match = constraints_pattern.search(content)
    constraints = ""
    if constraints_match:
        constraint_items_pattern = re.compile(r'<li>(.*?)</li>', re.DOTALL)
        constraints = ' • '.join(
            item.strip() for item in constraint_items_pattern.findall(constraints_match.group(1))
        )
        constraints = re.sub(r'<code>(.*?)</code>', r'\1', constraints)  # Remove <code> tags around constraints


    return description, constraints


def format_data(data):
    if isinstance(data, str):
        data = data.replace('[', '{').replace(']', '}')
        data = re.sub(r'\s+', ' ', data)  # Ensure single spaces
        return data
    if isinstance(data, list):
        formatted_list = ", ".join(format_data(item) for item in data)
        return f"{{ {formatted_list} }}"
    return str(data)


def update_test_template(dest_dir, filename, examples):
    test_file_path = os.path.join(dest_dir, f'{filename}-tests.cpp')
    
    with open(test_file_path, 'r') as file:
        lines = file.readlines()
    
    # Find the testCases section
    start_index = next(i for i, line in enumerate(lines) if 'std::vector<TestCase> testCases' in line) + 1
    end_index = next(i for i, line in enumerate(lines[start_index:]) if '};' in line)
    
    # Construct the new test cases content
    new_test_cases = "std::vector<TestCase> testCases = {\n"
    for example in examples:
        new_test_cases += f"    {{\n        {format_data(example[0])},  // Input\n        {format_data(example[1])}   // Expected Output\n    }},\n"
    new_test_cases += "};\n"
    
    # Replace the old test cases section
    lines[start_index:end_index] = [new_test_cases]
    
    # Write the updated content back to the file
    with open(test_file_path, 'w') as file:
        file.writelines(lines)
    print(f"Updated test cases in {test_file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fetch_leetcode_data.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    title_slug = filename.split('.', 1)[1]  # Remove the number from the filename
    
    try:
        data = fetch_leetcode_data(title_slug)
        content = data['data']['question']['content']
        examples = extract_examples(content)
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dest_dir = os.path.join(parent_dir, filename)
        update_test_template(dest_dir, filename, examples)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
