#!/usr/bin/env python
"""
Background script to install AI services dependencies for OBCMS/BMMS.
This script handles the installation of heavy AI packages without blocking the main process.
"""

import subprocess
import sys
import os
from datetime import datetime

def install_package(package_name):
    """Install a single package with error handling."""
    try:
        print(f"📦 Installing {package_name}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout per package
        )

        if result.returncode == 0:
            print(f"✅ {package_name} installed successfully")
            return True
        else:
            print(f"❌ Failed to install {package_name}: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"⏰ Installation of {package_name} timed out")
        return False
    except Exception as e:
        print(f"❌ Error installing {package_name}: {e}")
        return False

def check_package_installed(package_name):
    """Check if a package is already installed."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", f"import {package_name.replace('-', '_')}"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False

def main():
    """Main installation function."""

    print("=" * 60)
    print("OBCMS AI DEPENDENCIES INSTALLER")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Critical AI packages to install
    packages = [
        "sentence-transformers>=2.2.0",
        "faiss-cpu>=1.7.0",
        "google-generativeai>=0.1.0",
        "transformers>=4.20.0",
        "accelerate>=0.20.0"
    ]

    installed_packages = []
    failed_packages = []

    for package in packages:
        package_base = package.split(">=")[0].split("==")[0]

        # Check if already installed
        if check_package_installed(package_base):
            print(f"✅ {package_base} already installed")
            installed_packages.append(package_base)
            continue

        # Install the package
        if install_package(package):
            installed_packages.append(package_base)
        else:
            failed_packages.append(package_base)

    print("\n" + "=" * 60)
    print("INSTALLATION SUMMARY")
    print("=" * 60)

    print(f"✅ Successfully installed ({len(installed_packages)}):")
    for pkg in installed_packages:
        print(f"   - {pkg}")

    if failed_packages:
        print(f"\n❌ Failed to install ({len(failed_packages)}):")
        for pkg in failed_packages:
            print(f"   - {pkg}")
        return 1
    else:
        print("\n🎉 All AI dependencies installed successfully!")
        print("🚀 AI services are now ready for OBCMS/BMMS")
        return 0

if __name__ == "__main__":
    sys.exit(main())