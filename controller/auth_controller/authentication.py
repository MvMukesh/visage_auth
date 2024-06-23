from typing import Optional
from jose import JWTError, jwt #provide functions for creating and decoding JWT tokens used in authentication
from pydantic import BaseModel
from face_auth.entity.user import User
from datetime import datetime, timedelta
from starlette.responses import JSONResponse, RedirectResponse
from fastapi import APIRouter, HTTPException, Request, Response, status
from face_auth.business_val.user_val import LoginValidation, RegisterValidation
from face_auth.constant.auth_constant import ALGORITHM, SECRET_KEY



### defining DATA MODELS for user login and registration information ###

#expected data structure for user login requests
class Login(BaseModel): #using Pydantic BaseModel class
    """
        Base model to login
    """
    email_id: str
    password: str

#expected data structure for user registration requests
class Register(BaseModel): #using Pydantic BaseModel class
    """
        Base model to register
    """
    Name: str
    username: str
    email_id: str
    ph_no: int
    password1: str
    password2: str #Pydantic also allows alphanumeric characters



"""
let's defines a reusable router specifically for handling authentication-related endpoints 
    (likely login and registration) within your FastAPI application. 
The router utilizes pre-defined data models for user login and registration information 
    and sets a base path (/auth) for the routes it manages
"""
#defining a router - creating instance of APIRouter from FastAPI
router = APIRouter(prefix="/auth",tags=["auth"],
                   responses={"401": {"description":"Not Authorized!!!"}},)
"""
prefix="/auth": This sets the base path for all routes defined within this router.
    Any route defined here will start with /auth

tags=["auth"]: This adds the "auth" tag to all routes defined in this router, 
    which will be helpful for API documentation

responses={"401": {"description": "Not Authorized!!!"}}: 
    This pre-defines a response for the HTTP status code 401 (Unauthorized). 
    This response will be automatically sent if a route within this router 
    encounters an authorization error (e.g., invalid token)
        Say you dont have account and you are loging in.
"""

############

"""
defining a function named get_current_user, this retrieves 
    currently logged-in userinformation 
Also using JWT (JSON Web Token) for authentication
"""
# Calling the logger for Database read and insert operations
async def get_current_user(request: Request):
    """
        Args:
            request (Request): Request from route
        Returns:
            dict: Returns username and uuid of user
    """
    try:
        secret_key = SECRET_KEY
        algorithm = ALGORITHM

        token = request.cookies.get("access_token")
        if token is None:
            return None

        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        uuid: str = payload.get("sub")
        username: str = payload.get("username")

        if uuid is None or username is None:
            return logout(request)
        return {"uuid": uuid, "username": username}
    except JWTError:
        raise HTTPException(status_code=404, detail="Detail Not Found")
    except Exception as e:
        msg = "Error while getting current user"
        response = JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": msg})
        return response

"""
Functionality:
1. Retrieving Access Token:

- function attempts to get the access_token from the user's cookies using 
    request.cookies.get("access_token").
- if no token is found, the function returns None, indicating the user is 
    not authenticated.

2. JWT Decoding (if Token Exists):

- if a token is present, function uses jwt.decode from the jose library to 
    decode the token based on the secret key (SECRET_KEY) and algorithm (ALGORITHM) 
    defined in the face_auth.constant.auth_constant module
- this decoding process retrieves the payload embedded within the token

3. Extracting User Information:

- function attempts to extract two pieces of information from decoded payload:
    - uuid: This is likely a unique identifier for user
    - username: user's username
- if either uuid or username is missing, function will call logout function 
    to potentially clear any invalid tokens and returns None

4. Returning User Information:

- if everything is successful, function returns a dictionary containing
     retrieved uuid and username for current user

5. Error Handling:

function includes exception handling for two cases:
    - JWTError: if token decoding fails (e.g., invalid token), an HTTPException 
        with status code 404 (Not Found) and a detail message is raised
    - Exception: Any other unexpected exception is caught, and a generic error message 
        is returned in a JSON response with status code 404 (Not Found)
"""