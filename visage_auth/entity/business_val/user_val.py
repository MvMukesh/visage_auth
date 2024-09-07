import re
import sys
from typing import Optional

from passlib.context import CryptContext

from visage_auth.logger import logging
from visage_auth.entity.user import User
from visage_auth.exception import AppException
from visage_auth.data_access.user_data import UserData


bcrypt_context = CryptContext(schemes=["bcrypt"],deprecated="auto")


class LoginValidation:
    def __init__(self,email_id:str, password:str):
        """
        Args:
            email_id (str): _description_
            password (str): _description_
        """
        self.email_id = email_id
        self.password = password
        self.regex = re.compile(r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+")

    def validate(self) -> bool:
        """
        Validates user input

        Args:
            email_id (str): email_id of the user
            password (str): password of the user
        """
        try:
            msg = ""
            if not self.email_id:
                msg += "Email Id is required"
            if not self.password:
                msg += "Password is required"
            if not self.is_email_valid():
                msg += "Invalid Email Id"
            return msg
        except Exception as e:
            raise e

    def is_email_valid(self) -> bool:
        if re.fullmatch(self.regex, self.email_id):
            return True
        else:
            return False

    def verify_password(self, plain_password:str, hashed_password:str) -> bool:
        """
        Verifyies hashed password and plain password

        Args:
            plain_password (str): _description_
            hashed_password (str): _description_

        Returns:
            bool: _description_
        """
        return bcrypt_context.verify(plain_password,hashed_password)

    def validate_login(self) -> dict:

        """
        Checks all validation conditions for user registration
        """
        if len(self.validate()) != 0:
            return {"status": False, "msg": self.validate()}
        return {"status": True}

    def authenticate_user_login(self) -> Optional[str]:
        """
        Authenticates user and returns token if user is authenticated

        Args:
            email_id (str): _description_
            password (str): _description_
        """
        try:
            logging.info("Authenticating the user details.....")
            if self.validate_login()["status"]:
                userdata = UserData()
                logging.info("Fetching the user details from the database.....")
                user_login_val = userdata.get_user({"email_id":self.email_id})
                if not user_login_val:
                    logging.info("User not found while Login")
                    return False
                if not self.verify_password(self.password,user_login_val["password"]):
                    logging.info("Password is incorrect")
                    return False
                logging.info("User authenticated successfully....")
                return user_login_val
            return False
        except Exception as e:
            raise AppException(e, sys) from e


