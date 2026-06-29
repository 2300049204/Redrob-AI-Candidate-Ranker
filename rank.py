import json
import pandas as pd


def score_candidate(c):

    score = 0

    profile = c["profile"]
    signals = c["redrob_signals"]

    # --------------------------
    # Experience (25)
    # --------------------------

    exp = profile["years_of_experience"]

    if 5 <= exp <= 9:
        score += 25
    elif 4 <= exp < 5:
        score += 15
    elif 9 < exp <= 12:
        score += 10
    else:
        score -= 5

    # --------------------------
    # Title relevance (20)
    # --------------------------

    title = profile["current_title"].lower()

    good_titles = [
        "ai engineer",
        "ml engineer",
        "machine learning engineer",
        "search engineer",
        "recommendation engineer",
        "nlp engineer",
        "data scientist",
        "ranking engineer"
    ]

    for t in good_titles:
        if t in title:
            score += 20
            break

    # --------------------------
    # Skills relevance (35)
    # --------------------------

    skills = []

    for s in c["skills"]:
        skills.append(s["name"].lower())

    important_skills = {

        "python":10,
        "machine learning":10,
        "embeddings":8,
        "retrieval":8,
        "ranking":8,
        "llm":6,
        "nlp":6,
        "vector database":6,
        "recommendation system":6,
        "search":5,
        "deep learning":5
    }

    matched = 0

    for skill,weight in important_skills.items():

        if skill in skills:
            score += weight
            matched += 1

    # Need core AI skills

    core = [
        "python",
        "machine learning",
        "embeddings",
        "retrieval"
    ]

    core_count = 0

    for x in core:
        if x in skills:
            core_count += 1

    if core_count < 2:
        score -= 15

    # --------------------------
    # Behavioral signals (15)
    # --------------------------

    if signals["open_to_work_flag"]:
        score += 2

    score += signals["recruiter_response_rate"]*5

    score += signals["interview_completion_rate"]*5

    if signals["github_activity_score"]!=-1:
        score += signals["github_activity_score"]/20

    score += min(
        signals["saved_by_recruiters_30d"],
        5
    )

    # --------------------------
    # Penalties
    # --------------------------

    if signals["notice_period_days"]>60:
        score-=10

    if signals["recruiter_response_rate"]<0.3:
        score-=10

    if signals["interview_completion_rate"]<0.5:
        score-=10

    if signals["offer_acceptance_rate"]==0:
        score-=3

    return score


print("Loading candidates...")

candidates=[]

with open(
    "candidates.jsonl",
    "r",
    encoding="utf-8"
) as f:

    for line in f:

        if line.strip():

            candidates.append(
                json.loads(line)
            )

print(
    "Candidates loaded:",
    len(candidates)
)

# Score all candidates

for c in candidates:

    c["score"]=score_candidate(c)


# Sort

ranked=sorted(
    candidates,
    key=lambda x:x["score"],
    reverse=True
)


# Generate Top 100

top100=[]

for i,c in enumerate(
    ranked[:100],
    start=1
):

    profile=c["profile"]
    signals=c["redrob_signals"]

    skills=[
        s["name"].lower()
        for s in c["skills"]
    ]

    reason=[]

    exp=profile[
        "years_of_experience"
    ]

    reason.append(
        f"{exp} years relevant experience"
    )

    matched=[]

    for x in [

        "python",
        "machine learning",
        "embeddings",
        "retrieval",
        "ranking",
        "llm"

    ]:

        if x in skills:
            matched.append(x)

    if matched:

        reason.append(
            "skills: "
            + ", ".join(
                matched[:3]
            )
        )

    if signals[
        "open_to_work_flag"
    ]:

        reason.append(
            "actively looking"
        )

    if signals[
        "recruiter_response_rate"
    ]>0.7:

        reason.append(
            "high recruiter response"
        )

    if signals[
        "github_activity_score"
    ]>60:

        reason.append(
            "strong github activity"
        )

    top100.append({

        "candidate_id":
        c["candidate_id"],

        "rank":
        i,

        "score":
        round(
            c["score"],
            2
        ),

        "reasoning":
        "; ".join(reason)

    })


df=pd.DataFrame(
    top100
)

df.to_csv(
    "submission.csv",
    index=False
)

print(
    "submission.csv generated successfully"
)