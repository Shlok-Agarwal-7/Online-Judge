import shutil
import subprocess
import uuid
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from google import genai

from accounts.models import Profile

from .models import Problem


def normalize_output(text):
    return text.replace("\r\n", "\n").strip()


# A dedicated temporary directory for all execution-related files
TEMP_EXEC_DIR = Path("/tmp/online_judge/")


def set_limits(memory_limit_mb):
    """Sets memory limits for the child process."""
    try:
        import resource

        memory_bytes = memory_limit_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        resource.setrlimit(resource.RLIMIT_DATA, (memory_bytes, memory_bytes))
    except (ImportError, ValueError):
        pass


def compile_code(language, code_path, u_id):
    """Compiles the code and returns the path to the executable or errors."""
    compiled_dir = TEMP_EXEC_DIR / "compiled"
    compiled_dir.mkdir(parents=True, exist_ok=True)

    if language == "cpp":
        exec_path = compiled_dir / f"{u_id}.out"
        compile_cmd = ["g++", str(code_path), "-o", str(exec_path)]
        try:
            result = subprocess.run(
                compile_cmd, capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                return None, "Compilation Error: " + result.stderr
            return exec_path, None
        except subprocess.TimeoutExpired:
            return None, "Compilation Error: Timeout"
    elif language == "java":
        # Create a fresh directory for this submission
        class_dir = compiled_dir / u_id
        class_dir.mkdir(parents=True, exist_ok=True)

        # Always write the user’s code to Main.java
        java_file = class_dir / "Main.java"
        java_file.write_text(code_path.read_text())

        # Compile into class_dir
        compile_cmd = ["javac", "-d", str(class_dir), str(java_file)]
        try:
            result = subprocess.run(
                compile_cmd, capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                return None, "Compilation Error: " + result.stderr
            # Return a tuple (class_dir, classname)
            return (class_dir, "Main"), None
        except subprocess.TimeoutExpired:
            return None, "Compilation Error: Timeout"

    # elif language == "java":
        # For Java, the "executable" is the class name, and we need the directory path
        # return code_path, None
        # class_dir = code_path.parent
        # compile_cmd = ["javac", str(code_path)]
        # try:
        #     result = subprocess.run(
        #         compile_cmd, capture_output=True, text=True, timeout=10
        #     )
        #     if result.returncode != 0:
        #         return None, "Compilation Error: " + result.stderr
        #     # Return the directory containing the .class file
        #     return class_dir, None
        # except subprocess.TimeoutExpired:
        #     return None, "Compilation Error: Timeout"

    elif language == "py":
        # Python is interpreted, no compilation needed
        return code_path, None

    return None, "Unsupported language"


def execute_code(language, exec_path, u_id, input_data, time_limit, memory_limit):
    """Executes the code/compiled executable and returns the output."""
    input_dir = TEMP_EXEC_DIR / "input"
    output_dir = TEMP_EXEC_DIR / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    input_file_path = input_dir / f"{u_id}.txt"
    output_file_path = output_dir / f"{u_id}.txt"
    input_file_path.write_text(input_data)
    output_file_path.touch()

    run_cmd = []
    if language == "cpp":
        run_cmd = [str(exec_path)]
    elif language == "py":
        run_cmd = ["python", str(exec_path)]
    # elif language == "java":
    #     # class_name = f"{u_id}"
    #     run_cmd = [
    #         "java",
    #         "-Xms64m",
    #         "-Xmx64m",
    #         str(exec_path),
    #     ]
    elif language == "java":
        class_dir, cls = exec_path  # exec_path now is (Path, "Main")
        run_cmd = [
            "java",
            "-XX:+UnlockExperimentalVMOptions",
            "-Xms64m",
            "-Xmx64m",
            "-cp",
            str(class_dir),
            cls,
        ]

    try:
        with open(input_file_path, "r") as input_f, open(
            output_file_path, "w"
        ) as output_f:
            result = subprocess.run(
                run_cmd,
                stdin=input_f,
                stdout=output_f,
                stderr=subprocess.STDOUT,
                preexec_fn=lambda: set_limits(memory_limit),
                timeout=time_limit,
                text=True,
            )

        output_data = output_file_path.read_text()

        if result.returncode != 0:
            if "MemoryError" in output_data or result.returncode in [-9, 137]:
                return "Memory Limit Exceeded"
            print(output_data)
            return "RunTime Error: " + output_data

        return output_data

    except subprocess.TimeoutExpired:
        return "Time Limit Exceeded"
    except Exception as e:
        print(str(e))
        return "RunTime Error: " + str(e)
    finally:
        # Clean up input/output files for the current run
        input_file_path.unlink(missing_ok=True)
        output_file_path.unlink(missing_ok=True)


def run_code(language, code, input_data, time_limit=5, memory_limit=128):
    """Orchestrates a single run of code with custom input."""
    u_id = str(uuid.uuid4())
    code_dir = TEMP_EXEC_DIR / "code"
    code_dir.mkdir(parents=True, exist_ok=True)
    code_file_path = code_dir / f"{u_id}.{language}"
    code_file_path.write_text(code)

    exec_path, error = compile_code(language, code_file_path, u_id)

    if error:
        # Cleanup and return compilation error
        shutil.rmtree(code_dir, ignore_errors=True)
        return error

    output = execute_code(
        language, exec_path, u_id, input_data, time_limit, memory_limit
    )

    # Final cleanup
    if language in ["cpp"]:
        compiled_dir = TEMP_EXEC_DIR / "compiled"
        shutil.rmtree(compiled_dir, ignore_errors=True)
        # if language == "java":
        #     # remove .class file
        #      (code_dir / f"{u_id}.class").unlink(missing_ok=True)

    code_file_path.unlink(missing_ok=True)

    return output


def submit_code(language, code, problem_id):
    """Orchestrates a submission against all testcases."""
    problem = Problem.objects.get(id=problem_id)
    u_id = str(uuid.uuid4())

    code_dir = TEMP_EXEC_DIR / "code"
    code_dir.mkdir(parents=True, exist_ok=True)
    code_file_path = code_dir / f"{u_id}.{language}"
    code_file_path.write_text(code)

    # 1. Compile the code once
    exec_path, compile_error = compile_code(language, code_file_path, u_id)
    if compile_error:
        code_file_path.unlink(missing_ok=True)
        return {"verdict": compile_error}

    # 2. Run against all testcases
    verdict = "Accepted"
    for i, testcase in enumerate(problem.testcases.all(), 1):
        output = execute_code(
            language,
            exec_path,
            u_id,
            testcase.input,
            problem.time_limit,
            problem.memory_limit,
        )

        if normalize_output(output) != normalize_output(testcase.output):
            if "Time Limit Exceeded" in output:
                verdict = f"TLE on Testcase {i}"
            elif "Memory Limit Exceeded" in output:
                verdict = f"MLE on Testcase {i}"
            elif "RunTime Error" in output:
                verdict = f"Runtime Error on Testcase {i}"
            else:
                verdict = f"WA on Testcase {i}"
            break  # Stop on first failure

    # 3. Final Cleanup
    code_file_path.unlink(missing_ok=True)
    if language == "cpp":
        exec_path.unlink(missing_ok=True)
    # elif language == "java":
    #     # exec_path is a directory, and the .class file is inside it
    #     class_file = exec_path / f"{u_id}.class"
    #     class_file.unlink(missing_ok=True)

    return {"verdict": verdict}


def update_rank_on_point_increase(user_profile, old_points, new_points):
    affected_profiles = list(
        Profile.objects.filter(points__gte=old_points, points__lte=new_points)
        .exclude(pk=user_profile.pk)
        .order_by("-points", "user__username")
    )
    all_profiles = affected_profiles + [user_profile]
    all_profiles.sort(key=lambda p: (-p.points, p.user.username))

    min_rank = Profile.objects.filter(points__gt=new_points).count() + 1

    # Assign new ranks
    for i, profile in enumerate(all_profiles):
        profile.rank = min_rank + i

    Profile.objects.bulk_update(all_profiles, ["rank"])


def update_user_score_if_first_ac(user_id, problem_id):
    try:

        user = User.objects.get(id=user_id)
        problem = Problem.objects.get(id=problem_id)
        already_accepted = (
            problem.submissions.filter(verdict="Accepted", user=user)
            .exclude(verdict="Pending")
            .exists()
        )

        if already_accepted:
            return  # not first AC

        points = {"Easy": 25, "Medium": 50, "Hard": 100}
        earned = points.get(problem.difficulty, 0)
        profile = user.profile

        old_points = profile.points
        profile.points += earned
        profile.save()

        update_rank_on_point_increase(profile, old_points, profile.points)

    except (User.DoesNotExist, Problem.DoesNotExist):
        print("error in update scores")


import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")


def get_ai_hint(title, question):

    client = genai.Client(api_key=SECRET_KEY)

    prompt = f"""
            You are a helpful competitive programming assistant.

            The user is solving this problem:
            Title: {title}
            Description: {question}

            Give the user a **helpful hint** or idea (without giving away the full code or direct solution).
            Only give 1-2 short hints.
            Avoid spoilers. Just give nudges or ideas.
            """

    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)

    return response.text.strip()
