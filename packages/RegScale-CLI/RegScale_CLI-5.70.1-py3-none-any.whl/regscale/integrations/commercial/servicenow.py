#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Integration of ServiceNow into RegScale CLI tool """

# standard python imports
import datetime
import os
import sys
from concurrent.futures import CancelledError, ThreadPoolExecutor, as_completed
from copy import deepcopy
from json import JSONDecodeError
from threading import Lock
from typing import List, Optional, Tuple, Union, Literal
from urllib.parse import urljoin

import click
import requests
from pathlib import Path
from rich.progress import track

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.api_handler import APIUpdateError
from regscale.core.app.utils.app_utils import (
    check_file_path,
    check_license,
    create_progress_object,
    compute_hashes_in_directory,
    error_and_exit,
    save_data_to,
    get_current_datetime,
)
from regscale.core.app.utils.regscale_utils import verify_provided_module
from regscale.core.app.utils.threadhandler import create_threads, thread_assignment
from regscale.models import regscale_id, regscale_module
from regscale.models.regscale_models import File, Issue

job_progress = create_progress_object()
logger = create_logger()
APP_JSON = "application/json"
HEADERS = {"Content-Type": APP_JSON, "Accept": APP_JSON}
INCIDENT_TABLE = "api/now/table/incident"
update_counter = []
update_issues = []
new_regscale_issues = []
updated_regscale_issues = []
URGENCY_MAP = {
    "High": "1",
    "Medium": "2",
    "Low": "3",
}


# Create group to handle ServiceNow integration
@click.group()
def servicenow():
    """Auto-assigns incidents in ServiceNow for remediation."""
    check_license()


####################################################################################################
#
# PROCESS ISSUES TO ServiceNow
# ServiceNow REST API Docs:
# https://docs.servicenow.com/bundle/paris-application-development/page/build/applications/concept
# /api-rest.html
# Use the REST API Explorer in ServiceNow to select table, get URL, and select which fields to
# populate
#
####################################################################################################
@servicenow.command()
@regscale_id()
@regscale_module()
@click.option(
    "--snow_assignment_group",
    type=click.STRING,
    help="RegScale will sync the issues for the record to this ServiceNow assignment group.",
    prompt="Enter the name of the project in ServiceNow",
    required=True,
)
@click.option(
    "--snow_incident_type",
    type=click.STRING,
    help="Enter the ServiceNow incident type to use when creating new issues from RegScale.",
    prompt="Enter the ServiceNow incident type",
    required=True,
)
def issues(
    regscale_id: int,
    regscale_module: str,
    snow_assignment_group: str,
    snow_incident_type: str,
):
    """Process issues to ServiceNow."""
    sync_snow_to_regscale(
        regscale_id=regscale_id,
        regscale_module=regscale_module,
        snow_assignment_group=snow_assignment_group,
        snow_incident_type=snow_incident_type,
    )


@servicenow.command(name="issues_and_attachments")
@regscale_id()
@regscale_module()
@click.option(
    "--snow_assignment_group",
    type=click.STRING,
    help="RegScale will sync the issues for the record to this ServiceNow assignment group.",
    prompt="Enter the name of the project in ServiceNow",
    required=True,
)
@click.option(
    "--snow_incident_type",
    type=click.Choice(["High", "Medium", "Low"], case_sensitive=False),
    help="Enter the ServiceNow incident type to use when creating new issues from RegScale.",
    prompt="Enter the ServiceNow incident type",
    required=True,
)
@click.option(
    "--sync_attachments",
    type=click.BOOL,
    help=(
        "Whether RegScale will sync the attachments for the issue "
        "in the provided ServiceNow assignment group and vice versa. Defaults to True."
    ),
    required=False,
    default=True,
)
def issues_and_attachments(
    regscale_id: int,
    regscale_module: str,
    snow_assignment_group: str,
    snow_incident_type: str,
    sync_attachments: bool = True,
):
    """Process issues to ServiceNow."""
    sync_snow_and_regscale(
        parent_id=regscale_id,
        parent_module=regscale_module,
        snow_assignment_group=snow_assignment_group,
        snow_incident_type=snow_incident_type.title(),
        sync_attachments=sync_attachments,
    )


@servicenow.command(name="sync_work_notes")
def sync_work_notes():
    """Sync work notes from ServiceNow to existing issues."""
    sync_notes_to_regscale()


def get_issues_data(reg_api: Api, url_issues: str) -> List[dict]:
    """
    Fetch the full issue list from RegScale

    :param Api reg_api: RegScale API object
    :param str url_issues: URL for RegScale issues
    :return: List of issues
    :rtype: List[dict]
    """
    logger.info("Fetching full issue list from RegScale.")
    issue_response = reg_api.get(url_issues)
    result = []
    if issue_response.status_code == 204:
        logger.warning("No existing issues for this RegScale record.")
    else:
        try:
            result = issue_response.json()
        except JSONDecodeError as rex:
            error_and_exit(f"Unable to fetch issues from RegScale.\\n{rex}")
    return result


