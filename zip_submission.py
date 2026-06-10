import os
import zipfile

def zip_project(output_filename="submission.zip"):
    # Exclude directories
    exclude_dirs = {
        "node_modules",
        ".next",
        ".git",
        "__pycache__",
        ".venv",
        ".gemini",
        "out"
    }
    
    # Exclude specific files
    exclude_files = {
        output_filename,
        "zip_submission.py",
        "package-lock.json"
    }

    # Current working directory (project root)
    root_dir = os.path.abspath(os.path.dirname(__file__))
    
    print(f"Zipping repository: {root_dir}")
    print(f"Excluding directories: {', '.join(exclude_dirs)}")
    
    count = 0
    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(root_dir):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
            
            for file in files:
                if file in exclude_files or file.startswith('.'):
                    continue
                if file == "Maintenance_Wizard_Project_Report.pdf":
                    continue
                
                full_path = os.path.join(root, file)
                # Compute relative path for zip archive
                rel_path = os.path.relpath(full_path, root_dir)
                
                if file == "Maintenance_Wizard_Project_Report_v2.pdf":
                    zipf.write(full_path, "Maintenance_Wizard_Project_Report.pdf")
                else:
                    zipf.write(full_path, rel_path)
                count += 1

    print(f"Successfully created {output_filename} containing {count} files.")

if __name__ == "__main__":
    zip_project()
