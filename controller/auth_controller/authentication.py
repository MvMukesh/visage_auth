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
                   responses={"401": {"description": "Not Authorized!!!"}},)
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
