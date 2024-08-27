import os
import re
import time
import tenacity
from notion_client import Client
from rich.console import Console
from utils.cli import spinner, pprint, edit
from notion_client.errors import HTTPResponseError

# The ID of the database you want to update
DAILY_DATABASE_ID = "fa06555b1ab64dcd89b1acb9723e7001"
EXERCISE_DATABASE_ID = "8986f69c2ff84735930a8e0939449178"
TIME_DATABASE_ID = "332b06374a1c4f479c9aac5a6d5760ba"
OLD_NOTES_DATABASE_ID = "1a2d73c1d4b24572a2f4531a6e060e62"
DOORKNOCKING_LEADS_DATABASE_ID = "3846d84c4a714ecaa312d1164425dd43"
CONTACTS_DATABASE_ID = "31e6a483d0614ef2a1d600ef1241c2f9"
DOOR_TO_DOOR_METRICS_DATABASE_ID = "522a4b019a1e460087a441cf249d0fa4"
STREAKS_DATABASE_ID = "6777abd70157469fa30a316f3429ed1d"
OBSTACLES_DATABASE_ID = "156f37a8da094f43bb8b949c52d4da3c"
SUPPLEMENTS_DATABASE_ID = "42e94d8024254678b35290f058ecf522"
NOTES_DATABASE_ID = "16626418faff4c1294676311e9bf1b04"
CLEANING_LEADS_ID = "bbd8c9206bb54b998148fd181b3a5947"
CLEANER_PAYROLL_ID = "d45044ad66b443f68c9b39c58bde139c"
CUSTOMER_DATABASE_ID = "bbd8c9206bb54b998148fd181b3a5947"
CLEANER_DATABASE_ID = "326dabd09eed4fabb7353319d60f03bc"
ADDRESS_DATABASE_ID = "bd043f70540447a1aef655b5f52b5dce"
BOOKING_DATABASE_ID = "a6a202c0227649ca909ae7ed1b558b6f"
FINANCIAL_PORTFOLIO_DATABASE_ID = "e1ea3c37b6b74d9e8d6c4ae812fa08bf"

# The ID of the page you want to use
TEMPLATE_PAGE_ID = "5164fcac9c6d4783931539e1f374208c"

# The ID of the user you want to use
BRIAN_ID = "31201b63-874d-4a6c-b887-3f0fb859d6e9"
HANNAH_ID = "29d561ef-f742-4a57-bb9c-ca6e3c8a9862"

# Initialize the Notion client with your integration token
notion = Client(auth=os.environ["NOTION_API_KEY"])


console = Console()


def open_notion_page(page_id: str):
    os.system(f"open -a 'Notion' https://www.notion.so/{page_id.replace('-', '')}")


@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
    retry=tenacity.retry_if_exception_type(HTTPResponseError),
)
def update_notion_page(page_id, **kwargs):
    with spinner("Updating Notion page..."):
        return notion.pages.update(page_id=page_id, **kwargs)


def parse_text(rich_text: list) -> str | None:
    if not rich_text:
        return ""

    plain_text = ""
    for text in rich_text:
        if text["type"] == "mention":
            id = text["mention"]["page"]["id"]
            page = get_page(id)
            name = parse_text(page["properties"]["Name"]["title"])
            plain_text += f"@{name}"
        else:
            plain_text += text["plain_text"]

    return plain_text


def parse_relation(relation: list[dict]):
    if not relation:
        return None

    id = relation[0]["id"]
    page = get_page(id)
    properties = page["properties"]
    return properties


def parse_multi_select(options: list[dict]):
    if "options" in options:
        options = options["options"]

    if not options:
        return None

    return [option["name"] for option in options]


def parse_formula(formula: dict):
    formula_type = formula["type"]
    if formula_type == "date":
        return formula["date"]["start"]
    elif formula_type == "number":
        return formula["number"]
    elif formula_type == "string":
        return formula["string"]
    elif formula_type == "checkbox":
        return formula["checkbox"]
    elif formula_type == "array":
        return formula["array"]
    elif formula_type == "people":
        return formula["people"]
    elif formula_type == "relation":
        return formula["relation"]
    else:
        raise ValueError(f"Unsupported formula type: {formula_type}")


