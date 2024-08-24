import requests
from typing import Literal


class NetworkLists:
    def __init__(self, hostname):
        self.base_url = f"https://{hostname}/network-list/v2"

    def list_network_lists(self, session: requests.Session):
        url = f"{self.base_url}/network-lists"
        response = session.get(url, headers={"Accept": "application/json"}, timeout=5)

        print(response.json())

        try:
            return response.json()["networkLists"]
        except:
            return response.json()

    def create_network_list(
        self,
        session: requests.Session,
        network_list_name: str,
        network_list_type: Literal["IP", "GEO"],
        network_list_elements: list[str],
        network_list_description: str = None,
        network_list_contract_id: str = None,
        network_list_group_id: int = None,
    ):
        url = f"{self.base_url}/network-lists"
        data = {
            "name": network_list_name,
            "type": network_list_type,
            "list": network_list_elements,
            "description": network_list_description,
            "contractId": network_list_contract_id,
            "groupId": network_list_group_id,
        }
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        response = session.post(url, json=data, headers=headers)

        return response.json()

    def get_network_list(self, session: requests.Session, network_list_id: str):
        url = f"{self.base_url}/network-lists/{network_list_id}"
        response = session.get(url)

        return response.json()

    def delete_network_list(self, session: requests.Session, network_list_id: str):
        url = f"{self.base_url}/network-lists/{network_list_id}"
        response = session.delete(url)

        return response.json()

    def update_network_list(
        self,
        session: requests.Session,
        network_list_id: str,
        network_list_type: Literal["IP", "GEO"],
        network_list_elements: list[str],
        network_list_sync_point: int,
        network_list_description: str = None,
        extended: bool = False,
        include_elements: bool = True,
    ):
        url = f"{self.base_url}/network-lists/{network_list_id}"
        if extended:
            url += f"?extended={extended}"
        if include_elements:
            url += f"&includeElements={include_elements}"
        data = {
            "type": network_list_type,
            "list": network_list_elements,
            "syncPoint": network_list_sync_point,
        }
        if network_list_description:
            data["description"] = network_list_description
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        response = session.put(url, json=data, headers=headers)

        return response.json()

    def append_network_list(
        self,
        session: requests.Session,
        network_list_id: str,
        network_list_elements: list[str],
    ):
        url = f"{self.base_url}/network-lists/{network_list_id}/append"
        data = {"list": network_list_elements}
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        response = session.post(url, json=data, headers=headers)

        return response.json()

    def update_network_list_details(
        self,
        session: requests.Session,
        network_list_id: str,
        network_list_name: str,
        network_list_description: str = None,
    ):
        url = f"{self.base_url}/network-lists/{network_list_id}/details"
        data = {
            "name": network_list_name,
        }
        if network_list_description:
            data["description"] = network_list_description
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        response = session.put(url, json=data, headers=headers)

        return response.json()

    def remove_network_list_element(
        self,
        session: requests.Session,
        network_list_id: str,
        network_list_element: str,
    ):
        url = f"{self.base_url}/network-lists/{network_list_id}/elements?element={network_list_element}"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        response = session.delete(url, headers=headers)

        return response.json()

    def add_network_list_element(
        self,
        session: requests.Session,
        network_list_id: str,
        network_list_element: str,
    ):
        url = f"{self.base_url}/network-lists/{network_list_id}/elements?element={network_list_element}"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        response = session.put(url, headers=headers)

        return response.json()

    def activate_network_list(
        self,
        session: requests.Session,
        network_list_id: str,
        environment: Literal["STAGING", "PRODUCTION"],
        comments: str = None,
        notification_recipients: list[str] = None,
        siebel_ticket_id: str = None,
    ):
        url = f"{self.base_url}/network-lists/{network_list_id}/environments/{environment}/activate"
        body = {}
        if comments:
            body["comments"] = comments
        if notification_recipients:
            body["notificationRecipients"] = notification_recipients
        if siebel_ticket_id:
            body["siebelTicketId"] = siebel_ticket_id
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        response = session.post(url, json=body, headers=headers)

        return response.json()

    def get_activation_status(
        self,
        session: requests.Session,
        network_list_id: str,
        environment: Literal["STAGING", "PRODUCTION"],
    ):
        url = f"{self.base_url}/network-lists/{network_list_id}/environments/{environment}/status"
        response = session.get(url)

        return response.json()

    def get_activation_snapshot(
        self,
        session: requests.Session,
        network_list_id: str,
        sync_point: int,
        extended: bool = False,
    ):
        url = f"{self.base_url}/network-lists/{network_list_id}/sync-points/{sync_point}/history"
        if extended:
            url += f"?extended={extended}"
        response = session.get(url)

        return response.json()
