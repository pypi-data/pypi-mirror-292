from dataclasses import dataclass


@dataclass
class SalePriceEntry:
    id: str
    name: str
    value: int
    external_code: str

    def __repr__(self):
        return f"SalePriceEntry(id={self.id}, name={self.name}, value={self.value}, external_code={self.external_code})"


class SalePrices:
    def __init__(self, sale_prices_dict):
        self._attributes = {}
        for attribute_id, entry in sale_prices_dict.items():
            entry_with_id = {**entry, "id": attribute_id}
            external_code = entry['external_code']
            sale_price_entry = SalePriceEntry(**entry_with_id)
            setattr(self, external_code, sale_price_entry)
            self._attributes[external_code] = sale_price_entry

    @property
    def attributes(self):
        return list(self._attributes.keys())

    def get(self, external_code):
        return self._attributes.get(external_code, None)

    def __repr__(self):
        return f"SalePrices({', '.join(self.attributes)})"
