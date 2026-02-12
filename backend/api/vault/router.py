from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse
from ...core.vault_service import vault_service
from ...models.models import Usuario
from ..auth.deps import get_current_user
import os

router = APIRouter(prefix="/vault", tags=["Financial Vault"])

@router.post("/upload")
async def upload_to_vault(
    file: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Directly uploads a file to the vault.
    """
    filename = await vault_service.save_file(file)
    return {"filename": filename, "message": "File uploaded successfully"}

@router.get("/files")
async def list_vault_files(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lists all files in the financial vault.
    """
    return vault_service.get_all_files()

@router.get("/files/{filename}")
async def get_vault_file(
    filename: str,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Retrieves a specific file from the vault.
    """
    file_path = vault_service.upload_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(file_path))

@router.delete("/files/{filename}")
async def delete_vault_file(
    filename: str,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Deletes a file from the vault.
    """
    success = vault_service.delete_file(filename)
    if not success:
        raise HTTPException(status_code=404, detail="File not found or could not be deleted")
    return {"message": "File deleted successfully"}

@router.post("/ocr/{filename}")
async def extract_file_text(
    filename: str,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Triggers OCR extraction for a given file.
    """
    text = await vault_service.extract_text(filename)
    return {"text": text}
