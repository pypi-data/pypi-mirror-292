import requests
from amoApi.amoEntities.lead import Lead
import json
from typing import List, Union
from amoApi.amoEntities.contact import Contact
from .serializers import LeadSerializer, ContactSerializer


class AmoClient:
    def __init__(self, token: str, url: str):
        self._auth(token, url)

    def _delete(self, method: str, headers: dict = None, body: Union[dict, list] = None) -> json:
        if body is None:
            body = {}
        if headers is None:
            headers = {}
        if not self._token:
            raise ValueError("Not authorized!")
        headers["Authorization"] = "Bearer " + self._token
        response = requests.delete(
            "https://" + self._project_url + ".amocrm.ru/api/v4/" + method,
            headers=headers,
            json=body,
        )
        response.raise_for_status()
        return response.json()

    def _get(self, method, headers: dict = None, parameters: dict = None) -> json:
        if headers is None:
            headers = {}
        if parameters is None:
            parameters = {}
        if not self._token:
            raise ValueError("Not authorized!")
        headers["Authorization"] = "Bearer " + self._token
        response = requests.get(
            "https://" + self._project_url + ".amocrm.ru/api/v4/" + method,
            headers=headers,
            params=parameters,
        )
        response.raise_for_status()
        return response.json()

    def _post(
        self, method: str, headers: dict = None, body: Union[dict, list] = None
    ) -> json:
        if body is None:
            body = {}
        if headers is None:
            headers = {}
        if not self._token:
            raise ValueError("Not authorized!")
        headers["Authorization"] = "Bearer " + self._token
        response = requests.post(
            "https://" + self._project_url + ".amocrm.ru/api/v4/" + method,
            headers=headers,
            json=body,
        )
        response.raise_for_status()
        return response.json()

    def _patch(self, method, headers=None, body=None) -> json:
        if headers is None:
            headers = {}
        if body is None:
            body = {}
        if not self._token:
            raise ValueError("Not authorized!")
        headers["Authorization"] = "Bearer " + self._token
        response = requests.patch(
            "https://" + self._project_url + ".amocrm.ru/api/v4/" + method,
            headers=headers,
            json=body,
        )
        response.raise_for_status()
        return response.json()

    def _auth(self, token: str, url: str) -> None:
        headers = {"Authorization": "Bearer " + token}
        response = requests.get(
            "https://" + url + ".amocrm.ru/api/v4/leads", headers=headers
        )
        response.raise_for_status()
        self._token = token
        self._project_url = url
        self._url = "https://" + url + ".amocrm.ru/api/v4/"

    def get_lead(self, lead_id: int, params: dict = None) -> Lead:
        if params is None:
            params = {}
        response = self._get("leads/" + str(lead_id), parameters=params)
        lead = Lead(self)
        lead.from_json(response)
        return lead

    def get_leads(self, params: dict = None) -> List[Lead]:
        if params is None:
            params = {}
        leads = []
        response_leads = self._get("leads", parameters=params)
        if len(response_leads) == 0:
            return leads
        for json_lead in response_leads["_embedded"]["leads"]:
            lead = Lead(self)
            lead.from_json(json_lead)
            leads.append(lead)
        return leads

    def complex_create_lead(
        self, body: dict = None, contacts: dict = None, fields: dict = None
    ) -> Lead:
        if body is None:
            body = [{}]
        if contacts is None:
            contacts = [{}]
        if fields is None:
            fields = [{}]
        body[0]["custom_fields_values"] = fields
        body[0]["_embedded"] = {}
        body[0]["_embedded"]["contacts"] = contacts
        headers = {"Authorization": "Bearer " + self._token}
        r = requests.post(self._url + "leads/complex", json=body, headers=headers)
        lead = Lead()
        lead.id = json.loads(r.text)[0]["id"]
        return lead

    def get_contact(self, contact_id: int, params: dict = None):
        if params is None:
            params = {}
        params["with"] = "leads"
        contact = Contact(self, self._get("contacts/" + str(contact_id), parameters=params))
        return contact

    def get_contacts(self, params: dict = None):
        if params is None:
            params = {}
        return [
            Contact(self, json_contact)
            for json_contact in self._get("contacts", parameters=params)["_embedded"][
                "contacts"
            ]
        ]

    def get_contact_links(
        self, contacts_id: List[int] = None, chats_id: List[str] = None
    ):
        params = {}
        if contacts_id is not None:
            params["contact_id"] = contacts_id
        if chats_id is not None:
            params["chat_id"] = chats_id
        return self._get("contacts/chats", parameters=params)

    def get_lead_links(self, lead_id):
        return self._get("/api/v4/leads/" + str(lead_id) + "/links")

    def create_lead(self, body: dict = None) -> Lead:
        if body is None:
            body = [{}]
        r = self._post("leads", body=body)
        lead = Lead(self)
        lead.from_json(r["_embedded"]["leads"][0])
        return lead

    def patch_lead(self, lead: Lead) -> json:
        body = lead.get_json()
        serializer = LeadSerializer(data=body)
        serializer.validate_data()
        return self._patch(
            "leads/" + str(lead.get_id()), body=serializer.get_validated_data()
        )

    def patch_contact(self, contact: Contact) -> json:
        body = contact.get_json()
        serializer = ContactSerializer(data=body)
        serializer.validate_data()
        return self._patch(
            "contacts/" + str(contact.get_id()), body=serializer.get_validated_data()
        )

    def add_lead_text_note(self, lead: Lead, text: str) -> None:
        body = [{}]
        body[0]["entity_id"] = lead.get_id()
        body[0]["note_type"] = "common"
        body[0]["params"] = {"text": text}
        self._post(method="leads/notes", body=body)

    def create_source(self, name: str, external_id: str):
        body = [{"name": name, "external_id": external_id}]
        return self._post("sources", body=body)

    def delete_source(self, source_id: int):
        body = [{"id": source_id}]
        return self._delete("sources", body=body)

    def get_sources(self):
        return self._get("sources")

    def get_users(self):
        from amoApi.amoEntities.user import User

        return [User(self, user_json) for user_json in self._get("users")["_embedded"]["users"]]

    def get_companies(self, params: dict = None):
        params = {} if params is None else params
        from amoApi.amoEntities.company import Company

        return [
            Company(self, json_company)
            for json_company in self._get("companies", parameters=params)["_embedded"][
                "companies"
            ]
        ]

    def get_company(self, company_id: int):
        from amoApi.amoEntities.company import Company

        return Company(self, self._get("companies/" + str(company_id)))

    def get_cfs(self, enity_type: str):
        from amoApi.amoEntities.custom_field import CustomField

        return [
            CustomField(self, cf)
            for cf in self._get(method=enity_type + "/custom_fields")["_embedded"][
                "custom_fields"
            ]
        ]

    def create_cf(self, custom_field, enity_type: str):
        body = custom_field.get_json()
        return self._post(method=enity_type + "/custom_fields", body=body)

    def get_pipelines(self):
        return self._get("leads/pipelines")