def create_snow_incident(snow_api: Api, incident_url: str, snow_incident: dict) -> dict:
    """
    Create a new incident in ServiceNow

    :param Api snow_api: ServiceNow API object
    :param str incident_url: URL for ServiceNow incidents
    :param dict snow_incident: Incident data
    :return: Incident response
    :rtype: dict
    """
    result = {}
    try:
        response = snow_api.post(
            url=incident_url,
            headers=HEADERS,
            json=snow_incident,
        )
        if not response.raise_for_status():
            result = response.json()
    except requests.exceptions.RequestException as ex:
        logger.error("Unable to create incident %s in ServiceNow...\n%s", snow_incident, ex)
    return result


def sync_snow_to_regscale(
    regscale_id: int,
    regscale_module: str,
    snow_assignment_group: str,
    snow_incident_type: str,
) -> None:
    """
    Sync issues from ServiceNow to RegScale via API
    :param int regscale_id: ID # of record in RegScale to associate issues with
    :param str regscale_module: RegScale module to associate issues with
    :param str snow_assignment_group: Snow assignment group to filter for
    :param str snow_incident_type: Snow incident type to filter for
    :rtype: None
    """
    # initialize variables
    app = Application()
    reg_api = Api()
    verify_provided_module(regscale_module)
    config = app.config

    # Group related variables into a dictionary
    snow_config = {
        "reg_config": config,
        "url": config["snowUrl"],
        "user": config["snowUserName"],
        "pwd": config["snowPassword"],
        "reg_api": reg_api,
        "api": deepcopy(reg_api),
    }
    snow_config["api"].auth = (snow_config["user"], snow_config["pwd"])

    url_issues = urljoin(
        config["domain"],
        f"api/issues/getAllByParent/{str(regscale_id)}/{str(regscale_module).lower()}",
    )

    if issues_data := get_issues_data(reg_api, url_issues):
        check_file_path("artifacts")
        save_data_to(
            file=Path("./artifacts/existingRecordIssues.json"),
            data=issues_data,
        )
        logger.info(
            "Writing out RegScale issue list for Record # %s to the artifacts folder "
            + "(see existingRecordIssues.json).",
            regscale_id,
        )
        logger.info(
            "%s existing issues retrieved for processing from RegScale.",
            len(issues_data),
        )

        int_new, int_skipped = process_issues(
            issues_data,
            snow_config,
            snow_assignment_group,
            snow_incident_type,
        )

        logger.info(
            "%i new issue incidents opened in ServiceNow and %i issues already exist and were skipped.",
            int_new,
            int_skipped,
        )
    else:
        logger.warning("No issues found for this record in RegScale. No issues were processed.")


def create_snow_assignment_group(snow_assignment_group: str, snow_config: dict) -> None:
    """
    Create a new assignment group in ServiceNow or if one already exists,
    a 403 is returned from SNOW.

    :param str snow_assignment_group: ServiceNow assignment group
    :param dict snow_config: ServiceNow configuration
    :rtype: None
    """
    # Create a service now assignment group. The api will not allow me create dups
    snow_api = snow_config["api"]
    payload = {
        "name": snow_assignment_group,
        "description": "An automatically generated Service Now assignment group from RegScale.",
        "active": True,
    }
    url = urljoin(snow_config["url"], "api/now/table/sys_user_group")
    response = snow_api.post(
        url=url,
        headers=HEADERS,
        json=payload,
    )
    if response.status_code == 201:
        logger.info("ServiceNow Assignment Group %s created.", snow_assignment_group)
    elif response.status_code == 403:
        # I expect a 403 for a duplicate code already found
        logger.debug("ServiceNow Assignment Group %s already exists.", snow_assignment_group)
    else:
        error_and_exit(
            f"Unable to create ServiceNow Assignment Group {snow_assignment_group}. "
            f"Status code: {response.status_code}"
        )


def get_service_now_incidents(snow_config: dict, query: str) -> List[dict]:
    """
    Get all incidents from ServiceNow

    :param dict snow_config: ServiceNow configuration
    :param str query: Query string
    :return: List of incidents
    :rtype: List[dict]
    """
    snow_api = snow_config["api"]
    incident_url = urljoin(snow_config["url"], INCIDENT_TABLE)
    offset = 0
    limit = 500
    data = []

    while True:
        result, offset = query_incidents(
            api=snow_api,
            incident_url=incident_url,
            offset=offset,
            limit=limit,
            query=query,
        )
        data += result
        if not result:
            break

    return data


