class BaseSerializer:

    def __init__(self, data: dict):
        self.data = data
        self._validated_data = None

    def validate_data(self):
        self._validated_data = self.serialize_data()

    def serialize_data(self):
        return self.data

    def get_validated_data(self):
        if self._validated_data is None:
            raise ValueError("Data is not validated!")
        return self._validated_data
