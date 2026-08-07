#!/usr/bin/env python3

## @package generate_readme.py #################################################
##
## @brief    Erzeugt die README.md, welche als Startseite/Overwiew unserers
##           Novotechnik GutHub dargestellt wird.
##
## @author   Robert Malleschitz
## @mail     robert.malleschitz@novotechnik.de
################################################################################

# ==============================================================================
# Imports
# ==============================================================================
import os
import json
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any

# ==============================================================================
# Variables
# ==============================================================================
CATEGORY_ORDER = [
    "Firmware",
    "Jenkins",
    "Docker",
    "Tools",
    "Extern",
    "Sonstiges",
    "Quality"
]

CATEGORY_ICONS = {
    "Firmware"  : "🚀",
    "Jenkins"   : "🤖",
    "Docker"    : "🐳",
    "Tools"     : "🛠️",
    "Extern"    : "🌐",
    "Sonstiges" : "📌",
    "Quality"   : "✔️"
}

ORGANIZATION = "Novotechnik"    #!< Entsprechend der GitHub Ogranisation.

# ==============================================================================
# Functions
# ==============================================================================
def get_repositories(_organization: str = "") -> list:
    '''
    @brief    Liest alle Repositories der übergebenen Organisation aus.

    @param [in]    '_organization'    Bezeichner, wie er auch in GitHub steht.

    @return  'JSON'    Enthält alle Repositories zur übergebenen (GitHub) Or-
                       ganisation.
    '''

    githubCommand = [
        "gh",
        "repo",
        "list",
        _organization,
        "--limit",
        "100",
        "--json",
        "name,description"
    ]

    output = subprocess.check_output(githubCommand, text=True)

    repos = json.loads(output)

    return repos

##
def get_repository_data(_repository: str = "") -> str:
    '''
    @brief    Liest die Repository Details aus.

    @param [in]    '_repository'    Aus diesem Repository soll ausgelesen werden
    
    @return  'String'    Repository Daten.
    '''

    githubCommand = [
        "gh",
        "api",
        f"repos/{ORGANIZATION}/{_repository}"
    ]

    output = subprocess.check_output(githubCommand, text=True)

    repoData = json.loads(output)
    
    return repoData

##
def group_repositories_by_category(_repositories: list[dict]) -> defaultdict[str, list[dict]]:
    '''
    @brief    Gruppiert Repositories anhand der Kategorie.

    @param [in]    '_repositories'    Diese Repos sollen alle gruppiert werden.

    @return  'defaultdict[str, list[dict]]'    Verzeichnis mit den gruppierten
                                               Repos
    '''

    grouped = defaultdict(list)


    for repository in _repositories:

        repoData = get_repository_data(repository["name"])

        category = (
            repoData
            .get("custom_properties", {})
            .get("Kategorie", "Sonstiges")
        )

        grouped[category].append(repoData)

    return grouped

##
def load_template() -> str:
    '''
    @brief    Lädt das README.md Template.

    @param  'None'

    @return  'String'    README.md Template
    '''

    readmeTemplate = Path("scripts/templates/README.md.template")

    template = readmeTemplate.read_text(encoding="utf-8")

    return template

##
def create_repository_list(_repositories: list[dict] | None = None) -> str:
    '''
    @brief    Aus einer Liste von GitHub-Repositories wird nun eine formatierte
              Markdown-Liste als String erzeugt

    @param [in]    '_repositories'    Wir wollen die Proberties dieses Repos 
                                      haben!
    
    return  'String'    In Form gebrachte Repository Darstellung.
    '''

    if _repositories is None:
        return ""

    lines = []

    for repository in sorted(
            _repositories,
            key=lambda repo: repo["name"].lower()
    ):
        name = repository["name"]

        description = repository.get("description", "")
        homepage    = repository.get("homepage", "")

        lines.append(
            f"- [{name}]"
            f"(https://github.com/{ORGANIZATION}/{name})"
        )

        if description:
            lines.append(
                f"  - {description}"
            )
        
        if homepage:
            lines.append(
                f"  -🌐 {homepage}"
            )

        lines.append("")

    repoList = "\n".join(lines)

    return repoList 

##
def render_template(
                _template: str,
                    _groupedRepos: defaultdict[str, list[dict]]) -> str:
    '''
    @brief    Ersetzt die Platzhalter im Template.

    @param [in]    '_template'        Diese Template wollen wir befüllen.
    @param [in]    '_groupedRepos'    Mit diesen gruppierten Repos wollen wir
                                      das Template befüllen.
    
    @return  'String'    Vorlage zur Darstellung in GitHub/Novotechnik/Overiew.
    '''

    overviewPage = _template

    for category in CATEGORY_ORDER:

        icon = CATEGORY_ICONS.get(category, "")
        
        placeholder = (
            "{{"
            + category.upper()
            + "}}"
        )

        repositories = _groupedRepos.get(category, [])
        
        section = (f"## {icon} {category}\n\n")

        if repositories:
            section += create_repository_list(repositories)
        else:
            section += "_Keine Einträge_"

        overviewPage = overviewPage.replace(placeholder, section)
    
    return overviewPage

##
def write_readme(_content: str = "") -> None:
    '''
    @brief    Schreibt die fertige REDME.md.

    @note     Diese muss zwingend unter 
              "https://github.com/Novotechnik/.github/tree/main/profile" liegen!

    @sideeffect    README.md wird überschrieben.

    @param [in]    '_content'    README.md wollen wir hiermit überschreiben.

    @return  'None'
    '''

    print(">>> Content = \n", _content)

    readmeFile = Path("profile/README.md")

    readmeFile.write_text(_content, encoding="utf-8")

    print(">>> readmeFile = \n", readmeFile.resolve())

##
def main():
    '''
    @brief    Hier lesen wir alle verfügbaren Repositories ein, die in unserem
              Organisations (Novotechnik) GitHub angelegt sind.
    
    @param  'None'

    @return "repos/Novotechnik/.github/profile/README.md"
    '''
    
    repositories = get_repositories(ORGANIZATION)

    groupedRepositories = group_repositories_by_category(repositories)

    template = load_template()

    githubOverviewPage = render_template(template, groupedRepositories)

    write_readme(githubOverviewPage)

# ==============================================================================
# Classes
# ==============================================================================

# ==============================================================================
# Script
# ==============================================================================

if __name__ == "__main__":
    main()
