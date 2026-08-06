#!/usr/bin/env python3

## @package generate_readme.py ###################################################
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
# ==============================================================================
# Variables
# ==============================================================================
ogranization = "Novotechnik"    #!< Entsprechend der GitHub Ogranisation.
githubCheckoutCommand = ""

# ==============================================================================
# Functions
# ==============================================================================

# ==============================================================================
# Classes
# ==============================================================================

# ==============================================================================
# Script
# ==============================================================================

repos = subprocess.check_output([
    "gh",
    "repo",
    "organization",
    "--limit",
    "--json",
    "name"
])

categories = defaultdict(list)

for repo in repos:
    name = repo["name"]

    try:
        output = subprocess.check_output([
            "gh",
            "api",
            "f"repos/{orgranization}/{name}/properties/values"
        ])
        values = json.loads(output)
        category = "Sonstiges"

        for value in values:
            if "Kategorie" == value["property_name"]
                category = value["value"]
        categories[category].append(name)

    except Exception:
        categories["Sonstoges"].append(name)
      
with open("profile/README.md", "w") as readme:
    readme.write("# Novotechnik Repositories\n\n")

    for category in sorted(categories):
        readme.write(f"## {category}\n\n)

        for repo in sorted(categories[category]):
          readme.write(f"- https://gihtub.com/{organization}/{repo}\n")
        readme.write("\n")

if __name__ == "__main__":
    main()