def process_issues(
    issues_data: List[dict],
    snow_config: dict,
    snow_assignment_group: str,
    snow_incident_type: str,
) -> Tuple[int, int]:
    """
    Process issues and create new incidents in ServiceNow

    :param List[dict] issues_data: List of issues
    :param dict snow_config: ServiceNow configuration
    :param str snow_assignment_group: ServiceNow assignment group
    :param str snow_incident_type: ServiceNow incident type
    :return: Number of new incidents created, plus number of skipped incidents
    :rtype: Tuple[int, int]
    """
    config = snow_config["reg_config"]
    int_new = 0
    int_skipped = 0
    # Need a lock for int_new
    lock = Lock()
    # Make sure the assignment group exists
    create_snow_assignment_group(snow_assignment_group, snow_config)

    with job_progress:
        with ThreadPoolExecutor(max_workers=10) as executor:
            if issues_data:
                task = job_progress.add_task(
                    f"[#f8b737]Syncing {len(issues_data)} RegScale issues to ServiceNow",
                    total=len(issues_data),
                )

            futures = [
                executor.submit(
                    create_incident,
                    iss,
                    snow_config,
                    snow_assignment_group,
                    snow_incident_type,
                    config,
                    False,
                    None,
                )
                for iss in issues_data
            ]
            for future in as_completed(futures):
                try:
                    snow_response = future.result()
                    with lock:
                        if snow_response:
                            iss = snow_response["originalIssue"]
                            int_new += 1
                            logger.debug(snow_response)
                            logger.info(
                                "SNOW Incident ID %s created.",
                                snow_response["result"]["sys_id"],
                            )
                            iss["serviceNowId"] = snow_response["result"]["sys_id"]
                            try:
                                Issue(**iss).save()
                            except APIUpdateError as ex:
                                logger.error(
                                    "Unable to update issue in RegScale: %s\n%s",
                                    iss,
                                    ex,
                                )
                        else:
                            int_skipped += 1
                        job_progress.update(task, advance=1)
                except CancelledError as e:
                    logger.error("Future was cancelled: %s", e)

    return int_new, int_skipped


def create_incident(
    iss: dict,
    snow_config: dict,
    snow_assignment_group: str,
    snow_incident_type: str,
    config: dict,
    attachments: dict,
    add_attachments: bool = False,
) -> Optional[dict]:
    """
    Create a new incident in ServiceNow

    :param dict iss: Issue data
    :param dict snow_config: ServiceNow configuration
    :param str snow_assignment_group: ServiceNow assignment group
    :param str snow_incident_type: ServiceNow incident type
    :param dict config: Application config
    :param dict attachments: Dict of attachments from RegScale and ServiceNow
    :param bool add_attachments: Sync attachments from RegScale to ServiceNow, defaults to False
    :return: Response dataset from ServiceNow or None
    :rtype: Optional[dict]
    """
    response = None
    if iss.get("serviceNowId", "") == "":
        snow_incident = {
            "description": iss["description"],
            "short_description": iss["title"],
            "assignment_group": snow_assignment_group,
            "due_date": iss["dueDate"],
            "comments": f"RegScale Issue #{iss['id']} - {config['domain']}/issues/form/{iss['id']}",
            "state": "New",
            "urgency": snow_incident_type,
        }
        # update state and closed_at if the RegScale issue is closed
        if iss["status"] == "Closed":
            snow_incident["state"] = "Closed"
            snow_incident["closed_at"] = iss["dateCompleted"]
        incident_url = urljoin(snow_config["url"], INCIDENT_TABLE)
        if response := create_snow_incident(snow_config["api"], incident_url, snow_incident):
            response["originalIssue"] = iss
            if add_attachments and attachments:
                compare_files_for_dupes_and_upload(
                    snow_issue=response["result"],
                    regscale_issue=iss,
                    snow_config=snow_config,
                    attachments=attachments,
                )
    return response


def map_regscale_to_snow_incident(
    regscale_issue: Union[dict, Issue], snow_assignment_group: str, snow_incident_type: str, config: dict
) -> dict:
    """
    Map RegScale issue to ServiceNow incident

    :param Union[dict, Issue] regscale_issue: RegScale issue to map to ServiceNow incident
    :param str snow_assignment_group: ServiceNow assignment group
    :param str snow_incident_type: ServiceNow incident type
    :param dict config: RegScale CLI Application configuration
    :return: ServiceNow incident data
    :rtype: dict
    """
    if isinstance(regscale_issue, Issue):
        regscale_issue = regscale_issue.model_dump()
    snow_incident = {
        "description": regscale_issue["description"],
        "short_description": regscale_issue["title"],
        "assignment_group": snow_assignment_group,
        "due_date": regscale_issue["dueDate"],
        "comments": f"RegScale Issue #{regscale_issue['id']} - {config['domain']}/issues/form/{regscale_issue['id']}",
        "state": "New",
        "urgency": snow_incident_type,
    }
    # update state and closed_at if the RegScale issue is closed
    if regscale_issue["status"] == "Closed":
        snow_incident["state"] = "Closed"
        snow_incident["closed_at"] = regscale_issue["dateCompleted"]
    return snow_incident