@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
    retry=tenacity.retry_if_exception_type(HTTPResponseError),
)
def get_pages(database_id, **kwargs):
    with spinner("Querying Notion pages..."):
        next_cursor = None
        pages = []
        while True:
            try:
                response = notion.databases.query(
                    database_id,
                    **kwargs,
                    start_cursor=next_cursor if next_cursor else None,
                )

                pages += response["results"]
                next_cursor = response["next_cursor"]

                if not next_cursor:
                    break
            except HTTPResponseError as e:
                if e.status == 502:
                    # If the error is 502 error, wait and retry.
                    time.sleep(2)
                else:
                    console.print(f"[red]Error querying Notion database: {e}[/red]")
                    raise

    return pages


@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
    retry=tenacity.retry_if_exception_type(HTTPResponseError),
)
def get_database(database_id, **kwargs):
    with spinner("Retrieving Notion database..."):
        return notion.databases.retrieve(database_id, **kwargs)


@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
    retry=tenacity.retry_if_exception_type(HTTPResponseError),
)
def get_page(page_id: str, **kwargs):
    with spinner("Retrieving Notion page..."):
        return notion.pages.retrieve(page_id, **kwargs)


@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
    retry=tenacity.retry_if_exception_type(HTTPResponseError),
)
def get_page_property(page_id: str, property_id: str):
    with spinner("Retrieving Notion page property..."):
        return notion.pages.properties.retrieve(
            page_id=page_id, property_id=property_id
        )


@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
    retry=tenacity.retry_if_exception_type(HTTPResponseError),
)
def read_page_content(page_id: str):
    with spinner("Retrieving Notion page content..."):
        blocks = notion.blocks.children.list(block_id=page_id)
        blocks: list = blocks["results"]

    content = ""

    while blocks:
        block = blocks.pop(0)
        block_type = block["type"]
        has_children = block["has_children"]
        indentation_level = (
            block["indentation_level"] if "indentation_level" in block else 0
        )

        content += "\t" * indentation_level

        if block_type == "paragraph":
            text = parse_text(block["paragraph"]["rich_text"])
            content += f"{text}"
        elif block_type == "heading_1":
            text = parse_text(block["heading_1"]["rich_text"])
            content += f"# {text}"
        elif block_type == "heading_2":
            text = parse_text(block["heading_2"]["rich_text"])
            content += f"## {text}"
        elif block_type == "heading_3":
            text = parse_text(block["heading_3"]["rich_text"])
            content += f"### {text}"
        elif block_type == "bulleted_list_item":
            text = parse_text(block["bulleted_list_item"]["rich_text"])
            content += f"- {text}"
        elif block_type == "numbered_list_item":
            text = parse_text(block["numbered_list_item"]["rich_text"])
            content += f"1. {text}"
        elif block_type == "to_do":
            text = parse_text(block["to_do"]["rich_text"])
            content += f"[ ] {text}"
        elif block_type == "toggle":
            text = parse_text(block["toggle"]["rich_text"])
            content += f"**{text}**"

        content += "\n"

        if has_children:
            with spinner("Retrieving Notion page content..."):
                children = notion.blocks.children.list(block_id=block["id"])
                children: list = children["results"]

            for child in children:
                child["indentation_level"] = indentation_level + 1

            blocks = children + blocks

    return content


