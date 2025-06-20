# Memory Management Guidelines for LAIT

This document outlines best practices and solutions for handling memory issues in the LAIT application.

## Common Memory Issues

The "JS heap out of memory" error occurs when the Node.js process exhausts its allocated memory. This can happen in various scenarios:

1. Processing large files (PDFs, documents)
2. Loading large datasets into memory all at once
3. Memory leaks in React components
4. Inefficient data handling in backend processing

## Implemented Solutions

### Backend Improvements

- **File Size Limits**: 10MB maximum file size restriction for uploads
- **Chunked File Processing**: Files are processed in 1MB chunks to avoid loading entire large files into memory
- **Temporary File Management**: Proper cleanup of temporary files after processing
- **Memory-Efficient Data Processing**: Large datasets are processed in chunks

### Frontend Improvements

- **File Validation**: Files are validated for size and type before uploading
- **Limited Batch Uploads**: Maximum of 5 files can be uploaded at once
- **Sequential Processing**: Files are processed one at a time instead of in parallel
- **Progress Tracking**: Improved progress tracking to show activity during processing

### Development Environment

- **Increased Node.js Memory**: Development scripts now use `--max-old-space-size=4096` to allocate 4GB of memory
- **Memory Analysis Script**: Added `scripts/memory_check.js` to identify potential memory issues
- **Optimized Startup Script**: `run_with_increased_memory.sh` for easier development with proper memory allocation

## Best Practices

1. **Paginate Large Data**: Always use pagination when displaying large datasets
2. **Clean Up Subscriptions**: Ensure all React effects and subscriptions are properly cleaned up
3. **Manage File Uploads**: Limit file sizes and process files efficiently
4. **Memory Monitoring**: Use the memory check script periodically to monitor application memory usage
5. **Lazy Loading**: Use React.lazy() for code splitting and load components only when needed

## Using Increased Memory Allocation

For development with increased memory:

```bash
# Use the optimized startup script
./run_with_increased_memory.sh

# Or manually set memory limits
export NODE_OPTIONS=--max-old-space-size=4096
npm run dev
```

For production builds:

```bash
NODE_OPTIONS=--max-old-space-size=4096 npm run build
```

## Troubleshooting Memory Issues

If memory issues persist:

1. Run the memory analysis script: `node scripts/memory_check.js`
2. Check for large files in the project using the report
3. Review components that handle large datasets
4. Consider implementing virtual scrolling for large tables
5. Review API endpoints that return large datasets and implement pagination
