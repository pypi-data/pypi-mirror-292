import json
import logging
import os
import re
import time
from dataclasses import dataclass
from os import PathLike
from typing import Dict, List, Set, Tuple

from conan_report.git import (
    get_commit_hash,
    get_commit_tag,
    get_current_branch,
    get_remote_origin_url,
)
from conan_report.template_manager import get_local_template


@dataclass
class SoupInfo:
    name: str
    version: str
    url: str
    description: str
    license: List[str]
    required_by: List[str]
    requires: List[str]
    build_requires: List[str]


@dataclass
class ProjectDetails:
    remote_origin_url: str
    name: str
    hash: str
    tag: str
    current_branch: str
    report_time: str


def _get_project_details() -> ProjectDetails:
    remote_origin_url = get_remote_origin_url()
    name = remote_origin_url.split("/")[-1].replace(".git", "")
    hash = get_commit_hash()
    tag = get_commit_tag()
    current_branch = _get_branch_name()
    report_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return ProjectDetails(
        remote_origin_url=remote_origin_url,
        name=name,
        hash=hash,
        tag=tag,
        current_branch=current_branch,
        report_time=report_time,
    )


def _get_branch_name() -> str:
    ENV_BRANCH_NAME = "CI_COMMIT_REF_NAME"
    current_branch = get_current_branch()
    if current_branch:
        return current_branch

    # Get branch name from GitLab CI environment variable
    current_branch = os.environ.get(ENV_BRANCH_NAME)
    if current_branch:
        return current_branch

    logging.warning(
        f"Failed to get current branch name from both git and environment variable '{ENV_BRANCH_NAME}'"
    )
    return ""


#  TODO: Temporary solution to ignore lupin_ros2_interfaces
def _if_lupin_ros2_interfaces(soup: SoupInfo) -> bool:
    return "lupin_ros2_interfaces" in soup.name


def _split_name_version(value) -> Tuple[str, str]:
    parts = value.split("/")
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def _clean_soup_version(version: str) -> str:
    v = version.split("@")[0]
    return "" if "None" in v else v


def _format_soup_name_version(name_with_version: str) -> List[str]:
    name_version = name_with_version.split("/")
    if "conanfile.py" in name_version[0]:
        match = re.search(r"\blupin\w*", name_version[0])
        if match:
            format_name_version = (
                f"{match.group(0)}/{_clean_soup_version(name_version[1])}"
            )
    else:
        format_name_version = (
            f"{name_version[0]}/{_clean_soup_version(name_version[1])}"
        )
    return format_name_version.rstrip("/")


def _parse_soup_info(soup: Dict[str, str]) -> SoupInfo:
    name, version = _split_name_version(
        _format_soup_name_version(soup.get("display_name"))
    )

    url = soup.get("homepage", "")
    if not url:
        url = soup.get("url", "")

    required_by = [
        _format_soup_name_version(required) for required in soup.get("required_by", [])
    ]
    requires = [
        _format_soup_name_version(require) for require in soup.get("requires", [])
    ]

    build_requires = soup.get("build_requires", [])
    if build_requires:
        build_requires = [
            _format_soup_name_version(require) for require in build_requires
        ]

    return SoupInfo(
        name=name,
        version=version,
        url=url,
        description=soup.get("description"),
        license=soup.get("license"),
        required_by=required_by,
        requires=requires,
        build_requires=build_requires,
    )


def _find_project_dependencies(
    soups: List[SoupInfo], project_name: str
) -> Tuple[Set[str], Set[str], bool, bool]:
    project_dependencies: Set[str] = set()
    build_requires: Set[str] = set()
    found_project = False
    found_ros2_interfaces = False

    sorted_soups = sorted(
        soups, key=lambda soup: soup.name.startswith("lupin_"), reverse=True
    )
    for soup in sorted_soups:
        if soup.name == project_name:
            project_dependencies.update(soup.requires)
            build_requires.update(soup.build_requires)
            found_project = True
        elif _if_lupin_ros2_interfaces(soup):
            soups.remove(soup)
            logging.info("Found lupin_ros2_interfaces, removing from dependencies")
            found_ros2_interfaces = True
        if found_project and found_ros2_interfaces:
            break

    return project_dependencies, build_requires


def _classify_soups(
    soups: List[SoupInfo],
    project_dependencies: Set[str],
    build_requires: Set[str],
    project_name: str,
) -> Tuple[List[SoupInfo], List[SoupInfo]]:
    direct_soups = []
    indirect_soups = []

    for soup in soups:
        soup_identifier = f"{soup.name}/{soup.version}"
        if soup_identifier in project_dependencies:
            direct_soups.append(soup)
        elif soup_identifier not in build_requires and soup.name != project_name:
            indirect_soups.append(soup)
    logging.info(f"Direct dependencies found: {len(direct_soups)}")
    logging.info(f"Indirect dependencies found: {len(indirect_soups)}")
    return direct_soups, indirect_soups


def _classify_soups_by_dependency(
    soups: List[SoupInfo], project_name: str
) -> Tuple[List[SoupInfo], List[SoupInfo]]:
    project_dependencies, build_requires = _find_project_dependencies(
        soups, project_name
    )
    return _classify_soups(soups, project_dependencies, build_requires, project_name)


def _find_soups_info(json_file_path: PathLike) -> List[SoupInfo]:
    parsed_soups = []
    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            soups = json.load(f)
            for soup in soups:
                parsed_soups.append(_parse_soup_info(soup))
    except FileNotFoundError:
        logging.error(f"File not found: {json_file_path}")
        exit(1)
    except json.JSONDecodeError:
        logging.error(f"Failed to parse JSON file: {json_file_path}")
        exit(1)
    return parsed_soups


def generate_conan_report(json_file_path: PathLike) -> None:
    soups = _find_soups_info(json_file_path)
    project_details = _get_project_details()
    direct_soups, indirect_soups = _classify_soups_by_dependency(
        soups, project_details.name
    )

    args = {
        "project_details": project_details,
        "direct_soups": direct_soups,
        "indirect_soups": indirect_soups,
    }

    logging.info("Generating output from report template")
    j2_template = get_local_template()
    rendered_template = j2_template.render(**args)
    output_file = "conan_report.html"
    logging.info(f"Saving output to file {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(rendered_template)
