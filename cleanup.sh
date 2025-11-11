#!/bin/bash
# LAIT Cleanup Script - Archive redundant backend app files and make canonical entrypoint explicit

echo "🧹 Cleaning up / archiving redundant backend app files..."

# Define the main app file we want to keep (canonical entrypoint)
MAIN_APP="app_real.py"

# Directory to archive old files
ARCHIVE_DIR="backend/archive"
mkdir -p "$ARCHIVE_DIR"

# List of app files that should be archived (kept in archive for history)
declare -a APP_FILES=(
    "production_app.py"
    "enhanced_app.py"
    "unified_app.py"
    "single_root_app.py"
    "comprehensive_app.py"
    "app_real_new.py"
    "app.py"          # legacy factory (archived in favor of app_real.py)
    "simple_app.py"
)

echo "📌 Canonical backend entrypoint set to: backend/$MAIN_APP"

# Move redundant app files to archive (safe: do not delete)
for file in "${APP_FILES[@]}"; do
    if [ -f "backend/$file" ]; then
        echo "📦 Archiving backend/$file -> $ARCHIVE_DIR/"
        mv "backend/$file" "$ARCHIVE_DIR/"
    fi
done

echo "✅ Cleanup/archival completed!"
echo "📝 Note: Redundant backend app files have been moved to $ARCHIVE_DIR"
echo "🚀 The system now uses a single canonical backend: backend/$MAIN_APP"
