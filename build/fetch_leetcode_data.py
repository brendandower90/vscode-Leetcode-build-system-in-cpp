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
    else:
        raise Exception(f"Query failed to run with a {response.status_code}. Response: {response.text}")

def extract_examples(content):
    example_pattern = re.compile(r'<pre>(.*?)</pre>', re.DOTALL)
    examples = example_pattern.findall(content)

    processed_examples = []
    for example in examples:
        example = re.sub(r'<[^>]*>', '', example)
        example = re.sub(r'\\u2019', "'", example)
        example = re.sub(r'\\u2014', '-', example)
        example = re.sub(r'&lt;', '<', example)
        example = re.sub(r'&gt;', '>', example)
        example = re.sub(r'&#39;', "'", example)
        example = re.sub(r'\\n', '\n', example)
        example = example.strip()
        
        input_data = re.search(r'Input:\s*(\w+)\s*=\s*(\[.*?\])', example)
        output_data = re.search(r'Output:\s*(\[.*?\])', example)
        explanation_data = re.search(r'Explanation:\s*(.*)', example, re.DOTALL)
        
        if input_data and output_data and explanation_data:
            variable_name = input_data.group(1)
            input_value = input_data.group(2)
            explanation = explanation_data.group(1).strip().split('\n')
            explanation = [line.strip() for line in explanation]
            processed_examples.append((input_value, output_data.group(1), explanation))
    
    return processed_examples






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
    html_tag_re = re.compile(r'<[^>]+>')
    cleaned_text = html_tag_re.sub('', content)
    cleaned_text = re.sub(r'\\u2019', "'", cleaned_text)
    cleaned_text = re.sub(r'\\u2014', '-', cleaned_text)
    cleaned_text = re.sub(r'&lt;', '<', cleaned_text)
    cleaned_text = re.sub(r'&gt;', '>', cleaned_text)
    cleaned_text = re.sub(r'&#39;', "'", cleaned_text)
    cleaned_text = re.sub(r'\\n', '\n', cleaned_text)
    cleaned_text = re.sub(r'&nbsp;', ' ', cleaned_text)

    description = ''
    constraints = ''
    if 'Constraints:' in cleaned_text:
        description, constraints = cleaned_text.split('Constraints:')
    elif 'Constraints: ' in cleaned_text:
        description, constraints = cleaned_text.split('Constraints: ')
    
    # Split description from examples
    description_parts = description.split('Example')
    if len(description_parts) > 1:
        description = description_parts[0].strip()
    else:
        description = description.strip()
    constraints = constraints.strip().split('\n')

    wrapped_description = format_text_with_line_breaks(description, line_length)
    wrapped_constraints = '\n'.join([constraint.strip() for  constraint in constraints if constraint.strip()])

    return wrapped_description, wrapped_constraints


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
