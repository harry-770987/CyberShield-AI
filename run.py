import os
import subprocess
import sys

def main():
    print("=" * 60)
    print("Starting CyberShield AI Backend")
    print("=" * 60)
    
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    
    if not os.path.exists(backend_dir):
        print("Error: 'backend' directory not found.")
        sys.exit(1)
        
    os.chdir(backend_dir)
    
    # 1. Setup Virtual Environment
    venv_dir = os.path.join(backend_dir, "venv")
    if not os.path.exists(venv_dir):
        print("-> Virtual environment not found. Creating one now...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("-> Virtual environment created successfully.")
    
    # Define paths based on OS
    if os.name == 'nt': # Windows
        python_exe = os.path.join(venv_dir, "Scripts", "python.exe")
        pip_exe = os.path.join(venv_dir, "Scripts", "pip.exe")
    else: # Mac/Linux
        python_exe = os.path.join(venv_dir, "bin", "python")
        pip_exe = os.path.join(venv_dir, "bin", "pip")
        
    # 2. Install dependencies
    print("-> Checking/Installing dependencies (this may take a moment)...")
    subprocess.run([pip_exe, "install", "-r", "requirements.txt", "--quiet"], check=False)
    print("-> Dependencies are ready.")
    
    print("\nStarting FastAPI server on http://127.0.0.1:8000")
    print("Press Ctrl+C to stop the server.")
    print("-" * 60)
    
    try:
        # Run uvicorn using the virtual environment's python
        subprocess.run([python_exe, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"])
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        
    print("\n" + "=" * 60)
    print("To run the frontend dashboard:")
    print("1. Open a new terminal")
    print("2. cd frontend")
    print("3. npm install (if not already done)")
    print("4. npm run dev")
    print("=" * 60)

if __name__ == "__main__":
    main()
