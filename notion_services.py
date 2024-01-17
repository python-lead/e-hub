import os

from notion_client import Client
from pprint import pprint


def n_get(data, chained_keys):
    for key in chained_keys.split("."):
        try:
            if isinstance(data, list):
                data = data[int(key)]
            else:
                data = data[key]

        except (KeyError, TypeError, IndexError):
            return None

    return data


class NotionService:
    property_mapping = {
        "data": "properties.Data.title.0.plain_text",
        "type": "properties.Type.select.name",
        "completed": "properties.Completed.checkbox",
    }

    def __init__(self):
        self.notion_token = os.environ.get("NOTION_TOKEN")
        self.page_id = os.environ.get("NOTION_PAGE_ID")
        self.database_id = os.environ.get("NOTION_DATABASE_ID")

        self.client = Client(auth=self.notion_token)

    def get_page(self, page_id: str):
        return self.client.pages.retrieve(page_id)

    def read_page(self, page_id: str):
        page_response = self.get_page(page_id=page_id)

        pprint(page_response, indent=2)

    def get_db_info(self, database_id: str):
        return self.client.databases.retrieve(database_id=database_id)

    def get_db_data(self, database_id: str):
        return self.client.databases.query(database_id=database_id)

    def get_mapped_data(self, database_id: str, property_map: dict) -> list:
        results = []
        db_data = self.get_db_data(database_id=database_id)

        for row in db_data["results"]:
            data = {}

            for key, property_chain in property_map.items():
                value = n_get(row, property_chain)
                if value:
                    data[key] = value

            results.append(data)

        results.reverse()

        return results

    def get_e_display_data(self):
        return self.get_mapped_data(
            database_id=self.database_id, property_map=self.property_mapping
        )
