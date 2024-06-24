import uvicorn #to run the FastAPI application as a server
from fastapi import FastAPI
from starlette import status #Provides HTTP status codes for responses
from starlette.responses import RedirectResponse #creates a redirect response
from starlette.middleware.sessions import SessionMiddleware #Middleware for managing user sessions

from controller.app_controller import application
from controller.auth_controller import authenticate
from visage_auth.constant.application import APP_HOST, APP_PORT


app = FastAPI()

@app.get('/') #this defines a function named read_root that handles GET requests to the root path (/)
def read_root():
    #returning a RedirectResponse object
    return RedirectResponse(url='/auth',status_code=status.HTTP_302_FOUND)
#url='/auth': Specifies that the user should be redirected to the /auth path
#status_code=status.HTTP_302_FOUND: Sets the HTTP status code to 302 Found, 
    # indicating a redirection has occurred. This informs the user's browser 
    # that the requested resource (/) is located elsewhere (/auth)
"""
Data Flow:

1. User sends a GET request to the root path (/)
2. The read_root function intercepts the request
3. Function returns a RedirectResponse object, instructing the user's browser to redirect to the /auth path
4. ser's browser performs the redirection and sends a request to the /auth path (assuming the authentication logic resides there)
"""

app.include_router(authentication.router) #time to add controller/auth_controller/authentication


