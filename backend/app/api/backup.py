import os
import shutil
import subprocess

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.core.config import settings

router = APIRouter()

@router.get("/backup/export")
async def export_database():
  db_url = settings.DATABASE_URL

  # Create backup in __temp__ folder
  directory = "__temp__"
  backup_file = "backup"

  # Recreate the directory
  if os.path.exists(directory):
    shutil.rmtree(directory)

  os.makedirs(directory)
  
  # Exporting the database
  try:
    subprocess.run(
      [
        "pg_dump",
        f"--dbname={db_url}",
        f"--file={directory}/{backup_file}.sql",
      ],
      check=True,
    )

    return FileResponse(f"{directory}/{backup_file}.sql", media_type="application/octet-stream", filename=f"{backup_file}.sql")
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

@router.post("/backup/import")
async def import_database(backup_file: UploadFile = File(...)):
  db_url = settings.DATABASE_URL

  temp_file = f"temp_{backup_file.filename}"

  with open(temp_file, "wb+") as file_object:
    file_object.write(backup_file.file.read())

  # Clear the database
  try:
    subprocess.run(
      [
        "psql",
        f"--dbname={db_url}",
        "--command=DROP SCHEMA public CASCADE; CREATE SCHEMA public;",
      ],
      check=True,
    )
  except Exception as e:
    os.remove(temp_file)
    raise HTTPException(status_code=500, detail=str(e))

  # Importing the database
  try:
    subprocess.run(
      [
        "psql",
        f"--dbname={db_url}",
        f"--file={temp_file}",
      ],
      check=True,
    )
  except Exception as e:
    os.remove(temp_file)
    raise HTTPException(status_code=500, detail=str(e))

  os.remove(temp_file)
  return {"detail": "Database imported successfully"}
