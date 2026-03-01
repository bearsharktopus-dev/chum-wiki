"""
Convert character wiki pages to use collapsible spoiler sections.

Structure after conversion:
- VISIBLE: Title + blockquote, Infobox
- COLLAPSED: Background, Powers & Abilities, Personality, Relationships,
             each Arc Appearance (per-book), Trivia
- VISIBLE: Sources
"""

import os
import re

CHAR_DIR = "C:/Users/Jake/Documents/chum/chum-wiki/knowledge-base/characters"


def indent_block(text):
    """Indent content for use inside an admonition block.

    Non-empty lines get 4-space indent. Blank lines stay blank but
    consecutive blank lines are collapsed to one (to avoid breaking
    the admonition block).
    """
    lines = text.strip().split("\n")
    result = []
    prev_blank = False
    for line in lines:
        if line.strip():
            result.append("    " + line)
            prev_blank = False
        else:
            if not prev_blank:
                result.append("")
            prev_blank = True
    # Remove trailing blank lines
    while result and not result[-1].strip():
        result.pop()
    return "\n".join(result)


def make_collapsible(title, body, admonition_type="warning"):
    """Wrap content in a collapsed ??? admonition block."""
    body = body.strip()
    if not body:
        return ""
    indented = indent_block(body)
    return f'??? {admonition_type} "{title}"\n\n{indented}'


def process_arc_table(body):
    """Convert Arc Appearances table into per-book collapsible blocks."""
    lines = body.strip().split("\n")

    # Find table header, separator, and data rows
    found_header = False
    found_separator = False
    table_rows = []
    pre_table = []  # Any content before the table

    for line in lines:
        stripped = line.strip()
        if not found_header:
            if stripped.startswith("|") and "Book" in stripped and "Role" in stripped:
                found_header = True
                continue
            elif stripped:
                pre_table.append(line)
            continue
        if found_header and not found_separator:
            if re.match(r"^\|[\s\-:|]+\|$", stripped):
                found_separator = True
                continue
        if found_separator:
            if stripped.startswith("|"):
                table_rows.append(stripped)

    if not table_rows:
        # No parseable table - wrap the whole thing
        return "## Arc Appearances\n\n" + make_collapsible(
            "Arc Appearances", body
        )

    result = "## Arc Appearances\n"

    for row in table_rows:
        # Parse: | Book X: Title | Role | Key Events |
        cells = [c.strip() for c in row.split("|")]
        cells = [c for c in cells if c != ""]

        if len(cells) >= 3:
            book = cells[0]
            role = cells[1]
            # Rejoin remaining cells in case events text contained a |
            events = " | ".join(cells[2:])
        elif len(cells) == 2:
            book = cells[0]
            role = cells[1]
            events = ""
        else:
            continue

        result += f'\n??? warning "{book}"\n\n'
        result += f"    **Role:** {role}\n\n"
        if events:
            result += f"    {events}\n"

    return result


def process_powers(body):
    """Wrap Powers & Abilities in a collapsible, converting ### to bold."""
    body = body.strip()
    body = re.sub(r"^### (.+)$", r"**\1**", body, flags=re.MULTILINE)
    return make_collapsible("Powers & Abilities", body, "note")


def process_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by ## headers (not ### or deeper)
    parts = re.split(r"^(## (?!#).+)$", content, flags=re.MULTILINE)

    output_parts = []

    # First part: title + blockquote (before first ## header)
    output_parts.append(parts[0].rstrip())

    i = 1
    while i < len(parts) - 1:
        header = parts[i].strip()
        body = parts[i + 1]
        section_name = header[3:]  # Remove "## "

        if section_name == "Infobox":
            output_parts.append(header + "\n" + body.rstrip())
        elif section_name == "Sources":
            output_parts.append(header + "\n" + body.rstrip())
        elif section_name == "Arc Appearances":
            output_parts.append(process_arc_table(body))
        elif section_name == "Powers & Abilities":
            output_parts.append(process_powers(body))
        elif section_name in [
            "Background",
            "Personality",
            "Relationships",
            "Trivia",
        ]:
            output_parts.append(make_collapsible(section_name, body))
        else:
            # Unknown section - collapse it too with a note
            output_parts.append(make_collapsible(section_name, body, "note"))

        i += 2

    # Handle trailing content
    if len(parts) % 2 == 0 and len(parts) > 1:
        trailing = parts[-1].rstrip()
        if trailing:
            output_parts.append(trailing)

    return "\n\n".join(output_parts) + "\n"


# --- Main ---
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
