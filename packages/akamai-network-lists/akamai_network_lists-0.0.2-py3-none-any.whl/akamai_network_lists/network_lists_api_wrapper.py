import requests
from typing import Literal

class NetworkLists:
    def __init__(self, hostname):
        self.base_url = f"https://{hostname}/network-list/v2"

    def list_network_lists(self, session: requests.Session):
        url = f'{self.base_url}/network-lists'
        response = session.get(url)

        try:
            return response.json()["networkLists"]
        except:
            return response.json()

    def create_network_list(self, session: requests.Session, network_list_name: str, network_list_type: Literal["IP", "GEO"], network_list_elements: list[str], network_list_description: str = None, network_list_contract_id: str = None, network_list_group_id: int = None):
        url = f'{self.base_url}/network-lists'
        data = {
            "name": network_list_name,
            "type": network_list_type,
            "list": network_list_elements,
            "description": network_list_description,
            "contractId": network_list_contract_id,
            "groupId": network_list_group_id
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        response = session.post(url, json=data, headers=headers)

        return response.json()

    def get_network_list(self, session: requests.Session, network_list_id: str):
        url = f'{self.base_url}/network-lists/{network_list_id}'
        response = session.get(url)

        return response.json()