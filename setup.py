#!/usr/bin/env python3
"""
Setup script for NSE News Analysis System
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command with error handling"""
    print(f"\n📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error during {description}: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print("✅ Python version is compatible")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing Python dependencies...")
    
    # Upgrade pip first
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing requirements"):
        return False
    
    return True

def download_nltk_data():
    """Download required NLTK data"""
    print("\n📚 Downloading NLTK data...")
    
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("✅ NLTK data downloaded successfully")
        return True
    except Exception as e:
        print(f"❌ Error downloading NLTK data: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = ['data', 'output', 'logs']
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        print(f"✅ Created directory: {dir_name}")
    
    return True

def test_imports():
    """Test if all required modules can be imported"""
    print("\n🧪 Testing imports...")
    
    modules_to_test = [
        'pandas', 'numpy', 'requests', 'beautifulsoup4', 'nltk', 'textblob',
        'newspaper3k', 'feedparser', 'dash', 'plotly', 'fake_useragent'
    ]
    
    failed_imports = []
    
    for module in modules_to_test:
        try:
            if module == 'beautifulsoup4':
                import bs4
            elif module == 'newspaper3k':
                import newspaper
            else:
                __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        return False
    
    print("\n✅ All modules imported successfully")
    return True

def test_system():
    """Run a quick system test"""
    print("\n🔧 Running system test...")
    
    try:
        # Test configuration loading
        from config import NSE_COMPANIES_FILE, NEWS_SOURCES
        print("✅ Configuration loaded")
        
        # Test utilities
        from utils import load_nse_companies
        companies_df = load_nse_companies()
        if not companies_df.empty:
            print(f"✅ Loaded {len(companies_df)} NSE companies")
        else:
            print("❌ Failed to load NSE companies")
            return False
        
        # Test scraper initialization
        from scraper import NewsScraper
        scraper = NewsScraper()
        print("✅ News scraper initialized")
        
        # Test analyzer initialization
        from analyzer import NewsAnalyzer
        analyzer = NewsAnalyzer()
        print("✅ News analyzer initialized")
        
        print("\n✅ System test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 NSE News Analysis System Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Download NLTK data
    if not download_nltk_data():
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("\n❌ Some dependencies failed to import. Try:")
        print("   pip install --upgrade -r requirements.txt")
        sys.exit(1)
    
    # Test system
    if not test_system():
        print("\n❌ System test failed. Check the error messages above.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run full analysis: python main.py --mode full")
    print("2. Start dashboard: python main.py --mode dashboard")
    print("3. Analyze specific companies: python main.py --mode companies --companies RELIANCE TCS")
    print("\nFor help: python main.py --help")
    print("\n📚 Read README.md for detailed usage instructions")

if __name__ == "__main__":
    main()
