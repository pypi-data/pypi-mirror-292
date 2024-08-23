from .base_serializer import BaseSerializer


class LeadSerializer(BaseSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def serialize_data(self):
        data = self.data
        for i in range(0, len(data.get("_embedded", {}).get("tags", []))):
            data["_embedded"]["tags"][i].pop("color")
        for i in range(0, len(data.get("_embedded", {}).get("contacts", []))):
            data["_embedded"]["contacts"][i].pop("_links")
        for i in range(0, len(data.get("custom_fields_values", []))):
            data["custom_fields_values"][i].pop("is_computed")
        return data