def sync_snow_and_regscale(
    parent_id: int,
    parent_module: str,
    snow_assignment_group: str,
    snow_incident_type: Literal["High", "Medium", "Low"],
    sync_attachments: bool = True,
) -> None:
    """
    Sync issues, bidirectionally, from ServiceNow into RegScale as issues

    :param int parent_id: ID # from RegScale to associate issues with
    :param str parent_module: RegScale module to associate issues with
    :param str snow_assignment_group: Assignment Group Name of the project in ServiceNow
    :param str snow_incident_type: Type of issues to sync from ServiceNow
    :param bool sync_attachments: Whether to sync attachments in RegScale & ServiceNow, defaults to True
    :rtype: None
    """
    app = check_license()
    api = Api()
    config = app.config
    snow_config = {
        "reg_config": config,
        "url": config["snowUrl"],
        "user": config["snowUserName"],
        "pwd": config["snowPassword"],
        "reg_api": api,
        "api": deepcopy(api),
        "incident_type": URGENCY_MAP.get(snow_incident_type, "Low"),
        "incident_group": snow_assignment_group,
    }
    snow_config["api"].auth = (snow_config["user"], snow_config["pwd"])

    # see if provided RegScale Module is an accepted option
    verify_provided_module(parent_module)
    # Make sure the assignment group exists
    create_snow_assignment_group(snow_assignment_group, snow_config)

    incidents = get_snow_incidents(snow_config=snow_config, query="&sysparm_display_value=true")
    (
        regscale_issues,
        regscale_attachments,
    ) = Issue.fetch_issues_and_attachments_by_parent(
        parent_id=parent_id,
        parent_module=parent_module,
        fetch_attachments=sync_attachments,
    )
    snow_attachments = get_snow_attachment_metadata(snow_config)
    attachments = {
        "regscale": regscale_attachments or {},
        "snow": snow_attachments or {},
    }

    if regscale_issues:
        # sync RegScale issues to SNOW
        if issues_to_update := sync_regscale_to_snow(
            regscale_issues=regscale_issues,
            snow_config=snow_config,
            config=config,
            sync_attachments=sync_attachments,
            attachments=attachments,
        ):
            with job_progress:
                # create task to update RegScale issues
                updating_issues = job_progress.add_task(
                    f"[#f8b737]Updating {len(issues_to_update)} RegScale issue(s) from ServiceNow...",
                    total=len(issues_to_update),
                )
                # create threads to analyze ServiceNow incidents and RegScale issues
                create_threads(
                    process=update_regscale_issues,
                    args=(
                        issues_to_update,
                        api,
                        updating_issues,
                    ),
                    thread_count=len(issues_to_update),
                )
                # output the final result
                logger.info(
                    "%i/%i issue(s) updated in RegScale.",
                    len(issues_to_update),
                    len(update_counter),
                )
    else:
        logger.info("No issues need to be updated in RegScale.")

    if incidents:
        sync_regscale_issues_to_snow(
            incidents=incidents,
            regscale_issues=regscale_issues,
            sync_attachments=sync_attachments,
            attachments=attachments,
            app=app,
            snow_config=snow_config,
            parent_id=parent_id,
            parent_module=parent_module,
        )
    else:
        logger.info("No incidents need to be analyzed from ServiceNow.")


def update_regscale_issues(args: Tuple, thread: int) -> None:
    """
    Function to compare ServiceNow incidents and RegScale issues

    :param Tuple args: Tuple of args to use during the process
    :param int thread: Thread number of current thread
    :rtype: None
    """
    # set up local variables from the passed args
    (
        regscale_issues,
        app,
        task,
    ) = args
    # find which records should be executed by the current thread
    threads = thread_assignment(thread=thread, total_items=len(regscale_issues))
    # iterate through the thread assignment items and process them
    for i in range(len(threads)):
        # set the issue for the thread for later use in the function
        issue = regscale_issues[threads[i]]
        # update the issue in RegScale
        issue = issue.save()
        logger.debug(
            "RegScale Issue %i was updated with the ServiceNow incident #%s.",
            issue.id,
            issue.serviceNowId,
        )
        update_counter.append(issue)
        # update progress bar
        job_progress.update(task, advance=1)


def get_snow_incidents(snow_config: dict, query: str = "") -> List[dict]:
    """
    Get all incidents from ServiceNow

    :param dict snow_config: ServiceNow Configuration object
    :param str query: Query string, defaults to ""
    :return: List of incidents
    :rtype: List[dict]
    """
    snow_api = snow_config["api"]
    incident_url = urljoin(snow_config["url"], INCIDENT_TABLE)
    offset = 0
    limit = 500
    data = []

    while True:
        result, offset = query_incidents(
            api=snow_api,
            incident_url=incident_url,
            offset=offset,
            limit=limit,
            query=query,
        )
        data += result
        if not result:
            break

    return data


