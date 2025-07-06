from celery import shared_task
from .helpers import run_code,submit_code,update_user_score_if_first_ac
from .models import Submission

@shared_task
def run_code_task(language,code,input_data):
    output = run_code(language,code,input_data)
    return output

# @shared_task
# def submit_code_task(language,code,problem_id,submission_id):
#     result = submit_code(language,code,problem_id)
#     verdict = result.get("verdict") 
#     submission = Submission.objects.get(id = submission_id);
#     submission.verdict = verdict
#     submission.save()
#     user_id = submission.user.id

#     if(verdict == "Accepted"):
#         update_user_score_if_first_ac(user_id,problem_id)

#     return result["verdict"]

@shared_task
def submit_code_task(language, code, problem_id, submission_id):
    result = submit_code(language, code, problem_id)
    verdict = result.get("verdict")

    try:
        submission = Submission.objects.get(id=submission_id)
        submission.verdict = verdict
        submission.save()

        user_id = submission.user.id

        if verdict == "Accepted":
            update_user_score_if_first_ac(user_id, problem_id)

        return verdict

    except Submission.DoesNotExist:
        return f"Submission with ID {submission_id} not found."

