from sqlalchemy import Column, Integer, String
from utilities.db_manager import db, ma


class Service(db.Model):
    """
    This is a class that stores system network service data and used for
    interact with service table.

    Attributes:
        service_name (str): The name of the service.
        service_port (str): The port that the service uses.
        service_comment (str): Comment of the service.
    """
    __tablename__ = "services"
    id = Column(Integer, primary_key=True,
                nullable=False, unique=True)
    service_name = Column(String, nullable=False)
    service_port = Column(String, nullable=False)
    service_comment = Column(String, nullable=True)


class ServiceSchema(ma.Schema):
    """
    This is a class that used as custom serializers for Service Object.
    """
    class Meta:
        fields = ("id", "service_name", "service_port", "service_comment")


service_schema = ServiceSchema()
services_schema = ServiceSchema(many=True)
