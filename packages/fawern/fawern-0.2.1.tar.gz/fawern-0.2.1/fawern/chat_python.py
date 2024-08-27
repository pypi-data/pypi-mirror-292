import os
import subprocess
from groq import Groq
from dotenv import load_dotenv

try:
    # Load environment variables from .env file in the same directory as this script
    load_dotenv('.env')
    DEFAULT_API_KEY = os.getenv('GROQ_API_KEY')
    os.environ['GROQ_API_KEY'] = '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'
except Exception as e:
    print(f"Error loading environment variables: {e}")

class ChatPython:
    def __init__(self, model="llama-3.1-70b-versatile", temperature=1, max_tokens=1000, top_p=1):
        try:
            self.client = Groq()
            self.model = model
            self.temperature = temperature
            self.max_tokens = max_tokens
            self.top_p = top_p
            self.generated_code = ''
            self.prompt = ''
            self.file_name = ''
            self.root_directory = os.getcwd()
        except Exception as e:
            print(f"Error initializing ChatPython: {e}")

    def generate_code(self, prompt):
        try:
            self.prompt = f"Please generate Python code that is concise, functional, and directly implements the following requirements: {prompt}. Exclude any explanations, comments, or extra text. The code should adhere to Python best practices, ensure readability, and be ready for execution."
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": self.prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                stream=True,
                stop=None,
            )

            self.generated_code = ''
            for chunk in completion:
                self.generated_code += chunk.choices[0].delta.content or ""

            self.generated_code = self.remove_python_prefix(self.generated_code)
            return self.generated_code
        except Exception as e:
            print(f"Error generating code: {e}")
            return ""

    def remove_python_prefix(self, code):
        try:
            prefix = "python"
            code = code.replace("`", '')
            lines = code.splitlines()
            if lines[0].strip().startswith(prefix):
                lines[0] = lines[0].strip()[len(prefix):].strip()
                return "\n".join(lines)
            else:
                return code
        except Exception as e:
            print(f"Error removing python prefix: {e}")
            return code

    def generate_file_name(self):
        try:
            prompt_for_file_name = f"Based on the provided Python code description, generate a meaningful and contextually appropriate file name that ends with '.py'. The file name should reflect the primary functionality of the code. Here is the input: {self.prompt}"

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt_for_file_name}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                stream=True,
                stop=None,
            )

            generated_file_name = ''
            for chunk in completion:
                generated_file_name += chunk.choices[0].delta.content or ""

            generated_file_name = generated_file_name.strip()
            generated_file_name = generated_file_name.split("\n")[0].strip().replace("`", "").replace('"', '')

            return generated_file_name
        except Exception as e:
            print(f"Error generating file name: {e}")
            return "default_name.py"

    def write_code_to_file(self, path):
        try:
            self.file_name = self.generate_file_name()
            full_path = os.path.join(self.root_directory, path)
            os.makedirs(full_path, exist_ok=True)
            saved_path = os.path.join(full_path, self.file_name)
            print(f"Writing code to {saved_path}")

            if self.generated_code:
                with open(saved_path, "w") as file:
                    file.write(self.generated_code)
                print(f"Code written to {self.file_name}")
            else:
                raise Exception("No code generated yet")
        except Exception as e:
            print(f"Error writing code to file: {e}")

    def run_generated_code(self):
        try:
            result = subprocess.run(["python", self.file_name], capture_output=True, text=True, cwd=self.root_directory)
            return result.stdout
        except Exception as e:
            print(f"Error running generated code: {e}")
            return ""

class CodeAnalyzer:
    def __init__(self, api_key=DEFAULT_API_KEY, model="llama-3.1-70b-versatile", temperature=0.7, max_tokens=1000, top_p=1):
        try:
            os.environ['GROQ_API_KEY'] = api_key
            self.client = Groq()
            self.model = model
            self.temperature = temperature
            self.max_tokens = max_tokens
            self.top_p = top_p
        except Exception as e:
            print(f"Error initializing CodeAnalyzer: {e}")

    def analyze_code(self, code):
        try:
            prompt = f"Perform a comprehensive analysis of the following Python code, focusing on syntax errors, logical inconsistencies, and potential inefficiencies. Provide actionable suggestions to enhance code quality and performance. Here is the code:\n\n{code}"
            return self._get_completion(prompt)
        except Exception as e:
            print(f"Error analyzing code: {e}")
            return ""

    def find_syntax_errors(self, code):
        try:
            prompt = f"Identify and correct any syntax errors in the following Python code. Provide a revised version of the code with all corrections applied:\n\n{code}"
            return self._get_completion(prompt)
        except Exception as e:
            print(f"Error finding syntax errors: {e}")
            return ""

    def suggest_optimizations(self, code):
        try:
            prompt = f"Evaluate the efficiency of the following Python code and suggest optimizations where applicable. Aim to improve performance, readability, and maintainability. Here is the code:\n\n{code}"
            return self._get_completion(prompt)
        except Exception as e:
            print(f"Error suggesting optimizations: {e}")
            return ""

    def refactor_code(self, code):
        try:
            prompt = f"Refactor the following Python code to improve readability and maintainability, without changing its functionality:\n\n{code}"
            return self._get_completion(prompt)
        except Exception as e:
            print(f"Error refactoring code: {e}")
            return ""

    def get_code_explanation(self, code):
        try:
            prompt = f"Provide a detailed explanation of the following Python code, describing what each part of the code does:\n\n{code}"
            return self._get_completion(prompt)
        except Exception as e:
            print(f"Error getting code explanation: {e}")
            return ""

    def fix_code(self, code):
        try:
            prompt = f"Analyze and fix any issues found in the following Python code. Provide the corrected version:\n\n{code}"
            return self._get_completion(prompt)
        except Exception as e:
            print(f"Error fixing code: {e}")
            return ""

    def find_errors(self, code):
        try:
            prompt = f"Identify and explain any errors in the following Python code:\n\n{code}"
            return self._get_completion(prompt)
        except Exception as e:
            print(f"Error finding errors: {e}")
            return ""

    def suggest_improvements(self, code):
        try:
            prompt = f"Suggest improvements for the following Python code to enhance its performance, readability, and maintainability:\n\n{code}"
            return self._get_completion(prompt)
        except Exception as e:
            print(f"Error suggesting improvements: {e}")
            return ""

    def check_security_issues(self, code):
        try:
            prompt = f"Check the following Python code for any security vulnerabilities or potential issues:\n\n{code}"
            return self._get_completion(prompt)
        except Exception as e:
            print(f"Error checking security issues: {e}")
            return ""

    def generate_test_cases(self, code):
        try:
            prompt = f"Generate test cases for the following Python code to ensure it works correctly:\n\n{code}"
            return self._get_completion(prompt)
        except Exception as e:
            print(f"Error generating test cases: {e}")
            return ""

    def _get_completion(self, prompt):
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                stream=True,
                stop=None,
            )

            response = ''
            for chunk in completion:
                response += chunk.choices[0].delta.content or ""
            return response.strip()
        except Exception as e:
            print(f"Error getting completion: {e}")
            return ""

