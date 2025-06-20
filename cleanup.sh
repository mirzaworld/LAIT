#!/bin/bash
# LAIT Cleanup Script - Remove redundant app files

echo "🧹 Cleaning up redundant backend files..."

# Define the main app file we want to keep
MAIN_APP="enhanced_app.py"

# Directory to archive old files
ARCHIVE_DIR="backend/archive"
mkdir -p "$ARCHIVE_DIR"

# List of app files that should be archived (not deleted)
declare -a APP_FILES=(
    "production_app.py"
    "simple_app.py"
    "comprehensive_app.py"
    "super_simple.py"
)

# Move redundant app files to archive
for file in "${APP_FILES[@]}"; do
    if [ -f "backend/$file" ]; then
        echo "📦 Archiving $file"
        mv "backend/$file" "$ARCHIVE_DIR/"
    fi
done

echo "✅ Cleanup completed!"
echo "📝 Note: Redundant app files have been moved to $ARCHIVE_DIR"
echo "🚀 The system now uses a single unified backend: backend/$MAIN_APP"
