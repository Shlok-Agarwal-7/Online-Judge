# import re
# import resource
# import subprocess
# import uuid
# import signal
# from pathlib import Path

# from django.conf import settings

# def set_memory_limit(max_mem_mb):
#     # Convert MB to bytes
#     max_mem_bytes = max_mem_mb * 1024 * 1024

#     def set_limits():
#         # Set max address space (virtual memory)
#         resource.setrlimit(resource.RLIMIT_AS, (max_mem_bytes, max_mem_bytes))

#     return set_limits


# def run_code(language, code, input_data, u_ID=None):

#     project_dir = Path(settings.BASE_DIR)
#     directories = ["code", "input", "output", "compiled"]

#     for directory in directories:
#         dir_path = project_dir / directory

#         if not dir_path.exists():
#             dir_path.mkdir(parents=True, exist_ok=True)

#     code_dir = project_dir / "code"
#     input_dir = project_dir / "input"
#     output_dir = project_dir / "output"
#     compiled_dir = project_dir / "compiled"

#     if u_ID == None:
#         u_ID = str(uuid.uuid4())

#     code_file = f"{u_ID}.{language}"
#     input_file = f"{u_ID}.txt"
#     output_file = f"{u_ID}.txt"

#     code_file_path = code_dir / code_file
#     input_file_path = input_dir / input_file
#     output_file_path = output_dir / output_file

#     with open(code_file_path, "w") as code_file:
#         code_file.write(code)

#     with open(input_file_path, "w") as input_file:
#         input_file.write(input_data)

#     with open(output_file_path, "w") as output_file:
#         pass

#     memory_limit_fn = set_memory_limit(100)

#     try:
#         run_cmd = []
#         if language == "cpp":
#             exec_path = compiled_dir / f"{u_ID}.out"
#             compiled_cmd = ["g++", str(code_file_path), "-o", str(exec_path)]
#             compile_result = subprocess.run(
#                 compiled_cmd, capture_output=True, text=True
#             )

#             if compile_result.returncode != 0:
#                 output_file_path.write_text(
#                     "Compilation Error : \n" + compile_result.stderr
#                 )
#                 return output_file_path.read_text()

#             run_cmd = [str(exec_path)]

#         elif language == "py":
#             run_cmd = ["python", str(code_file_path)]

#         elif language == "java":
#             run_cmd = ["java", str(code_file_path)]

#         else:
#             return "Unsupported language"

#         with open(input_file_path, "r") as input_file:
#             with open(output_file_path, "w") as output_file:
#                 result = subprocess.run(
#                     run_cmd,
#                     stdin=input_file,
#                     stdout=output_file,
#                     stderr=output_file,
#                     preexec_fn=memory_limit_fn,
#                     timeout=3,
#                 )

#         if result.returncode < 0:
#             signal_killed = -result.returncode
#             if signal_killed == signal.SIGKILL:
#                 output_file_path.write_text("Memory Limit Exceeded")
#             elif signal_killed == signal.SIGSEGV:
#                 output_file_path.write_text("Segmentation Fault")
#             else:
#                 output_file_path.write_text(f"Terminated by signal {signal_killed}")
#         elif result.returncode != 0:
#             output_file_path.write_text("RunTime Error occurred")

#     except subprocess.TimeoutExpired:
#         output_file_path.write_text("Time Limit Exceeded")

#     except Exception as e:
#         output_file_path.write_text("RunTime Error : \n" + str(e))

#     with open(output_file_path, "r") as output_file:
#         output_data = output_file.read()

#     return output_data

import re
import subprocess
import uuid
from pathlib import Path

from django.conf import settings

from accounts.models import Profile

from .models import Problem


def run_code(langauge, code, input_data,u_ID = None):
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

    if(u_ID == None):
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

    try:
        run_cmd = []
        if langauge == "cpp":
            exec_path = compiled_dir / f"{u_ID}.out"
            compiled_cmd = ["g++", str(code_file_path), "-o", str(exec_path)]
            compile_result = subprocess.run(
                compiled_cmd, capture_output=True, text=True
            )

            if compile_result.returncode != 0:
                output_path.write("Compilation Error : \n" + compile_result.stderr)
                return output_path.read_text()

            run_cmd = [str(exec_path)]

        elif langauge == "py":
            run_cmd = ["python", str(code_file_path)]

        elif langauge == "java":
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

    pattern1 = r"^(Compilation Error) :"
    pattern2 = r"^(RunTime Error) :"
    i = 1

    for testcase in testcases:
        actual_output = run_code(language, code, testcase.input, u_ID)

        if actual_output == "Time Limit Exceeded":
            return {"verdict": f"TLE on Testcase {i}"}

        if re.match(pattern1, actual_output):
            return {"verdict": "Compilation Error"}

        if re.match(pattern2, actual_output):
            return {"verdict": f"WA on Testcase {i}"}

        if actual_output.strip() != testcase.output.strip():
            return {"verdict": f"WA on Testcase {i}"}

        i += 1

    return {"verdict": "Accepted"}


def update_rank_on_point_increase(user_profile, old_points, new_points):
    affected_profiles = list(
        Profile.objects.filter(points__gt=old_points, points__lte=new_points)
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
