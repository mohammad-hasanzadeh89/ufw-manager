from sqlalchemy import Column, Integer, String, Boolean
from utilities.db_manager import db, ma, bcrypt


class User(db.Model):
    """
    This is a class that stores user data and used for
    interact with users table.

    Attributes:
        username (str): The username of the user.
        password (str): The password of the user.
        admin_privileges (bool): Indicate the user has authority
        to grant users manager_privileges.
        manager_privileges (bool): Indicate the user has authority
        to interact with UFW.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False,
                autoincrement=True, unique=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    admin_privileges = Column(Boolean, default=False, nullable=False)
    manager_privileges = Column(Boolean, default=False, nullable=False)

    def __init__(self, username, password, admin_privileges, manager_privileges):
        self.username = username
        self.set_password(password)
        self.admin_privileges = admin_privileges
        self.manager_privileges = manager_privileges

    def set_password(self, password):
        """
        The function to hash and set user password with hash version of it.

        Parameters:
            password (str): The string that will be set as the user password.
        """
        self.password = bcrypt.generate_password_hash(password, 12).decode()

    def verify_password(self, pwd):
        """
        The function to compare plain text to hashed password.

        Parameters:
            pwd (str): The string that will be checked for equality.

        Return:
            bool: That repesents, hashed password and plain
            text is equal or not.
        """
        return bcrypt.check_password_hash(self.password, pwd)

    def __repr__(self):
        """
        The function that returns string representation of the user.

        Return:
            str: The string representation of the user.
        """
        return f'{self.username}'


class UserSchema(ma.Schema):
    """
    This is a class that used as custom serializers for User Object.
    """
    class Meta:
        fields = ("id", "username", "admin_privileges", "manager_privileges")


user_schema = UserSchema()
users_schema = UserSchema(many=True)
