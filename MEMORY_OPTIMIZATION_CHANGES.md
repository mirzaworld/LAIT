# Memory Optimization Changes

## Issue: "JS heap out of memory" Error

The application was experiencing "JS heap out of memory" errors, likely due to inefficient handling of large files and data processing.

## Changes Implemented

### Backend Changes

1. Added file size limits (10MB maximum) to prevent excessive memory consumption
2. Implemented chunked file processing for large uploads instead of loading entire files into memory
3. Added proper cleanup of temporary files after processing
4. Improved error handling for large file uploads

### Frontend Changes

1. Added file validation for size and type before uploading
2. Limited batch uploads to a maximum of 5 files at once
3. Modified upload process to handle files sequentially rather than all at once
4. Added progress tracking to show upload status

### Development Environment Improvements

1. Added `--max-old-space-size=4096` to Node.js options to increase available memory
2. Created a memory analysis script (`scripts/memory_check.cjs`) to identify memory issues
3. Created a memory-optimized startup script (`run_with_increased_memory.sh`)
4. Added documentation on memory management best practices

### NPM Scripts Added

- `npm run memory-check` - Run the memory analysis script
- `npm run start-optimized` - Start both backend and frontend with increased memory

## Documentation

- Added detailed `docs/MEMORY_MANAGEMENT.md` with best practices and troubleshooting tips
- Updated README.md with information about memory-optimized startup options

## Additional Improvements

1. Identified large files in the codebase that might contribute to memory pressure
2. Added recommendations for handling large datasets and file processing

## Testing

The memory check script revealed several large libraries and model files that could contribute to memory pressure. The application now handles these more efficiently with the implemented changes.

These optimizations should resolve the "JS heap out of memory" errors and provide a more stable application experience, especially when processing large files or datasets.