def sync_regscale_to_snow(
    regscale_issues: list[Issue],
    snow_config: dict,
    config: dict,
    attachments: dict,
    sync_attachments: bool = True,
) -> list[Issue]:
    """
    Sync issues from RegScale to SNOW

    :param list[Issue] regscale_issues: list of RegScale issues to sync to SNOW
    :param dict snow_config: SNOW configuration
    :param dict config: RegScale CLI configuration
    :param dict attachments: Dict of attachments from RegScale and SNOW
    :param bool sync_attachments: Sync attachments from RegScale to SNOW, defaults to True
    :return: list of RegScale issues that need to be updated
    :rtype: list[Issue]
    """
    new_issue_counter = 0
    issuess_to_update = []
    with job_progress:
        # create task to create ServiceNow incidents
        creating_issues = job_progress.add_task(
            f"[#f8b737]Verifying {len(regscale_issues)} RegScale issue(s) exist in ServiceNow...",
            total=len(regscale_issues),
        )
        for issue in regscale_issues:
            # see if ServiceNow incident already exists
            if not issue.serviceNowId or issue.serviceNowId == "":
                new_issue = create_incident(
                    iss=issue.model_dump(),
                    snow_config=snow_config,
                    snow_assignment_group=snow_config["incident_group"],
                    snow_incident_type=snow_config["incident_type"],
                    config=config,
                    add_attachments=sync_attachments,
                    attachments=attachments,
                )
                # log progress
                new_issue_counter += 1
                # get the ServiceNow incident ID
                snow_id = new_issue["result"]["number"]
                # update the RegScale issue for the ServiceNow link
                issue.serviceNowId = snow_id
                # add the issue to the update_issues global list
                issuess_to_update.append(issue)
            job_progress.update(creating_issues, advance=1)
    # output the final result
    logger.info("%i new incident(s) opened in ServiceNow.", new_issue_counter)
    return issuess_to_update


def compare_files_for_dupes_and_upload(
    snow_issue: dict,
    regscale_issue: dict,
    snow_config: dict,
    attachments: dict,
) -> None:
    """
    Compare files for duplicates and upload them to ServiceNow and RegScale

    :param dict snow_issue: SNOW issue to upload the attachments to
    :param dict regscale_issue: RegScale issue to upload the attachments from
    :param dict snow_config: SNOW configuration
    :param dict attachments: Attachments from RegScale and ServiceNow
    :rtype: None
    """
    import tempfile

    api = Api()
    snow_uploaded_attachments = []
    regscale_uploaded_attachments = []
    with tempfile.TemporaryDirectory() as temp_dir:
        snow_dir, regscale_dir = download_issue_attachments_to_directory(
            directory=temp_dir,
            regscale_issue=regscale_issue,
            snow_issue=snow_issue,
            api=api,
            snow_config=snow_config,
            attachments=attachments,
        )
        snow_attachment_hashes = compute_hashes_in_directory(snow_dir)
        regscale_attachment_hashes = compute_hashes_in_directory(regscale_dir)

        upload_files_to_snow(
            snow_attachment_hashes=snow_attachment_hashes,
            regscale_attachment_hashes=regscale_attachment_hashes,
            snow_issue=snow_issue,
            snow_config=snow_config,
            regscale_issue=regscale_issue,
            snow_uploaded_attachments=snow_uploaded_attachments,
        )
        upload_files_to_regscale(
            snow_attachment_hashes=snow_attachment_hashes,
            regscale_attachment_hashes=regscale_attachment_hashes,
            regscale_issue=regscale_issue,
            api=api,
            regscale_uploaded_attachments=regscale_uploaded_attachments,
        )

    log_upload_results(regscale_uploaded_attachments, snow_uploaded_attachments, regscale_issue, snow_issue)


def download_snow_attachment(attachment: dict, snow_config: dict, save_dir: str) -> None:
    """
    Download an attachment from ServiceNow

    :param dict attachment: Attachment to download
    :param dict snow_config: SNOW configuration
    :param str save_dir: Directory to save the attachment in
    :rtype: None
    """
    snow_api = snow_config["api"]
    # check if the file_name has an extension
    if not Path(attachment["file_name"]).suffix:
        import mimetypes

        suffix = mimetypes.guess_extension(attachment["content_type"])
        attachment["file_name"] = attachment["file_name"] + suffix
    with open(os.path.join(save_dir, attachment["file_name"]), "wb") as file:
        res = snow_api.get(attachment["download_link"])
        if res.ok:
            file.write(res.content)
        else:
            logger.error("Unable to download %s from ServiceNow.", attachment["file_name"])


def upload_files_to_snow(
    snow_attachment_hashes: dict,
    regscale_attachment_hashes: dict,
    snow_issue: dict,
    snow_config: dict,
    regscale_issue: dict,
    snow_uploaded_attachments: list,
) -> None:
    """
    Upload files to ServiceNow

    :param dict snow_attachment_hashes: Dictionary of SNOW attachment hashes
    :param dict regscale_attachment_hashes: Dictionary of RegScale attachment hashes
    :param dict snow_issue: SNOW issue to upload the attachments to
    :param dict snow_config: SNOW configuration
    :param dict regscale_issue: RegScale issue to upload the attachments from
    :param list snow_uploaded_attachments: List of SNOW attachments that were uploaded
    :rtype: None
    """
    snow_api = snow_config["api"]
    upload_url = urljoin(snow_config["url"], "/api/now/attachment/file")

    for file_hash, file in regscale_attachment_hashes.items():
        if file_hash not in snow_attachment_hashes:
            with open(file, "rb") as in_file:
                path_file = Path(file)
                data = in_file.read()
                params = {
                    "table_name": "incident",
                    "table_sys_id": snow_issue["sys_id"],
                    "file_name": f"RegScale_Issue_{regscale_issue['id']}_{path_file.name}",
                }
                headers = {"Content-Type": File.determine_mime_type(path_file.suffix), "Accept": APP_JSON}
                response = snow_api.post(url=upload_url, headers=headers, data=data, params=params)
                if response.raise_for_status():
                    logger.error(
                        "Unable to upload %s to ServiceNow incident %s.",
                        path_file.name,
                        snow_issue["number"],
                    )
                else:
                    logger.debug(
                        "Uploaded %s to ServiceNow incident %s.",
                        path_file.name,
                        snow_issue["number"],
                    )
                    snow_uploaded_attachments.append(file)


