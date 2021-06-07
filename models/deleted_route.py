from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from utilities.db_manager import db, ma


class DeletedRoute(db.Model):
    """
    This is a class that stores deleted route data and used for
    interact with deleted_route table.

    Attributes:
        adder_user_id (int): The ID of the user that adds this rule.
        deleter_user_id (int): The ID of the user that deletes this rule.
        rule_command (str): The command that used to create this rule.
        add_date (datetime): The date and time this rule added.
        delete_date (datetime): The date and time this rule deleted.
    """
    __tablename__ = "deleted_route"
    id = Column(Integer, primary_key=True,
                nullable=False, unique=True)
    adder_user_id = Column(Integer, nullable=False)
    deleter_user_id = Column(Integer, nullable=False)
    route_command = Column(String, nullable=False)
    add_date = Column(DateTime, nullable=False)
    delete_date = Column(DateTime, nullable=False, default=datetime.now())


class DeletedRouteSchema(ma.Schema):
    """
    This is a class that used as custom serializers for DeletedRule Object.
    """
    class Meta:
        fields = ("id", "adder_user_id", "deleter_user_id",
                  "route_command", "add_date", "delete_date")


deleted_route_schema = DeletedRouteSchema()
deleted_routes_schema = DeletedRouteSchema(many=True)