@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
    retry=tenacity.retry_if_exception_type(HTTPResponseError),
)
def write_page_content(page_id: str, content: str, after=None, append=False):
    # Convert content to blocks
    content_blocks = []
    block_with_children_index = None
    indentation_level = 0
    for line in content.split("\n"):
        # Count the number of tabs
        tabs = re.findall(r"^\t+", line)
        if tabs:
            tabs = len(tabs[0])
        else:
            tabs = 0

        # Remove tabs
        line = line.replace("\t", "")

        if line.startswith("# "):
            block = {
                "type": "heading_1",
                "heading_1": {"rich_text": [{"text": {"content": line.strip("# ")}}]},
            }
        elif line.startswith("## "):
            block = {
                "type": "heading_2",
                "heading_2": {"rich_text": [{"text": {"content": line.strip("## ")}}]},
            }
        elif line.startswith("### "):
            block = {
                "type": "heading_3",
                "heading_3": {"rich_text": [{"text": {"content": line.strip("### ")}}]},
            }
        elif line.startswith("- "):
            block = {
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"text": {"content": line.strip("- ")}}]
                },
            }
        elif re.match(r"^\d+\. ", line):
            block = {
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"text": {"content": re.sub(r"^\d+\. ", "", line)}}]
                },
            }
        elif line.startswith("[ ] "):
            block = {
                "type": "to_do",
                "to_do": {"rich_text": [{"text": {"content": line.strip("[ ] ")}}]},
            }
        elif line.startswith(">"):
            block = {
                "type": "toggle",
                "toggle": {"rich_text": [{"text": {"content": line.strip("> ")}}]},
            }
        else:
            block = {
                "type": "paragraph",
                "paragraph": {"rich_text": [{"text": {"content": line}}]},
            }

        if tabs > indentation_level:
            # If the indentation level is greater than the current indentation
            # level, add as a child of the previous block
            block_with_children_index = len(content_blocks) - 1
            block["parent_block_index"] = block_with_children_index
        elif block_with_children_index is not None and tabs == indentation_level:
            # If the indentation level is the same as the current indentation
            # level, add to the same parent block
            block["parent_block_index"] = block_with_children_index
        elif block_with_children_index is not None and tabs < indentation_level:
            # If the indentation level is less than the current indentation
            # level, break out of the current block
            block_with_children_index = None

        content_blocks.append(block)

        indentation_level = tabs

    # Add blocks with parents as children under the parent block
    for block in content_blocks:
        if "parent_block_index" in block:
            parent_block = content_blocks[block["parent_block_index"]]
            type = parent_block["type"]
            if "children" not in parent_block[type]:
                parent_block["has_children"] = True
                parent_block[type]["children"] = []

            block = block.copy()
            del block["parent_block_index"]
            parent_block[type]["children"].append(block)

    # Delete all blocks with parents
    content_blocks = [
        block for block in content_blocks if "parent_block_index" not in block
    ]

    # Write the blocks to the page
    with spinner("Writing Notion page content..."):
        if not append:
            blocks = notion.blocks.children.list(block_id=page_id)
            blocks: list = blocks["results"]

            # Delete all existing blocks
            for block in blocks:
                notion.blocks.delete(block["id"])

        notion.blocks.children.append(block_id=page_id, children=content_blocks)


@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
    retry=tenacity.retry_if_exception_type(HTTPResponseError),
)
def edit_page_content(page_id: str):
    content = read_page_content(page_id)
    content = edit(content, report=False)

    write_page_content(page_id, content)


@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
    retry=tenacity.retry_if_exception_type(HTTPResponseError),
)
def list_block_children(block_id, **kwargs):
    results = []
    has_more = True
    start_cursor = None

    with spinner("Querying Notion pages..."):
        while has_more:
            response = notion.blocks.children.list(
                block_id=block_id, start_cursor=start_cursor, **kwargs
            )
            results.extend(response["results"])
            has_more = response["has_more"]
            start_cursor = response["next_cursor"]

    return results


@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
    retry=tenacity.retry_if_exception_type(HTTPResponseError),
)
def add_page(
    parent_id: str,
    properties: dict,
    content: str = None,
    children: list = None,
):
    args = {
        "parent": {"database_id": parent_id},
        "properties": properties,
    }

    if children:
        args["children"] = children

    with spinner("Creating Notion page..."):
        page = notion.pages.create(**args)

    if content:
        write_page_content(page["id"], content)

    return page


@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
    retry=tenacity.retry_if_exception_type(HTTPResponseError),
)
def archive_page(page_id: str):
    with spinner("Archiving Notion page..."):
        return notion.pages.update(page_id=page_id, archived=True)
