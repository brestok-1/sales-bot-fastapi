class MissingColumnsException(Exception):
    def __init__(self, missing_columns):
        self.missing_columns = missing_columns
        self.message = f"Missing required columns: {', '.join(missing_columns)}"
        super().__init__(self.message)


class InvalidRowException(Exception):
    def __init__(self, message: str, row: int):
        self.message = message
        self.row = row
