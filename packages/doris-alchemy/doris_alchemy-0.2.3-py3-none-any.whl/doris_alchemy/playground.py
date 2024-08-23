from datetime import datetime
import os
from pprint import pprint
from typing import Optional
from sqlalchemy import BigInteger, Column, DateTime, Double, Engine, Index, Integer, String, Table, Text, UniqueConstraint, create_engine, func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

from doris_alchemy.datatype import RANGE
from doris_alchemy.datatype import RANDOM
from doris_alchemy.orm_base import METADATA
from doris_alchemy.orm_base import DorisBaseMixin

USER = os.environ['DORIS_PROD_USER']
PWD = os.environ['DORIS_PROD_PWD']
HOST = '10.0.100.115'
PORT = '9030'
DB = 'test'

def make_eng() -> Engine:
    return create_engine(f"doris+mysqldb://{USER}:{PWD}@{HOST}:{PORT}/{DB}")


table = Table(
    'dummy_table_2',
    METADATA,
    Column('id', Integer),
    Column('name', String(64), nullable=False),
    Column('description', Text),
    Column('date', DateTime),
    
    # doris_unique_key=('id'),
    doris_partition_by=RANGE('id'),
    # doris_distributed_by=HASH('id'),
    doris_distributed_by = RANDOM(32),
    doris_properties={"replication_allocation": "tag.location.default: 1"},
    doris_autogen_primary_key=True
)


class Base(DorisBaseMixin, DeclarativeBase):
    metadata = METADATA
    doris_autogen_primary_key = True
    
    __table_args__ = {
        'mysql_charset': 'foobar'
    }
    
    last_updated:Mapped[datetime] = mapped_column(default=datetime.now,
                                                  onupdate=datetime.now,
                                                  server_default=func.current_timestamp())
    

# class Dummy(Base):
#     __tablename__ = 'dummy_two'
    
#     id:             Mapped[int] = mapped_column(Integer, primary_key=True)
#     name:           Mapped[str] = mapped_column(String(127))
#     description:    Mapped[str]
#     date:           Mapped[datetime]
    
#     __table_args__ = (
#         UniqueConstraint('id'),
#         {
#             'doris_properties': {"replication_allocation": "tag.location.default: 1"},
#             'comment': "Some table comment"
#         })
#     # doris_unique_key = 'id'
#     # doris_distributed_by = HASH('id')
#     # doris_distributed_by = RANDOM(32)
#     # doris_partition_by = RANGE('id', ('PARTITION p1 VALUES LESS THAN ("1000")'))
#     doris_autogen_primary_key = True


class ContractClid(Base):
    __tablename__ = 'ariba_contract_clids'
    
    item_number:Mapped[int]     = mapped_column(BigInteger, primary_key=True)
    contract_id:Mapped[str]     = mapped_column(String(15), primary_key=True)
    id:Mapped[str]              = mapped_column(String(15), primary_key=True)
    mpu_id:Mapped[Optional[int]]
    contract_item_number:Mapped[Optional[str]]
    type:Mapped[Optional[str]]
    subtype:Mapped[Optional[str]]
    
    short_name:Mapped[Optional[str]]
    trade_name:Mapped[Optional[str]]
    # nosology:Mapped[Optional[str]]
    delivery_deadline_date:Mapped[Optional[datetime]]
    last_modified_date: Mapped[datetime]
    supply_number:Mapped[Optional[str]]
    offer_cost:Mapped[Optional[float]] = mapped_column(Double)
    quantity:Mapped[Optional[int]]
    unit_of_measure:Mapped[Optional[str]]
    
    unit_price:Mapped[Optional[float]] = mapped_column(Double)
    
    classifier_code:Mapped[Optional[str]]
    classifier_name:Mapped[Optional[str]]
    add_classifier_code:Mapped[Optional[str]]
    add_classifier_name:Mapped[Optional[str]]
    
    __table_args__ = (
        UniqueConstraint('contract_id'),
    )


ROWS = [
    ('BMW', 'A car brand', datetime(2024, 1, 1)),
    ('Airbus', 'Construction bureau', datetime(2024, 2, 10)),
    ('Volvo', 'A car brand', datetime(2022, 12, 1, 10, 35))
]

def __mk_row(id :int, row: tuple[str, str, datetime]):
    return {
        'id': id,
        'name': row[0],
        'description': row[1],
        'date': row[2]
    }

if __name__ == '__main__':
    engine = make_eng()
    # pprint(Dummy.__table_args__)
    # try:
    #     Dummy.drop(engine)
    # except:
    #     print("Doesn't exist")
    # Dummy.create(engine)
    
    try:
        ContractClid.drop(engine)
    except:
        print("Doesn't exist")
    ContractClid.create(engine)
    
    pprint(ContractClid.__table_args__)
    
    
    # with Session(engine) as s:
    #     # print(engine.dialect.has_table(s.connection(), 'dummy_two'))
    #     vals = [__mk_row(i, ROWS[i]) for i in range(len(ROWS))]
    #     q = insert(Dummy)
    #     s.execute(q, vals)
    #     # s.execute(q)
    #     sel = select(Dummy)
    #     res = s.execute(sel)
    #     pprint(list(res))
    pass