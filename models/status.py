from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from utilities.db_manager import db, ma


class Status(db.Model):
    """
    This is a class that stores status of UFW service
    data and used for
    interact with status table.

    Attributes:
        user_id (int): The ID of the user that changes status
        of UFW to this rule.
        ufw_status (bool): Indicate UFW service is active or not.
        change_date (datetime): The date and time this change made.
    """
    __tablename__ = "statues"
    id = Column(Integer, primary_key=True,
                nullable=False, unique=True)
    user_id = Column(Integer, nullable=False)
    ufw_status = Column(Boolean, nullable=False)
    change_date = Column(DateTime, nullable=False, default=datetime.now())


class StatusSchema(ma.Schema):
    """
    This is a class that used as custom serializers for Status Object.
    """
    class Meta:
        fields = ("id", "user_id", "ufw_status", "change_date")


status_schema = StatusSchema()
statuses_schema = StatusSchema(many=True)
