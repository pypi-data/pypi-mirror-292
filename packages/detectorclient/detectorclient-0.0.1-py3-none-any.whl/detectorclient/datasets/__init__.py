from typing import Any


class Dataset:
    def __init__(
        self,
        sql_alchemy_model: Any,
        fraud_field: str,
        amount_field: str,
        step_field: str,
        hidden_fields: list[str]
    ):
        self.sql_alchemy_model = sql_alchemy_model
        self.fraud_field = fraud_field
        self.amount_field = amount_field
        self.step_field = step_field
        self.hidden_fields = hidden_fields
