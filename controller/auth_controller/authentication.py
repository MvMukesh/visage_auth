from typing import Optional
from jose import JWTError, jwt #provide functions for creating and decoding JWT tokens used in authentication
from pydantic import BaseModel
from visage_auth.entity.user import User
from datetime import datetime, timedelta
from starlette.responses import JSONResponse, RedirectResponse
from fastapi import APIRouter, HTTPException, Request, Response, status
from visage_auth.business_val.user_val import LoginValidation, RegisterValidation
from visage_auth.constant.auth_constant import ALGORITHM, SECRET_KEY



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

        #get access_token from user's cookies
        token = request.cookies.get("access_token")
        #if no token is found return none, indicating user is not authenticated
        if token is None:
            return None

        #If a token is present decode token based on secret key and algorithm
            # defined in visage_auth.constant.auth_constant module
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        uuid: str = payload.get("sub")
        username: str = payload.get("username")

        #if uuid or username is missing then logout
        if uuid is None or username is None:
            return logout(request)
        #if all good return this of current user
        return {"uuid": uuid, "username": username} 
    #JWTEroor handling - Case-1
    except JWTError:
        raise HTTPException(status_code=404, detail="Detail Not Found")
    #Exception handling - Case-2
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
    defined in the visage_auth.constant.auth_constant module
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

################

#this function will generate a JWT (JSON Web Token) for a user
    # expires_delta (Optional[timedelta]): This parameter allows specifying an optional expiration time for the token as a timedelta object. 
        # If not provided, a default expiration of 15 minutes is used
def create_access_token(uuid:str,username:str,expires_delta:Optional[timedelta]=None) -> str:
    """
    Generates JWT tokens that can be used for user authentication 
        throughout the application
        OR
    Generate a JWT token containing user information and an expiration claim
        Args:
            uuid (str): uuid of the user
            username (str): username of the user

        Raises:
            e: _description_

        Returns:
            _type_: _description_
    """

    try:
        secret_key = SECRET_KEY #retrieves secret key for signing JWT token
        algorithm = ALGORITHM

        ## constructing JWT payload
        encode = {"sub":uuid,"username":username} #sub is a registered JWT claim that typically represents subject of token (user in this case)
        
        ## setting token expiration (optional)
        if expires_delta: #checks if expires_delta argument was provided when calling create_access_token function
            #expire = datetime.utcnow() + expires_delta #if expires_delta is provided, it calculates expiration time by adding provided timedelta object to current UTC time
            expire = datetime.now(datetime.UTC) + expires_delta
        else:
            #expire = datetime.utcnow() + timedelta(minutes=15) #adds 15 minutes to current UTC time to define expiration time
            expire = datetime.now(datetime.UTC) + timedelta(minutes=15)
        
        ## adding expiration claim - essential for verifying validity of token later
        encode.update({"exp": expire}) #updates encode dictionary with a new key-value pair: "exp" (representing expiration) is set to calculated expiration time (expire)
        
        ## JWT Encoding and Return
        # return jwt.encode(encode, Configuration().SECRET_KEY, algorithm=Configuration().ALGORITHM)
        ## using jwt.encode function from the jose library
        return jwt.encode(encode, secret_key, algorithm=algorithm)
        """
        encode: payload dictionary containing user information and expiration claim
        secret_key: application's secret key used for signing token
        algorithm: signing algorithm used (e.g., HS256)
        """
    ## Error Handling: catch any unexpected errors during the encoding process
    except Exception as e:
        raise e
    
################

@router.post("/token")
async def login_for_access_token(response:Response,login) -> dict: #"login" object as input - containing user's email and password
    """
    Handles user login and generates a JWT access token if login is successful
        OR
    Handles user login, validates credentials and generates JWT tokens for authenticated users
        Returns:
            dict: response
    """

    try:
        #creating an instance of LoginValidation is created, potentially using login object's email and password
        user_validation = LoginValidation(login.email_id, login.password)
        #calling authenticate_user_login method of this LoginValidation object which verifies user credentials against database(i.e. MongoDB here) 
        user: Optional[str] = user_validation.authenticate_user_login()
        
        ## Handling Failed Login
        
        #if authenticate_user_login returns a user object (presumably containing user information like UUID and username), login is successful
        if not user:
            return {"status":False, "uuid":None, "response":response}
        
        #creating a token_expires timedelta object, representing desired token expiration time (here 15 minutes)
        token_expires = timedelta(minutes=15)
        
        ## Generating Access Token
        #calling create_access_token function (defined earlier) with user's UUID, username and token_expires to generate a JWT access token
        token = create_access_token(user["UUID"],user["username"], 
                                    expires_delta=token_expires)
        
        ## Setting Access Token Cookie
        #setting generated JWT token as a cookie named access_token in the user's response
        response.set_cookie(key="access_token",
                            value=token, 
                            httponly=True) #httponly=True flag ensures cookie cannot be accessed by JavaScript for enhanced security
        
        ## Returning Success Response
        #returning a dictionary containing status=True, user's UUID and original response object
            #This response will be used by frontend to indicate successful login and potentially access user information
        return {"status": True, "uuid": user["UUID"], "response": response}
    ## Error Handling (previous code)
    # except Exception as e:
    #     msg = "Failed to set access token"
    #     response = JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": msg})
    #     return {"status": False, "uuid": None, "response": response}
    
    ## Specific Exception Handling
    except ValueError as e:
        # Handle specific login validation errors (e.g., invalid credentials)
        msg = f"Login failed: {e}"
        response = JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                content={"message": msg})
        return {"status": False, "uuid": None, "response": response}

    except Exception as e:
        # Catch other unexpected errors
        msg = "An unexpected error occurred during login."
        response = JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                content={"message": msg})
        return {"status": False, "uuid": None, "response": response}

