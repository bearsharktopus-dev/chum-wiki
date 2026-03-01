"""
1. Uncollapse Background, Powers & Abilities, Personality, Relationships, Trivia
   back into normal ## sections (no dropdowns at all).
2. Remove the ## Sources section entirely.

Leaves Arc Appearances per-book collapsibles intact.
"""

import os
import re

CHAR_DIR = "C:/Users/Jake/Documents/chum/chum-wiki/knowledge-base/characters"

# Sections to uncollapse back to normal ## headers
UNCOLLAPSE = {
    "Background": "## Background",
    "Powers & Abilities": "## Powers & Abilities",
    "Personality": "## Personality",
    "Relationships": "## Relationships",
    "Trivia": "## Trivia",
}


def process_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    output = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check for ## Sources — skip entire section until next ## or EOF
        if line.strip() == "## Sources":
            i += 1
            # Skip everything in the Sources section
            while i < len(lines):
                # Stop if we hit another ## header (not ###)
                if re.match(r"^## (?!#)", lines[i]):
                    break
                i += 1
            continue

        # Check for collapsible blocks we want to uncollapse
        match = re.match(r'^(\?\?\?\+?\s+\w+\s+)"(.+)"$', line)
        if match:
            title = match.group(2)
            if title in UNCOLLAPSE:
                # Emit the normal ## header
                output.append(UNCOLLAPSE[title])
                output.append("")
                i += 1

                # Skip the blank line after ??? header
                while i < len(lines) and lines[i].strip() == "":
                    i += 1

                # Now un-indent the content (remove 4-space prefix)
                while i < len(lines):
                    l = lines[i]
                    # If line is indented (part of admonition content)
                    if l.startswith("    "):
                        output.append(l[4:])  # Remove 4-space indent
                        i += 1
                    elif l.strip() == "":
                        # Blank line — check if next line is still indented
                        if i + 1 < len(lines) and lines[i + 1].startswith("    "):
                            output.append("")
                            i += 1
                        else:
                            # End of admonition block
                            output.append("")
                            i += 1
                            break
                    else:
                        # Non-indented line — end of admonition
                        break

                # For Powers & Abilities: convert **bold** back to ### headers
                if title == "Powers & Abilities":
                    new_output = []
                    for ol in output:
                        converted = re.sub(r"^\*\*(.+)\*\*$", r"### \1", ol)
                        new_output.append(converted)
                    output = new_output

                continue

        output.append(line)
        i += 1

    # Clean up trailing whitespace and ensure single newline at end
    result = "\n".join(output)
    # Remove excessive trailing blank lines
    result = result.rstrip() + "\n"
    return result


if __name__ == "__main__":
    count = 0
    errors = []

    for filename in sorted(os.listdir(CHAR_DIR)):
        if filename.endswith(".md"):
            filepath = os.path.join(CHAR_DIR, filename)
            try:
                result = process_file(filepath)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(result)
                count += 1
                print(f"  OK: {filename}")
            except Exception as e:
                errors.append((filename, str(e)))
                print(f"  ERROR: {filename}: {e}")

    print(f"\nProcessed {count} files")
    if errors:
        print(f"Errors: {len(errors)}")
        for fn, err in errors:
            print(f"  {fn}: {err}")
