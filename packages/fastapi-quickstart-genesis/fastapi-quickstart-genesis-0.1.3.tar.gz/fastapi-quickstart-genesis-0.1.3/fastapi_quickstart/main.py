import os
import sys
import shutil
from pathlib import Path

def create_fastapi_app(app_name: str, output_dir: str = "."):
    """
    Create a basic FastAPI app structure.
    """
    # Create the main app directory
    app_dir = Path(output_dir) / app_name
    app_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    (app_dir / "app").mkdir()
    (app_dir / "tests").mkdir()

    # Copy template files
    template_dir = Path(__file__).parent / "templates"
    shutil.copy(template_dir / "main.py.template", app_dir / "app" / "main.py")
    shutil.copy(template_dir / "models.py.template", app_dir / "app" / "models.py")
    shutil.copy(template_dir / "requirements.txt.template", app_dir / "requirements.txt")

    print(f"FastAPI app structure created in {app_dir}")

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m fastapi_quickstart <app_name>")
    else:
        create_fastapi_app(sys.argv[1])

if __name__ == "__main__":
    main()