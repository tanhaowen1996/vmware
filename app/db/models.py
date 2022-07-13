
from datetime import datetime

from sqlalchemy import Column, BigInteger, String, PickleType, DateTime, func
from sqlalchemy_utils import generic_repr

from .database import Base


@generic_repr
class BaseModel(Base):
    __abstract__ = True
    created_on = Column(
        DateTime, default=datetime.utcnow, server_default=func.now()
    )
    updated_on = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=func.now(),
    )
    id = Column(BigInteger, primary_key=True, autoincrement=True)


class VM(BaseModel):
    __tablename__ = "vms"

    uuid = Column(String(64), nullable=False)
    name = Column(String(255), nullable=False)
    project_id = Column(String(64), nullable=False)
    hypervisor_uuid = Column(String(64), nullable=False)
    host = Column(String(255))
    cluster = Column(String(64))
    hostname = Column(String(64))
    ip = Column(String(64))
    power_state = Column(String(32))
    guest_id = Column(String(255))
    guest_full_name = Column(String(255))
    tags = Column(PickleType)

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        return {
            'uuid': self.uuid,
            'name': self.name,
            'project_id': self.project_id,
            'hypervisor_uuid': self.hypervisor_uuid,
            'host': self.host,
            'cluster': self.cluster,
            'hostname': self.hostname,
            'ip': self.ip,
            'power_state': self.power_state,
            'guest_id': self.guest_id,
            'guest_full_name': self.guest_full_name,
            'tags': self.tags,
        }