def download_issue_attachments_to_directory(
    directory: str,
    regscale_issue: dict,
    snow_issue: dict,
    api: Api,
    snow_config: dict,
    attachments: dict,
) -> tuple[str, str]:
    """
    Function to download attachments from ServiceNow and RegScale issues to a directory

    :param str directory: Directory to store the files in
    :param dict regscale_issue: RegScale issue to download the attachments for
    :param dict snow_issue: SNOW issue to download the attachments for
    :param Api api: Api object to use for interacting with RegScale
    :param dict snow_config: SNOW configuration
    :param dict attachments: Dictionary of attachments from RegScale and ServiceNow
    :return: Tuple of strings containing the SNOW and RegScale directories
    :rtype: tuple[str, str]
    """
    # determine which attachments need to be uploaded to prevent duplicates by checking hashes
    snow_dir = os.path.join(directory, "snow")
    check_file_path(snow_dir, False)
    # download all attachments from ServiceNow to the snow directory in temp_dir
    for attachment in attachments["snow"].get(snow_issue.get("sys_id"), []):
        download_snow_attachment(attachment, snow_config, snow_dir)
    # get the regscale issue attachments
    regscale_issue_attachments = attachments["regscale"].get(regscale_issue["id"], [])
    # create a directory for the regscale attachments
    regscale_dir = os.path.join(directory, "regscale")
    check_file_path(regscale_dir, False)
    # download regscale attachments to the directory
    for attachment in regscale_issue_attachments:
        with open(os.path.join(regscale_dir, attachment.trustedDisplayName), "wb") as file:
            file.write(
                File.download_file_from_regscale_to_memory(
                    api=api,
                    record_id=regscale_issue["id"],
                    module="issues",
                    stored_name=attachment.trustedStorageName,
                    file_hash=(attachment.fileHash if attachment.fileHash else attachment.shaHash),
                )
            )
    return snow_dir, regscale_dir


def upload_files_to_regscale(
    snow_attachment_hashes: dict,
    regscale_attachment_hashes: dict,
    regscale_issue: dict,
    api: Api,
    regscale_uploaded_attachments: list,
) -> None:
    """
    Upload files to RegScale

    :param dict snow_attachment_hashes: Dictionary of SNOW attachment hashes
    :param dict regscale_attachment_hashes: Dictionary of RegScale attachment hashes
    :param dict regscale_issue: RegScale issue to upload the attachments to
    :param Api api: Api object to use for interacting with RegScale
    :param list regscale_uploaded_attachments: List of RegScale attachments that were uploaded
    :rtype: None
    :return: None
    """
    for file_hash, file in snow_attachment_hashes.items():
        if file_hash not in regscale_attachment_hashes:
            with open(file, "rb") as in_file:
                path_file = Path(file)
                if File.upload_file_to_regscale(
                    file_name=f"ServiceNow_attachment_{path_file.name}",
                    parent_id=regscale_issue["id"],
                    parent_module="issues",
                    api=api,
                    file_data=in_file.read(),
                ):
                    regscale_uploaded_attachments.append(file)
                    logger.debug(
                        "Uploaded %s to RegScale issue #%i.",
                        path_file.name,
                        regscale_issue["id"],
                    )
                else:
                    logger.warning(
                        "Unable to upload %s to RegScale issue #%i.",
                        path_file.name,
                        regscale_issue["id"],
                    )


def log_upload_results(
    regscale_uploaded_attachments: list, snow_uploaded_attachments: list, regscale_issue: dict, snow_issue: dict
) -> None:
    """
    Log the results of the upload process

    :param list regscale_uploaded_attachments: List of RegScale attachments that were uploaded
    :param list snow_uploaded_attachments: List of Snow attachments that were uploaded
    :param dict regscale_issue: RegScale issue that the attachments were uploaded to
    :param dict snow_issue: SNOW issue that the attachments were uploaded to
    :rtype: None
    """
    if regscale_uploaded_attachments and snow_uploaded_attachments:
        logger.info(
            "%i file(s) uploaded to RegScale issue #%i and %i file(s) uploaded to ServiceNow incident %s.",
            len(regscale_uploaded_attachments),
            regscale_issue["id"],
            len(snow_uploaded_attachments),
            snow_issue["number"],
        )
    elif snow_uploaded_attachments:
        logger.info(
            "%i file(s) uploaded to ServiceNow incident %s.",
            len(snow_uploaded_attachments),
            snow_issue["number"],
        )
    elif regscale_uploaded_attachments:
        logger.info(
            "%i file(s) uploaded to RegScale issue #%i.",
            len(regscale_uploaded_attachments),
            regscale_issue["id"],
        )


