import typing as t

from hrflow_connectors.connectors.hrflow.warehouse import (
    HrFlowJobWarehouse,
    HrFlowProfileWarehouse,
)
from hrflow_connectors.connectors.recruitee.warehouse import (
    RecruiteeJobWarehouse,
    RecruiteeProfileWarehouse,
)
from hrflow_connectors.core import (
    ActionName,
    ActionType,
    BaseActionParameters,
    Connector,
    ConnectorAction,
    ConnectorType,
    WorkflowType,
)


def get_profile_cv_url(attachments: t.List[t.Dict]):
    cv_url = next(
        (attachment for attachment in attachments if attachment.get("type") == "resume")
    )["public_url"]
    return cv_url


def get_profile_links(urls: t.List[t.Dict]) -> t.List:
    profile_links = []
    social_links = []

    profile_links = [e["url"] for e in urls if e.get("type") == "from_resume"]
    social_links = [e["url"] for e in urls if e.get("type") != "from_resume"]

    return profile_links, social_links


def format_profile(hrflow_profile: t.Dict) -> t.Dict:
    hrflow_profile_info = hrflow_profile["info"]
    profile_links, social_links = get_profile_links(hrflow_profile_info["urls"])
    profile = dict(
        name=hrflow_profile_info["full_name"],
        remote_cv_url=get_profile_cv_url(hrflow_profile["attachments"]),
        emails=[hrflow_profile_info["email"]],
        phones=[hrflow_profile_info["phone"]],
        social_links=social_links,
        links=profile_links,
        cover_letter="",
        sources=[hrflow_profile["source"]["name"]],
    )
    return profile


def format_to_hrflow_profile(recruitee_profile: t.Dict) -> t.Dict:
    recruitee_educations = next(
        (
            field["values"]
            for field in recruitee_profile["fields"]
            if field["kind"] == "education"
        ),
        [],
    )

    recruitee__experiences = next(
        (
            field["values"]
            for field in recruitee_profile["fields"]
            if field["kind"] == "experience"
        ),
        [],
    )
    educations = [
        dict(
            school=education["school"],
            date_start=education["start_date"],
            date_end=education["end_date"],
            description=education["description"],
            title=education["major"],
        )
        for education in recruitee_educations
    ]
    experiences = [
        dict(
            company=experience["company"],
            date_start=experience["start_date"],
            date_end=experience["end_date"],
            description=experience["description"],
            title=experience["title"],
            location=dict(text=experience["location"], lat=None, lng=None),
        )
        for experience in recruitee__experiences
    ]

    recruitee_emails = recruitee_profile.get("emails", [])
    recruitee_phones = recruitee_profile.get("phones", [])
    email = recruitee_emails[0] if recruitee_emails else None
    phone = recruitee_phones[0] if recruitee_phones else None

    urls = [
        dict(url=url, type="from_resume")
        for url in recruitee_profile.get("social_links", [])
        + recruitee_profile.get("links", [])
    ]
    profile = dict(
        reference=str(recruitee_profile.get("id")),
        text=recruitee_profile.get("description"),
        info=dict(
            full_name=recruitee_profile.get("name"),
            email=email,
            phone=phone,
            urls=urls,
        ),
        educations=educations,
        experiences=experiences,
        attachments=[
            dict(
                type="resume",
                public_url=recruitee_profile.get("cv_original_url"),
                filename="original_cv",
            )
        ],
        source=dict(name=recruitee_profile.get("source")),
    )
    return profile


def get_tags(recruitee_job: t.Dict) -> t.List[t.Dict]:
    job = recruitee_job
    t = lambda name, value: dict(name=name, value=value)

    tags = [
        t("recruitee_category", job.get("category")),
        t("recruitee_department", job.get("department")),
        t("recruitee_options_cv", job.get("options_cv")),
        t("recruitee_options_cover_letter", job.get("options_cover_letter")),
        t("recruitee_experience", job.get("experience")),
        t("recruitee_education", job.get("education")),
        t("recruitee_employment_type", job.get("employment_type")),
        t("recruitee_remote_option", job.get("remote")),
        t("recruitee_candidates_count", job.get("candidates_count")),
        t(
            "recruitee_disqualified_candidates_count",
            job.get("disqualified_candidates_count"),
        ),
        t(
            "recruitee_qualified_candidates_count",
            job.get("qualified_candidates_count"),
        ),
        t("recruitee_hired_candidates_count", job.get("hired_candidates_count")),
    ]
    return tags


def get_ranges_float(recruitee_job: t.Dict) -> t.List[t.Dict]:
    t = lambda name, value_min, value_max, unit: dict(
        name=name, value_min=value_min, value_max=value_max, unit=unit
    )
    salary = recruitee_job.get("salary", {})
    ranges_float = [
        t(
            "working hours",
            recruitee_job.get("min_hours"),
            recruitee_job.get("max_hours"),
            "Hours per week",
        ),
        t(
            "salary per {}".format(salary.get("period")),
            salary.get("min"),
            salary.get("max"),
            salary.get("currency"),
        ),
    ]
    return ranges_float


def format_job(recruitee_job: t.Dict) -> t.Dict:
    sections = [
        dict(
            name="recruitee_job_requirements",
            title="Job Requirements",
            description=recruitee_job["requirements"],
        )
    ]
    job = dict(
        name=recruitee_job.get("title"),
        reference=str(recruitee_job.get("id")),
        created_at=recruitee_job.get("created_at"),
        updated_at=recruitee_job.get("updated_at"),
        location=dict(lat=None, lng=None, text=recruitee_job.get("location")),
        url=recruitee_job.get("url"),
        summary=recruitee_job.get("description"),
        sections=sections,
        tags=get_tags(recruitee_job),
        ranges_float=get_ranges_float(recruitee_job),
    )
    return job


Recruitee = Connector(
    name="Recruitee",
    type=ConnectorType.ATS,
    description="",
    url="https://recruitee.com/",
    actions=[
        ConnectorAction(
            name=ActionName.push_profile,
            trigger_type=WorkflowType.catch,
            description=(
                "Writes a profile from Hrflow.ai Source as a candidate on Recruitee via"
                " the API"
            ),
            parameters=BaseActionParameters.with_defaults(
                "WriteProfileActionParameters", format=format_profile
            ),
            origin=HrFlowProfileWarehouse,
            target=RecruiteeProfileWarehouse,
            action_type=ActionType.outbound,
        ),
        ConnectorAction(
            name=ActionName.pull_job_list,
            trigger_type=WorkflowType.pull,
            description=(
                "Retrieves all jobs via the ***Recruitee*** API and send them"
                " to a ***Hrflow.ai Board***."
            ),
            parameters=BaseActionParameters.with_defaults(
                "ReadJobsActionParameters", format=format_job
            ),
            origin=RecruiteeJobWarehouse,
            target=HrFlowJobWarehouse,
            action_type=ActionType.inbound,
        ),
        ConnectorAction(
            name=ActionName.pull_profile_list,
            trigger_type=WorkflowType.pull,
            description=(
                "Retrieves all profiles via the ***Recruitee*** API and send them"
                " to a ***Hrflow.ai Source***."
            ),
            parameters=BaseActionParameters.with_defaults(
                "ReadProfilesActionParameters", format=format_to_hrflow_profile
            ),
            origin=RecruiteeProfileWarehouse,
            target=HrFlowProfileWarehouse,
            action_type=ActionType.inbound,
        ),
    ],
)
