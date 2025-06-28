import re
import subprocess
import uuid
from pathlib import Path

from django.conf import settings

from .models import Problem


def run_code(language, code, input_data, u_ID=None):
    project_dir = Path(settings.BASE_DIR)
    directories = ["code", "input", "output", "compiled"]

    for directory in directories:
        dir_path = project_dir / directory

        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)

    code_dir = project_dir / "code"
    input_dir = project_dir / "input"
    output_dir = project_dir / "output"
    compiled_dir = project_dir / "compiled"

    if u_ID == None:
        u_ID = str(uuid.uuid4())

    code_file = f"{u_ID}.{language}"
    input_file = f"{u_ID}.txt"
    output_file = f"{u_ID}.txt"

    code_file_path = code_dir / code_file
    input_file_path = input_dir / input_file
    output_file_path = output_dir / output_file

    with open(code_file_path, "w") as code_file:
        code_file.write(code)

    with open(input_file_path, "w") as input_file:
        input_file.write(input_data)

    with open(output_file_path, "w") as output_file:
        pass

    try:
        run_cmd = []
        if language == "cpp":
            exec_path = compiled_dir / f"{u_ID}.out"
            compiled_cmd = ["g++", str(code_file_path), "-o", str(exec_path)]
            compile_result = subprocess.run(
                compiled_cmd, capture_output=True, text=True
            )

            if compile_result.returncode != 0:
                output_file_path.write_text(
                    "Compilation Error : \n" + compile_result.stderr
                )
                return output_file_path.read_text()

            run_cmd = [str(exec_path)]

        elif language == "py":
            run_cmd = ["python", str(code_file_path)]

        elif language == "java":
            run_cmd = ["java", str(code_file_path)]

        else:
            return "Unsupported language"

        with open(input_file_path, "r") as input_file:
            with open(output_file_path, "w") as output_file:
                subprocess.run(
                    run_cmd,
                    stdin=input_file,
                    stdout=output_file,
                    stderr=output_file,
                    timeout=3,
                )
    except subprocess.TimeoutExpired:
        output_file_path.write_text("Time Limit Exceeded")

    except Exception as e:
        output_file_path.write_text("RunTime Error : \n" + str(e))

    with open(output_file_path, "r") as output_file:
        output_data = output_file.read()

    return output_data


def submit_code(language, code, problem_id):

    u_ID = str(uuid.uuid4())

    testcases = Problem.objects.get(id=problem_id).testcases.all()

    pattern = r"^(Compilation Error|RunTime Error) :"
    i = 1

    for testcase in testcases:
        actual_output = run_code(language, code, testcase.input, u_ID)

        if actual_output == "Time Limit Exceeded":
            return {"verdict": f"TLE on Testcase {i}"}

        if re.match(pattern, actual_output):
            return {"verdict": f"WA on Testcase {i}"}
        if actual_output.strip() != testcase.output.strip():
            return {"verdict": f"WA on Testcase {i}"}

        i += 1

    return {"verdict": "Accepted"}