class CodeFormatter:
    def __init__(self):
        pass

    def format_code(self, code):
        try:
            prompt = f"Format the following Python code according to PEP8 standards:\n\n{code}"
            return self._get_completion(prompt)
        except Exception as e:
            print(f"Error formatting code: {e}")
            return ""

    def _get_completion(self, prompt):
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                stream=True,
                stop=None,
            )

            response = ''
            for chunk in completion:
                response += chunk.choices[0].delta.content or ""
            return response.strip()
        except Exception as e:
            print(f"Error getting completion: {e}")
            return ""

class ErrorLogAnalyzer:
    def __init__(self):
        try:
            self.error_logs = []
        except Exception as e:
            print(f"Error initializing ErrorLogAnalyzer: {e}")

    def log_error(self, error_message):
        try:
            self.error_logs.append(error_message)
        except Exception as e:
            print(f"Error logging error: {e}")

    def analyze_errors(self):
        try:
            if not self.error_logs:
                return "No errors logged."

            prompt = f"Analyze the following Python error logs and provide suggestions for fixing them:\n\n{self.error_logs}"
            return self._get_completion(prompt)
        except Exception as e:
            print(f"Error analyzing errors: {e}")
            return ""

    def _get_completion(self, prompt):
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                stream=True,
                stop=None,
            )

            response = ''
            for chunk in completion:
                response += chunk.choices[0].delta.content or ""
            return response.strip()
        except Exception as e:
            print(f"Error getting completion: {e}")
            return ""

class BaseAssistant:
    def __init__(self, model="llama-3.1-70b-versatile", temperature=0.7, max_tokens=1000, top_p=1):
        try:
            self.client = Groq()
            self.model = model
            self.temperature = temperature
            self.max_tokens = max_tokens
            self.top_p = top_p
        except Exception as e:
            print(f"Error initializing BaseAssistant: {e}")

    def _get_completion(self, prompt):
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                stream=True,
                stop=None,
            )

            response = ''
            for chunk in completion:
                response += chunk.choices[0].delta.content or ""
            return response.strip()
        except Exception as e:
            print(f"Error getting completion: {e}")
            return ""

class CodeReviewer(BaseAssistant):
    def review_code(self, code):
        try:
            prompt = f"Review the following Python code as a senior developer would. Provide feedback on its structure, clarity, maintainability, and overall quality:\n\n{code}"
            return self._get_completion(prompt)
        except Exception as e:
            print(f"Error reviewing code: {e}")
            return ""

class DocumentationGenerator(BaseAssistant):
    def generate_docstrings(self, code):
        try:
            prompt = f"Generate detailed docstrings and inline comments for the following Python code:\n\n{code}"
            return self._get_completion(prompt)
        except Exception as e:
            print(f"Error generating docstrings: {e}")
            return ""

class ConvertToPython(BaseAssistant):
    def convert_code(self, code):
        try:
            prompt = f"Convert the given code to Python code:\n\n{code}"
            return self._get_completion(prompt)
        except Exception as e:
            print(f"Error converting code: {e}")
            return ""

class CodeVisualizer(BaseAssistant):
    def visualize_code(self, code):
        try:
            prompt = f"Create a flowchart or class diagram for the following Python code:\n\n{code}"
            return self._get_completion(prompt)
        except Exception as e:
            print(f"Error visualizing code: {e}")
            return ""

class BugFixer(BaseAssistant):
    def fix_bugs(self, code):
        try:
            prompt = f"Automatically identify and fix any bugs in the following Python code. Provide the corrected version:\n\n{code}"
            return self._get_completion(prompt)
        except Exception as e:
            print(f"Error fixing bugs: {e}")
            return ""

class UnitTestGenerator(BaseAssistant):
    def generate_tests(self, code):
        try:
            prompt = f"Generate unit tests for the following Python code. Ensure that all functions and methods are covered:\n\n{code}"
            return self._get_completion(prompt)
        except Exception as e:
            print(f"Error generating unit tests: {e}")
            return ""
