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

SUBCATEGORY_ICONS = {
    "Compiler"       : "⚙️",
    "Hall"           : "🧲",
    "Images"         : "📦",
    "Linear"         : "📏",
    "Rotativ"        : "🔄",
    "Sources"        : "🔗",
    "Shared Library" : "📚",
    "Template"       : "📄"
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
def get_repository_property(
                        _repository: str = "",
                            _property: str = "") -> str:
    '''
    @brief    Liest eine Custom Property eines Repositories aus.

    @param [in]    '_repository'    Aus diesem Repository soll ausgelesen werden
    @param [in]    '_property'      Diese Property wollen wir ausgelesen haben.

    @return  'String'    Repository Property.
    '''

    githubCommand = [
        "gh",
        "api",
        f"repos/{ORGANIZATION}/{_repository}"
    ]

    output = subprocess.check_output(githubCommand, text=True)

    property = (
        json.loads(output)
        .get("custom_properties", {})
        .get(_property, "")
    )
    
    return property

##
def get_repository_subcategory(
                        _repository: str = "",
                            _category: str = "") -> str:
    '''
    @brief    Ermittelt die Unterkategorie eines Repositories abhängig von
              dessen Hauptkategorie.

    @param [in]    '_repository'    Aus diesem Repository soll ausgelesen werden
    @param [in]    '_category'      Ermittle die Unterkategorien zu dieser
                                    Hauptkategorie.

    @return  'String'    Unterkategorie.
    '''

    subcategory = ""

    match _category:

        case "Firmware":
            subcategory = get_repository_property(_repository, "Sensortyp")

        case "Docker":
            subcategory = get_repository_property(_repository, "Docker")

        case "Jenkins":
            subcategory = get_repository_property(_repository, "Jenkins")

        case _:
            subcategory = "Allgemein"

    return subcategory

##
def group_repositories(
        _repositories: list[dict]) -> defaultdict[str, defaultdict[str, list[dict]]]:
    '''
    @brief    Gruppiert Repositories nach Kategorie und Untergruppe.

    @param [in]    '_repositories'    Diese Repos sollen alle gruppiert werden.

    @return  'defaultdict[str, list[dict]]'    Verzeichnis mit den gruppierten
                                               Repos
    '''

    grouped = defaultdict(
        lambda: defaultdict(list)
    )


    for repository in _repositories:

        category = get_repository_property(repository["name"], "Kategorie")

        if not category:
            category = "Sonstoges"

        subcategory = get_repository_subcategory(repository["name"], category)
        
        if not subcategory:
            subcategory = "Allgemein"

        grouped[category][subcategory].append(repository)

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
                f"    - 📜 {description}"
            )
        
        if homepage:
            lines.append(
                f"    - 🌐 [Produktseite]"
                f"({homepage})"
            )

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
        
        section = (
            f"## {icon} {category}\n\n"
        )

        subcategories = _groupedRepos.get(category, {})

        if not subcategories:
            section += "_Keine Einträge_\n\n"
        else:
            for subcategory in sorted(subcategories.keys()):

                subcategoryIcon = SUBCATEGORY_ICONS.get(subcategory, "📂")

                section += (
                    f"### {subcategoryIcon }{subcategory}\n\n"
                )

                section += create_repository_list(subcategories[subcategory])

                section += "\n\n"

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

    readmeFile = Path("profile/README.md")

    readmeFile.write_text(_content, encoding="utf-8")

##
def main():
    '''
    @brief    Hier lesen wir alle verfügbaren Repositories ein, die in unserem
              Organisations (Novotechnik) GitHub angelegt sind.
    
    @param  'None'

    @return "repos/Novotechnik/.github/profile/README.md"
    '''
    
    repositories = get_repositories(ORGANIZATION)

    groupedRepositories = group_repositories(repositories)

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
