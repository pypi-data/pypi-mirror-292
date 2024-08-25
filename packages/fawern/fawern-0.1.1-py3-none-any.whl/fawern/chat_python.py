import os
import subprocess
from groq import Groq
from dotenv import load_dotenv

os.chdir(os.path.dirname(os.path.abspath(__file__)))
load_dotenv('.env')
DEFAULT_API_KEY = os.getenv('GROQ_API_KEY')
os.environ['GROQ_API_KEY'] = DEFAULT_API_KEY

class ChatPython:
    """
    ChatPython is an AI Python developer that generates Python code based on a given input prompt.

    Attributes:
        model (str): The model name used for code generation.
        temperature (float): Sampling temperature to control the creativity of the generated code.
        max_tokens (int): The maximum number of tokens in the generated code.
        top_p (float): Controls diversity via nucleus sampling.
        generated_code (str): Stores the generated code.
        prompt (str): Stores the input prompt for code generation.
        file_name (str): Stores the generated file name for saving the code.
    """

    def __init__(self, model="llama-3.1-70b-versatile", temperature=1, max_tokens=1000, top_p=1):
        """
        Initializes the ChatPython class with model, temperature, max_tokens, and top_p attributes.

        Args:
            model (str): The name of the model to use for code generation.
            temperature (float): The sampling temperature.
            max_tokens (int): The maximum number of tokens.
            top_p (float): The nucleus sampling value.
        """
        self.client = Groq()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.generated_code = ''
        self.prompt = ''
        self.file_name = ''

    def generate_code(self, prompt):
        """
        Generates Python code based on the provided prompt.

        Args:
            prompt (str): The input prompt describing the code requirements.

        Returns:
            str: The generated Python code.
        """
        self.prompt = f"Please generate Python code that is concise, functional, and directly implements the following requirements: {prompt}. Exclude any explanations, comments, or extra text. The code should adhere to Python best practices, ensure readability, and be ready for execution."
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": self.prompt
                }
            ],
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

    def remove_python_prefix(self, code):
        """
        Removes the 'python' prefix from the generated code if it exists.

        Args:
            code (str): The generated code string.

        Returns:
            str: The cleaned code without the 'python' prefix.
        """
        prefix = "python"
        code = code.replace("`", '')
        lines = code.splitlines()
        if lines[0].strip().startswith(prefix):
            lines[0] = lines[0].strip()[len(prefix):].strip()
            return "\n".join(lines)
        else:
            return code

    def generate_file_name(self):
        """
        Generates a meaningful and contextually appropriate file name based on the code description.

        Returns:
            str: The generated file name ending with '.py'.
        """
        prompt_for_file_name = f"Based on the provided Python code description, generate a meaningful and contextually appropriate file name that ends with '.py'. The file name should reflect the primary functionality of the code. Here is the input: {self.prompt}"

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt_for_file_name
                }
            ],
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

    def write_code_to_file(self, path):
        """
        Writes the generated code to a file with the generated file name.

        Args:
            path (str): The directory path where the file should be saved.
        """
        self.file_name = self.generate_file_name()
        saved_path = os.path.join(path, self.file_name)
        print(f"Writing code to {saved_path}")
        if self.generated_code:
            with open(saved_path, "w") as file:
                file.write(self.generated_code)
            print(f"Code written to {self.file_name}")
        else:
            raise Exception("No code generated yet")

    def run_generated_code(self):
        """
        Executes the generated Python code in a subprocess.

        Returns:
            str: The output of the executed code.
        """
        try:
            result = subprocess.run(["python", self.file_name], capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            raise Exception(f"Cannot run code: {e}")


class CodeAnalyzer:
    """
    CodeAnalyzer is a Python code analysis AI tool that can analyze, refactor, and optimize Python code based on a given input prompt.

    Attributes:
        model (str): The model name used for analysis.
        temperature (float): Sampling temperature for the analysis.
        max_tokens (int): Maximum number of tokens for the analysis.
        top_p (float): Controls diversity via nucleus sampling.
    """

    def __init__(self, api_key=DEFAULT_API_KEY, model="llama-3.1-70b-versatile", temperature=0.7, max_tokens=1000, top_p=1):
        """
        Initializes the CodeAnalyzer class with API key, model, temperature, max_tokens, and top_p attributes.

        Args:
            model (str): The model name for analysis.
            temperature (float): The sampling temperature.
            max_tokens (int): The maximum number of tokens.
            top_p (float): The nucleus sampling value.
        """
        os.environ['GROQ_API_KEY'] = api_key
        self.client = Groq()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p

    def analyze_code(self, code):
        """
        Performs a comprehensive analysis of the provided Python code, focusing on errors and inefficiencies.

        Args:
            code (str): The Python code to analyze.

        Returns:
            str: The analysis and suggestions for improving the code.
        """
        prompt = f"Perform a comprehensive analysis of the following Python code, focusing on syntax errors, logical inconsistencies, and potential inefficiencies. Provide actionable suggestions to enhance code quality and performance. Here is the code:\n\n{code}"
        return self._get_completion(prompt)

    def find_syntax_errors(self, code):
        """
        Identifies and corrects syntax errors in the provided Python code.

        Args:
            code (str): The Python code to check for syntax errors.

        Returns:
            str: The corrected version of the code.
        """
        prompt = f"Identify and correct any syntax errors in the following Python code. Provide a revised version of the code with all corrections applied:\n\n{code}"
        return self._get_completion(prompt)

    def suggest_optimizations(self, code):
        """
        Suggests optimizations to improve the efficiency and readability of the provided Python code.

        Args:
            code (str): The Python code to optimize.

        Returns:
            str: Suggestions for improving the code.
        """
        prompt = f"Evaluate the efficiency of the following Python code and suggest optimizations where applicable. Aim to improve performance, readability, and maintainability. Here is the code:\n\n{code}"
        return self._get_completion(prompt)

    def refactor_code(self, code):
        """
        Refactors the provided Python code to improve readability and maintainability without changing functionality.

        Args:
            code (str): The Python code to refactor.

        Returns:
            str: The refactored code.
        """
        prompt = f"Refactor the following Python code to improve readability and maintainability, without changing its functionality:\n\n{code}"
        return self._get_completion(prompt)

    def get_code_explanation(self, code):
        """
        Provides a detailed explanation of the provided Python code, describing its functionality.

        Args:
            code (str): The Python code to explain.

        Returns:
            str: A detailed explanation of the code.
        """
        prompt = f"Provide a detailed explanation of the following Python code, describing what each part of the code does:\n\n{code}"
        return self._get_completion(prompt)

    def fix_code(self, code):
        """
        Analyzes and fixes any issues found in the provided Python code.

        Args:
            code (str): The Python code to fix.

        Returns:
            str: The corrected version of the code.
        """
        prompt = f"Analyze and fix any issues found in the following Python code. Provide the corrected version:\n\n{code}"
        return self._get_completion(prompt)

    def find_errors(self, code):
        """
        Identifies and explains any errors in the provided Python code.

        Args:
            code (str): The Python code to analyze for errors.

        Returns:
            str: A detailed explanation of any errors found.
        """
        prompt = f"Identify and explain any errors in the following Python code:\n\n{code}"
        return self._get_completion(prompt)

    def suggest_improvements(self, code):
        """
        Suggests improvements for enhancing the performance, readability, and maintainability of the provided Python code.

        Args:
            code (str): The Python code to improve.

        Returns:
            str: Suggestions for improving the code.
        """
        prompt = f"Suggest improvements for the following Python code to enhance its performance, readability, and maintainability:\n\n{code}"
        return self._get_completion(prompt)

    def check_security_issues(self, code):
        """
        Checks the provided Python code for any security vulnerabilities or potential issues.

        Args:
            code (str): The Python code to analyze for security issues.

        Returns:
            str: A report on any security vulnerabilities found.
        """
        prompt = f"Check the following Python code for any security vulnerabilities or potential issues:\n\n{code}"
        return self._get_completion(prompt)

    def generate_test_cases(self, code):
        """
        Generates test cases to ensure the correctness of the provided Python code.

        Args:
            code (str): The Python code to generate test cases for.

        Returns:
            str: The generated test cases.
        """
        prompt = f"Generate test cases for the following Python code to ensure it works correctly:\n\n{code}"
        return self._get_completion(prompt)

    def _get_completion(self, prompt):
        """
        Internal method to generate a completion response based on the provided prompt.

        Args:
            prompt (str): The input prompt for generating a completion.

        Returns:
            str: The generated completion response.
        """
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
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


class CodeFormatter:
    """
    CodeFormatter formats Python code according to PEP8 standards.

    Attributes:
        None
    """

    def __init__(self):
        """
        Initializes the CodeFormatter class.
        """
        pass

    def format_code(self, code):
        """
        Formats the provided Python code according to PEP8 standards.

        Args:
            code (str): The Python code to format.

        Returns:
            str: The formatted code.
        """
        prompt = f"Format the following Python code according to PEP8 standards:\n\n{code}"
        return self._get_completion(prompt)

    def _get_completion(self, prompt):
        """
        Internal method to generate a completion response based on the provided prompt.

        Args:
            prompt (str): The input prompt for generating a completion.

        Returns:
            str: The generated completion response.
        """
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


class ErrorLogAnalyzer:
    """
    ErrorLogAnalyzer logs and analyzes Python errors, providing suggestions for fixing them.

    Attributes:
        error_logs (list): A list of logged error messages.
    """

    def __init__(self):
        """
        Initializes the ErrorLogAnalyzer class with an empty error log list.
        """
        self.error_logs = []

    def log_error(self, error_message):
        """
        Logs an error message for future analysis.

        Args:
            error_message (str): The error message to log.
        """
        self.error_logs.append(error_message)

    def analyze_errors(self):
        """
        Analyzes logged errors and provides suggestions for fixing them.

        Returns:
            str: Suggestions for fixing the logged errors.
        """
        if not self.error_logs:
            return "No errors logged."

        prompt = f"Analyze the following Python error logs and provide suggestions for fixing them:\n\n{self.error_logs}"
        return self._get_completion(prompt)

    def _get_completion(self, prompt):
        """
        Internal method to generate a completion response based on the provided prompt.

        Args:
            prompt (str): The input prompt for generating a completion.

        Returns:
            str: The generated completion response.
        """
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


class BaseAssistant:
    """
    BaseAssistant serves as a base class for various assistant functionalities, such as code reviewing, documentation generation, and more.

    Attributes:
        model (str): The model name used for generating completions.
        temperature (float): Sampling temperature for generating responses.
        max_tokens (int): Maximum number of tokens for generating responses.
        top_p (float): Controls diversity via nucleus sampling.
    """

    def __init__(self, model="llama-3.1-70b-versatile", temperature=0.7, max_tokens=1000, top_p=1):
        """
        Initializes the BaseAssistant class with model, temperature, max_tokens, and top_p attributes.

        Args:
            model (str): The model name for generating responses.
            temperature (float): The sampling temperature.
            max_tokens (int): The maximum number of tokens.
            top_p (float): The nucleus sampling value.
        """
        self.client = Groq()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p

    def _get_completion(self, prompt):
        """
        Internal method to generate a completion response based on the provided prompt.

        Args:
            prompt (str): The input prompt for generating a completion.

        Returns:
            str: The generated completion response.
        """
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
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


class CodeReviewer(BaseAssistant):
    """
    CodeReviewer provides functionality to review Python code and provide feedback on its structure, clarity, and overall quality.

    Methods:
        review_code(code): Reviews the given Python code and provides feedback.
    """

    def review_code(self, code):
        """
        Reviews the provided Python code as a senior developer would.

        Args:
            code (str): The Python code to review.

        Returns:
            str: Feedback on the code's structure, clarity, maintainability, and quality.
        """
        prompt = f"Review the following Python code as a senior developer would. Provide feedback on its structure, clarity, maintainability, and overall quality:\n\n{code}"
        return self._get_completion(prompt)


class DocumentationGenerator(BaseAssistant):
    """
    DocumentationGenerator generates detailed docstrings and inline comments for Python code.

    Methods:
        generate_docstrings(code): Generates docstrings for the provided Python code.
    """

    def generate_docstrings(self, code):
        """
        Generates detailed docstrings and inline comments for the provided Python code.

        Args:
            code (str): The Python code to document.

        Returns:
            str: The Python code with added docstrings and inline comments.
        """
        prompt = f"Generate detailed docstrings and inline comments for the following Python code:\n\n{code}"
        return self._get_completion(prompt)


class ConvertToPython(BaseAssistant):
    """
    ConvertToPython converts code from other languages to Python code.

    Methods:
        convert_code(code): Converts the given code to Python.
    """

    def convert_code(self, code):
        """
        Converts the provided code from another language to Python.

        Args:
            code (str): The code to convert to Python.

        Returns:
            str: The converted Python code.
        """
        prompt = f"Convert the given code to Python code:\n\n{code}"
        return self._get_completion(prompt)


class CodeVisualizer(BaseAssistant):
    """
    CodeVisualizer generates visual representations, such as flowcharts or class diagrams, for Python code.

    Methods:
        visualize_code(code): Visualizes the given Python code.
    """

    def visualize_code(self, code):
        """
        Creates a flowchart or class diagram for the provided Python code.

        Args:
            code (str): The Python code to visualize.

        Returns:
            str: The visual representation of the code.
        """
        prompt = f"Create a flowchart or class diagram for the following Python code:\n\n{code}"
        return self._get_completion(prompt)


class BugFixer(BaseAssistant):
    """
    BugFixer automatically identifies and fixes bugs in Python code.

    Methods:
        fix_bugs(code): Fixes bugs in the provided Python code.
    """

    def fix_bugs(self, code):
        """
        Automatically identifies and fixes any bugs in the provided Python code.

        Args:
            code (str): The Python code to fix.

        Returns:
            str: The corrected version of the code with bugs fixed.
        """
        prompt = f"Automatically identify and fix any bugs in the following Python code. Provide the corrected version:\n\n{code}"
        return self._get_completion(prompt)


class UnitTestGenerator(BaseAssistant):
    """
    UnitTestGenerator generates unit tests for Python code.

    Methods:
        generate_tests(code): Generates unit tests for the provided Python code.
    """

    def generate_tests(self, code):
        """
        Generates unit tests for the provided Python code.

        Args:
            code (str): The Python code to generate unit tests for.

        Returns:
            str: The generated unit tests covering all functions and methods.
        """
        prompt = f"Generate unit tests for the following Python code. Ensure that all functions and methods are covered:\n\n{code}"
        return self._get_completion(prompt)