def sync_regscale_issues_to_snow(
    incidents: list[dict],
    regscale_issues: list[Issue],
    sync_attachments: bool,
    attachments: dict,
    app: "Application",
    snow_config: dict,
    parent_id: int,
    parent_module: str,
) -> None:
    """
    Sync incidents from ServiceNow to RegScale

    :param list[dict] incidents: List of SNOW incidents to sync to RegScale
    :param list[Issue] regscale_issues: List of RegScale issues to compare to SNOW Incidents
    :param bool sync_attachments: Sync attachments from ServieNow to RegScale, defaults to True
    :param dict attachments: Attachments from RegScale and ServiceNow
    :param Application app: RegScale CLI application object
    :param dict snow_config: ServiceNow configuration
    :param int parent_id: Parent record ID in RegScale
    :param str parent_module: Parent record module in RegScale
    :rtype: None
    """
    issues_closed = []
    with job_progress:
        creating_issues = job_progress.add_task(
            f"[#f8b737]Comparing {len(incidents)} ServiceNow incident(s)"
            f" and {len(regscale_issues)} RegScale issue(s)...",
            total=len(incidents),
        )
        create_threads(
            process=create_and_update_regscale_issues,
            args=(
                incidents,
                regscale_issues,
                snow_config,
                sync_attachments,
                attachments,
                app,
                parent_id,
                parent_module,
                creating_issues,
                job_progress,
            ),
            thread_count=len(incidents),
        )
        logger.info(
            f"Analyzed {len(incidents)} ServiceNow incidents(s), created {len(new_regscale_issues)} issue(s), "
            f"updated {len(updated_regscale_issues)} issue(s), and closed {len(issues_closed)} issue(s) in RegScale.",
        )


def create_and_update_regscale_issues(args: Tuple, thread: int) -> None:
    """
    Function to create or update issues in RegScale from ServiceNow

    :param Tuple args: Tuple of args to use during the process
    :param int thread: Thread number of current thread
    :rtype: None
    """
    # set up local variables from the passed args
    (
        incidents,
        regscale_issues,
        snow_config,
        add_attachments,
        attachments,
        app,
        parent_id,
        parent_module,
        task,
        progress,
    ) = args
    # find which records should be executed by the current thread
    threads = thread_assignment(thread=thread, total_items=len(incidents))
    # iterate through the thread assignment items and process them
    for i in range(len(threads)):
        snow_incident: dict = incidents[threads[i]]
        regscale_issue: Optional[Issue] = next(
            (issue for issue in regscale_issues if issue.serviceNowId == snow_incident["number"]), None
        )
        # see if the incident needs to be created in RegScale
        if not regscale_issue:
            # map the SNOW incident to a RegScale issue object
            issue = map_incident_to_regscale_issue(
                incident=snow_incident,
                parent_id=parent_id,
                parent_module=parent_module,
            )
            # create the issue in RegScale
            if regscale_issue := issue.create():
                logger.debug(
                    "Created issue #%i-%s in RegScale.",
                    regscale_issue.id,
                    regscale_issue.title,
                )
                new_regscale_issues.append(regscale_issue)
            else:
                logger.warning("Unable to create issue in RegScale.\nIssue: %s", issue.dict())
        elif snow_incident["state"].lower() == "closed" and regscale_issue.status not in ["Closed", "Cancelled"]:
            # update the status and date completed of the RegScale issue
            regscale_issue.status = "Closed"
            regscale_issue.dateCompleted = snow_incident["closed_at"]
            # update the issue in RegScale
            updated_regscale_issues.append(regscale_issue.save())
        elif regscale_issue:
            # update the issue in RegScale
            updated_regscale_issues.append(regscale_issue.save())

        if add_attachments and regscale_issue and snow_incident["sys_id"] in attachments["snow"]:
            # determine which attachments need to be uploaded to prevent duplicates by
            # getting the hashes of all SNOW & RegScale attachments
            compare_files_for_dupes_and_upload(
                snow_issue=snow_incident,
                regscale_issue=regscale_issue.model_dump(),
                snow_config=snow_config,
                attachments=attachments,
            )
        # update progress bar
        progress.update(task, advance=1)


def map_incident_to_regscale_issue(incident: dict, parent_id: int, parent_module: str) -> Issue:
    """
    Map a ServiceNow incident to a RegScale issue

    :param dict incident: ServiceNow incident to map to RegScale issue
    :param int parent_id: Parent record ID in RegScale
    :param str parent_module: Parent record module in RegScale
    :return: RegScale issue object
    :rtype: Issue
    """
    default_due_date = datetime.datetime.now() + datetime.timedelta(days=30)
    new_issue = Issue(
        title=incident["short_description"],
        description=incident["description"],
        dueDate=incident["due_date"] or default_due_date.strftime("%Y-%m-%d %H:%M:%S"),
        parentId=parent_id,
        parentModule=parent_module,
        serviceNowId=incident["number"],
        status="Closed" if incident["state"].lower() == "closed" else "Open",
        severityLevel=Issue.assign_severity(incident["priority"].split(" ")[-1]),
    )
    # correct the status if it is canceled
    if incident["state"].lower() == "canceled":
        new_issue.status = "Cancelled"
    if new_issue.status in ["Closed", "Cancelled"]:
        new_issue.dateCompleted = incident.get("closed_at", get_current_datetime())
    return new_issue