################

#this function handles GET requests at root path (/) within previously defined router
@router.get("/", response_class=JSONResponse) #response_class=JSONResponse specifies that the return value of the function should be automatically converted to a JSON response object
async def authentication_page(request:Request): #asynchronous function (useful for handling non-blocking operations)
    """
    Provides a basic GET endpoint for authentication page, 
        returning a simple success message in JSON format

        Returns:
            _type_: JSONResponse (with a success message)
    """
    try:
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message":"Authentication Page"})
    ## Exception Handling - (old)
    # except Exception as e:
    #     raise e
    except Exception as e:
        # improved error handling based on potential exceptions
        if isinstance(e, HTTPException):
            # Handle known HTTP exceptions (e.g., user-caused errors)
            return e
        else:
            # catch other unexpected errors
            msg = "An unexpected error occurred during authentication."
            response = JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    content={"message": msg})
            return response

################

#function decorator defining a POST route at root path (/) within previously defined router (router)
@router.post("/", response_class=JSONResponse)
async def login(request:Request,login:Login): #response_class=JSONResponse specifies that the function should automatically convert its return value to a JSON response object
    """
    Handles user login requests and returns a JSON response 
        indicating success or failure
            OR
    provides a robust approach to handling user login requests, 
        differentiating between successful login, unsuccessful login due to incorrect credentials, and unexpected errors

        Arguments:
            request: Request: captures incoming HTTP request object
            login: Login: receives data from request body, expected to be an instance of Login data model defined earlier
                            this model likely contains user's email and password for login
        Returns:
            _type_: Login Response
    """
    try:
        # response = RedirectResponse(url="/application/", status_code=status.HTTP_302_FOUND)
        msg = "Login Successful"
        response = JSONResponse(status_code=status.HTTP_200_OK, 
                                content={"message": msg})
        #calling login_for_access_token
            # it handles login validation, token generation (if successful), and potentially sets access token as a cookie in response
            # token_response will be a dictionary containing information about login attempt (e.g., status indicating success or failure, uuid of user if successful)
        token_response = await login_for_access_token(response=response,
                                                      login=login)
        ## Handling Unsuccessful Login
            #if token_response["status"] is False (indicating unsuccessful login), a new message ("Incorrect Username and password") is assigned to msg
        if not token_response["status"]:
            msg = "Incorrect Username and password"
            # JSON response will be created with status code HTTP_401_UNAUTHORIZED, indicating unauthorized access due to incorrect credentials
                #  response content includes "status": False and error message
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                content={"status": False, "message": msg},)
            # return RedirectResponse(url="/", status_code=status.HTTP_401_UNAUTHORIZED, headers={"msg": msg})
        # msg = "Login Successfull"
        # response = JSONResponse(status_code=status.HTTP_200_OK, content={"message": msg}, headers={"uuid": "abda"})
        
        ## Setting User UUID (Successful Login)
            #Assuming token_response["status"] is True (successful login), user's uuid is extracted from token_response["uuid"]
                #this uuid is then set as a header in response object using response.headers["uuid"] = token_response["uuid"]
        response.headers["uuid"] = token_response["uuid"]
        
        ##Returning Response
            # response object will be returned, containing appropriate status code, message, and potentially user's uuid in header (for successful login) 
        return response

    ##Exception Handling
    except HTTPException:
        msg = "UnKnown Error"
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                            content={"status":False, "message":msg},)
        # return RedirectResponse(url="/", status_code=status.HTTP_401_UNAUTHORIZED, headers={"msg": msg})
    except Exception as e:
        msg = "User NOT Found"
        response = JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content={"status": False, "message": msg},)
        return response
    
################
    
@router.get("/register",response_class=JSONResponse)
async def authentication_page(request: Request):
    """
    Route for User Registration
                OR
    Handling user registration

        request: Request. captures incoming HTTP request object containing details about current request
        Returns:
            _type_: Register Response
    """
    try:
        return JSONResponse(status_code=status.HTTP_200_OK,content={"message":"Registration Page"})
    except Exception as e:
        raise e   

################

#get rout for registering || In fron-end implementation response_class must be html now it is JSONResponse)
@router.post("/register",response_class=JSONResponse)
async def register_user(request:Request,register:Register):

    """
        Post request to register a user

        Args:
            request (Request): Request Object
            register (Register):    Name: str
                                    username: str
                                    email_id: str
                                    ph_no: int
                                    password1: str
                                    password2: str
        Raises:
            e: If user registration fails

        Returns:
            _type_: Will redirect to the embedding generation route and return the UUID of user
    """
    try:
        name = register.Name
        username = register.username
        password1 = register.password1
        password2 = register.password2
        email_id = register.email_id
        ph_no = register.ph_no

        # add uuid to the session (passing to User Entity, will get UUID)
        user = User(name,username,email_id,ph_no,password1,password2) #using User class from user.py
        request.session["uuid"] = user.uuid_ #storing UUID in session

        # Validation of user input data to check format of data
        user_registration = RegisterValidation(user)

        validate_regitration = user_registration.validate_registration()
        if not validate_regitration["status"]:
            msg = validate_regitration["msg"]
            response = JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,content={"status":False,"message":msg},)
            return response

        # Save user if validation is successful
        validation_status = user_registration.authenticate_user_registration()

        msg = "Registration Successful...Please Login to continue"
        response = JSONResponse(status_code=status.HTTP_200_OK,
                                content={"status":True,"message":validation_status["msg"]},
                                headers={"uuid":user.uuid_},)
        return response
    
    except Exception as e:
        raise e