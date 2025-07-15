import re
import subprocess
import uuid
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from google import genai

from accounts.models import Profile

from .models import Problem


def set_limits(MEMORY_LIMIT_MB=512):
    try:
        import resource

        memory_bytes = MEMORY_LIMIT_MB * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        resource.setrlimit(resource.RLIMIT_DATA, (memory_bytes, memory_bytes))
    except ImportError:
        pass


def run_code(langauge, code, input_data, u_ID=None, memory_limit=512, time_limit=3):
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

    code_file = f"{u_ID}.{langauge}"
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

    exec_path = None
    try:
        run_cmd = []
        if langauge == "cpp":
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

        elif langauge == "py":
            run_cmd = ["python", str(code_file_path)]

        elif langauge == "java":
            run_cmd = ["java", str(code_file_path)]

        else:
            return "Unsupported language"

        with open(input_file_path, "r") as input_file:
            with open(output_file_path, "w") as output_file:
                result = subprocess.run(
                    run_cmd,
                    stdin=input_file,
                    stdout=output_file,
                    stderr=output_file,
                    # preexec_fn=set_limits(memory_limit),
                    timeout=time_limit,
                )
        if result.returncode != 0:
            if result.returncode == -9 or result.returncode == 137:
                output_file_path.write_text("Memory Limit Exceeded")

    except subprocess.TimeoutExpired:
        output_file_path.write_text("Time Limit Exceeded")

    except Exception as e:
        output_file_path.write_text("RunTime Error : \n" + str(e))

    finally:
        with open(output_file_path, "r") as output_file:
            output_data = output_file.read()
        for path in [code_file_path, input_file_path, output_file_path]:
            try:
                if path and path.exists():
                    path.unlink()
            except Exception as cleanup_err:
                print(f"Error cleaning up {path}: {cleanup_err}")
        try:
            if exec_path != None:
                exec_path.unlink()
        except Exception as cleanup_err:
            print(f"Error cleaning up  : {cleanup_err}")

    return output_data


def submit_code(language, code, problem_id):

    u_ID = str(uuid.uuid4())

    testcases = Problem.objects.get(id=problem_id).testcases.all()
    time_limit = Problem.objects.get(id=problem_id).time_limit
    memory_limit = Problem.objects.get(id=problem_id).memory_limit

    pattern1 = r"^(Compilation Error) :"
    pattern2 = r"^(RunTime Error) :"
    i = 1

    for testcase in testcases:
        actual_output = run_code(
            language, code, testcase.input, u_ID, time_limit, memory_limit
        )

        print(actual_output)
        
        if actual_output == "Time Limit Exceeded":
            return {"verdict": f"TLE on Testcase {i}"}

        if actual_output == "Memory Limit Exceeded":
            return {"vedict": f"MLE on Testcase{i}"}

        if re.match(pattern1, actual_output):
            return {"verdict": "Compilation Error"}

        if re.match(pattern2, actual_output):
            print("here")
            return {"verdict": f"WA on Testcase {i}"}

        if actual_output.strip() != testcase.output.strip():
            print("here last")
            return {"verdict": f"WA on Testcase {i}"}

        i += 1

    return {"verdict": "Accepted"}


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