def get_snow_attachment_metadata(snow_config: dict) -> dict[str, list[dict]]:
    """
    Get attachments for a ServiceNow incident

    :param dict snow_config: ServiceNow's configuration object
    :return: Dictionary of attachments with table_sys_id as the key and the attachments as the value
    :rtype: dict[str, list[dict]]
    """
    snow_api = snow_config["api"]
    attachment_url = urljoin(snow_config["url"], "api/now/attachment")
    offset = 0
    limit = 500
    data = []
    sorted_data = {}

    while True:
        result, offset = query_incidents(
            api=snow_api,
            incident_url=attachment_url,
            offset=offset,
            limit=limit,
            query="&table_name=incident",
        )
        data += result
        if not result:
            break
    for item in data:
        key = item["table_sys_id"]
        if key in sorted_data:
            sorted_data[key].append(item)
        else:
            sorted_data[key] = [item]
    return sorted_data


def sync_notes_to_regscale() -> None:
    """
    Sync work notes from ServiceNow to existing issues

    :rtype: None
    """
    app = Application()
    reg_api = Api()
    # get secrets
    snow_url = app.config["snowUrl"]
    snow_user = app.config["snowUserName"]
    snow_pwd = app.config["snowPassword"]
    snow_api = deepcopy(reg_api)  # no need to instantiate a new config, just copy object
    snow_api.auth = (snow_user, snow_pwd)
    snow_config = {"url": snow_url, "api": snow_api}
    query = "&sysparm_query=GOTO123TEXTQUERY321=regscale"
    data = get_service_now_incidents(snow_config, query=query)
    process_work_notes(config=app.config, api=reg_api, data=data)


def process_work_notes(config: dict, api: Api, data: list) -> None:
    """
    Process and Sync the worknotes to RegScale

    :param dict config: Application config
    :param Api api: API object
    :param list data: list of data from ServiceNow to sync with RegScale
    :rtype: None
    """
    update_issues = []
    for dat in track(
        data,
        description=f"Processing {len(data):,} ServiceNow incidents",
    ):
        sys_id = str(dat["sys_id"])
        try:
            regscale_response = api.get(url=config["domain"] + f"/api/issues/findByServiceNowId/{sys_id}")
            if regscale_response.raise_for_status():
                logger.warning("Cannot find RegScale issue with a incident %s.", sys_id)
            else:
                logger.debug("Processing ServiceNow Issue # %s", sys_id)
                if work_item := dat["work_notes"]:
                    issue = regscale_response.json()[0]
                    if work_item not in issue["description"]:
                        logger.info(
                            "Updating work item for RegScale issue # %s and ServiceNow incident " + "# %s.",
                            issue["id"],
                            sys_id,
                        )
                        issue["description"] = (
                            f"<strong>ServiceNow Work Notes: </strong>{work_item}<br/>" + issue["description"]
                        )
                        update_issues.append(issue)
        except requests.HTTPError:
            logger.warning(
                "HTTP Error: Unable to find RegScale issue with ServiceNow incident ID of %s.",
                sys_id,
            )
    if len(update_issues) > 0:
        logger.info(update_issues)
        api.update_server(
            url=urljoin(config["domain"], "/api/issues"),
            message=f"Updating {len(update_issues)} issues..",
            json_list=update_issues,
        )
    else:
        logger.warning("No ServiceNow work items found, No RegScale issues were updated.")
        sys.exit(0)


def query_incidents(api: Api, incident_url: str, offset: int, limit: int, query: str) -> Tuple[list, int]:
    """
    Paginate through query results

    :param Api api: API object
    :param str incident_url: URL for ServiceNow incidents
    :param int offset: Used in URL for ServiceNow API call
    :param int limit: Used in URL for ServiceNow API call
    :param str query: Query string for ServiceNow API call
    :return: Tuple[Result data from API call, offset integer provided]
    :rtype: Tuple[list, int]
    """
    result = []
    offset_param = f"&sysparm_offset={offset}"
    url = urljoin(incident_url, f"?sysparm_limit={limit}{offset_param}{query}")
    logger.debug(url)
    response = api.get(url=url, headers=HEADERS)
    if response.status_code == 200:
        try:
            result = response.json().get("result", [])
        except JSONDecodeError as e:
            logger.error("Unable to decode JSON: %s\nResponse: %i: %s", e, response.status_code, response.text)
    else:
        logger.error(
            "Unable to query ServiceNow. Status code: %s, Reasone: %s",
            response.status_code,
            response.reason,
        )
    offset += limit
    logger.debug(len(result))
    return result, offset
