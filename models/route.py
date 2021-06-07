from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from utilities.db_manager import db, ma


class Route(db.Model):
    """
    This is a class that stores route data and used for
    interact with routes table.

    Attributes:
        user_id (int): The ID of the user that adds this route.
        route_command (str): The command that used to create this route.
        route_action (str): The action type of this route.
        _in: Ingress filter.
        in_on: Ingress filter on this device.
        _out: egress filter.
        out_on: egress filter on this device.
        to_IP (str): The IP address that will be the destination
        of traffic of this route.
        to_port (str): The port that this route will apply to it in the destination.
        from_IP (str): The address that will be the source 
        of traffic of this route.
        from_port (str): The port that this route will apply to it in the source.
        from_service_name (str):  The service_name that this route will apply to it in the source.
        protocol (str): The protocol that this route will apply to it.
        to_service_name (str):  The service_name that this route will apply to it in the destination.
        add_date (datetime): The date and time this route added. 
    """
    __tablename__ = "routes"
    id = Column(Integer, primary_key=True,
                nullable=False, unique=True)
    user_id = Column(Integer, nullable=False)
    route_command = Column(String, nullable=False)
    route_action = Column(String, nullable=False)
    _in = Column(String, nullable=True)
    in_on = Column(String, nullable=True)
    _out = Column(String, nullable=True)
    out_on = Column(String, nullable=True)
    to_IP = Column(String, nullable=True)
    to_port = Column(String, nullable=True)
    to_service_name = Column(String, nullable=True)
    from_IP = Column(String, nullable=True)
    from_port = Column(String, nullable=True)
    from_service_name = Column(String, nullable=True)
    protocol = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    add_date = Column(DateTime, nullable=False, default=datetime.now())


class RuleSchema(ma.Schema):
    """
    This is a class that used as custom serializers for Route Object.
    """
    class Meta:
        fields = ("id", "user_id", "route_command", "route_action",
                  "_in", "in_on", "_out", "out_on", "to_IP", "to_port", "to_service_name",
                  "from_IP", "from_port", "from_service_name",
                  "protocol", "comment", "add_date")


route_schema = RuleSchema()
routes_schema = RuleSchema(many=True)
