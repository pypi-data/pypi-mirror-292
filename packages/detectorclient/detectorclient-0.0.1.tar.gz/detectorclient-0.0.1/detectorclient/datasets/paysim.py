from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.ext.declarative import declarative_base
from detectorclient.datasets import Dataset

Base = declarative_base()


class _PaySimModel(Base):
    __tablename__ = 'paysim'

    id = Column(Integer, primary_key=True, autoincrement=True)
    step = Column(Integer)
    type = Column(String(255))
    amount = Column(Numeric(16, 2))
    nameOrig = Column(String(255))
    oldbalanceOrg = Column(Numeric(16, 2))
    newbalanceOrig = Column(Numeric(16, 2))
    nameDest = Column(String(255))
    oldbalanceDest = Column(Numeric(16, 2))
    newbalanceDest = Column(Numeric(16, 2))
    isFraud = Column(Integer)
    isFlaggedFraud = Column(Integer)


class PaySimDataset(Dataset):
    def __init__(self):
        super().__init__(
            sql_alchemy_model=_PaySimModel,
            fraud_field='isFraud',
            amount_field='amount',
            step_field='step',
            hidden_fields=['id', 'step', 'isFraud', 'isFlaggedFraud']
        )