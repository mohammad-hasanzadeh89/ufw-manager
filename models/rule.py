from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from utilities.db_manager import db, ma


class Rule(db.Model):
    """
    This is a class that stores rule data and used for
    interact with rules table.

    Attributes:
        user_id (int): The ID of the user that adds this rule.
        rule_command (str): The command that used to create this rule.
        rule_action (str): The action type of this rule.
        in_out: Ingress or egress filter.
        to_IP (str): The IP address that will be the destination
        of traffic of this rule.
        to_port (str): The port that this rule will apply to it in the destination.
        from_IP (str): The address that will be the source 
        of traffic of this rule.
        from_port (str): The port that this rule will apply to it in the source.
        from_service_name (str):  The service_name that this rule will apply to it in the source.
        protocol (str): The protocol that this rule will apply to it.
        to_service_name (str):  The service_name that this rule will apply to it in the destination.
        add_date (datetime): The date and time this rule added. 
    """
    __tablename__ = "rules"
    id = Column(Integer, primary_key=True,
                nullable=False, unique=True)
    user_id = Column(Integer, nullable=False)
    rule_command = Column(String, nullable=False)
    rule_action = Column(String, nullable=False)
    in_out = Column(String, nullable=False)
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
    This is a class that used as custom serializers for Rule Object.
    """
    class Meta:
        fields = ("id", "user_id", "rule_command", "rule_action",
                  "in_out", "to_IP", "to_port", "to_service_name",
                  "from_IP", "from_port", "from_service_name",
                  "protocol", "comment", "add_date")


rule_schema = RuleSchema()
rules_schema = RuleSchema(many=True)
