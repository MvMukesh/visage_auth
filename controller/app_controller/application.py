import os
from typing import List
from fastapi import APIRouter, File, Request
from starlette import status
from starlette.responses import JSONResponse, RedirectResponse
from controller.auth_controller.authentication import get_current_user
from visage_auth.business_val.user_embedding_val import (UserLoginEmbeddingValidation,
                                                       UserRegisterEmbeddingValidation,)


router = APIRouter(prefix="/application",tags=["application"],
                   responses={"401":{"description":"Not Authorized!!!"}},)
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"



@router.post("/register_embedding")
async def register_embedding(request: Request,
                             files: List[bytes] = File(description="Multiple files as UploadFile"),):
    """
        This function is used to get the embedding of the user while register

        Args:
            request (Request): _description_
            files (List[UploadFile], optional): _description_. Defaults to \File(description="Multiple files as UploadFile").

        Returns:
            Response: If user is registered then it returns the response
    """

    try:
        # Get the UUID from the session
        uuid = request.session.get("uuid")
        if uuid is None:
            return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
        user_embedding_validation = UserRegisterEmbeddingValidation(uuid)

        # Save the embeddings
        user_embedding_validation.save_embedding(files)

        msg = "Embedding Stored Successfully in Database"
        response = JSONResponse(status_code=status.HTTP_200_OK,
                                content={"status": True, "message": msg},
                                headers={"uuid": uuid},)
        return response
    except Exception as e:
        msg = "Error in Storing Embedding in Database"
        response = JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content={"status": True, "message": msg},)
        return response
