class PriceRangeConverter:
    regex = r"\d+-\d+"

    def to_python(self, value):
        min_val, max_val = map(int, value.split("-"))
        return {"min": min_val, "max": max_val}

    def to_url(self, value):
        return f"{value['min']}-{value['max']}"


class StatusConverter:
    regex = "new|processing|completed|cancelled"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value
