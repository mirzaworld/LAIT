// Memory check utility for LAIT application
// Run with: node scripts/memory_check.js

import fs from 'fs';
import path from 'path';
import { exec as execCallback } from 'child_process';
import { fileURLToPath } from 'url';
import { promisify } from 'util';

const exec = promisify(execCallback);
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const checkPaths = [
  '../backend',
  '../src'
];
const largeFileSizeThreshold = 5 * 1024 * 1024; // 5MB
const baseDir = path.resolve(__dirname);
const outputFile = path.join(baseDir, 'memory_analysis.txt');

// Memory usage formatter
function formatMemorySize(bytes) {
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  if (bytes === 0) return '0 Byte';
  const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}

// Current process memory usage
function getProcessMemoryUsage() {
  const memoryUsage = process.memoryUsage();
  
  return {
    rss: formatMemorySize(memoryUsage.rss), // Resident Set Size
    heapTotal: formatMemorySize(memoryUsage.heapTotal), // Total heap size
    heapUsed: formatMemorySize(memoryUsage.heapUsed), // Used heap size
    external: formatMemorySize(memoryUsage.external || 0), // External memory
    arrayBuffers: formatMemorySize(memoryUsage.arrayBuffers || 0) // ArrayBuffers size
  };
}

// Find large files
async function findLargeFiles(dir, threshold) {
  const largeFiles = [];
  const resolvedDir = path.resolve(baseDir, dir);
  
  try {
    // Check if directory exists
    if (!fs.existsSync(resolvedDir)) {
      return [];
    }
    
    const files = await fs.promises.readdir(resolvedDir);
    
    for (const file of files) {
      const filePath = path.join(resolvedDir, file);
      const stats = await fs.promises.stat(filePath);
      
      if (stats.isDirectory()) {
        const subDirLargeFiles = await findLargeFiles(filePath, threshold);
        largeFiles.push(...subDirLargeFiles);
      } else if (stats.size > threshold) {
        largeFiles.push({
          path: filePath,
          size: stats.size,
          formattedSize: formatMemorySize(stats.size)
        });
      }
    }
  } catch (error) {
    console.error(`Error scanning directory ${dir}:`, error);
  }
  
  return largeFiles;
}

// Main analysis function
async function analyzeMemoryUsage() {
  console.log('Starting memory analysis...');
  let output = '## LAIT Memory Analysis Report ##\n\n';
  
  // 1. Current process memory usage
  const memoryUsage = getProcessMemoryUsage();
  output += 'Current Process Memory Usage:\n';
  output += `- RSS (Resident Set Size): ${memoryUsage.rss}\n`;
  output += `- Heap Total: ${memoryUsage.heapTotal}\n`;
  output += `- Heap Used: ${memoryUsage.heapUsed}\n`;
  output += `- External: ${memoryUsage.external}\n`;
  output += `- ArrayBuffers: ${memoryUsage.arrayBuffers}\n\n`;
  
  // 2. Find large files that might cause memory issues
  output += 'Large Files (over 5MB):\n';
  
  let allLargeFiles = [];
  for (const checkPath of checkPaths) {
    console.log(`Scanning ${checkPath} for large files...`);
    const largeFiles = await findLargeFiles(checkPath, largeFileSizeThreshold);
    allLargeFiles = [...allLargeFiles, ...largeFiles];
  }
  
  if (allLargeFiles.length > 0) {
    allLargeFiles.sort((a, b) => b.size - a.size);
    
    for (const file of allLargeFiles) {
      output += `- ${file.path} (${file.formattedSize})\n`;
    }
  } else {
    output += '- No large files found\n';
  }
  output += '\n';
  
  // 3. Node.js settings
  output += 'Node.js Memory Settings:\n';
  try {
    const { stdout } = await exec('node -e "console.log(JSON.stringify(process.memoryUsage()))"');
    const nodeMemory = JSON.parse(stdout);
    
    output += `- RSS: ${formatMemorySize(nodeMemory.rss)}\n`;
    output += `- Heap Total: ${formatMemorySize(nodeMemory.heapTotal)}\n`;
    output += `- Heap Used: ${formatMemorySize(nodeMemory.heapUsed)}\n`;
    
    const { stdout: maxOld } = await exec('node --v8-options | grep -i "old_space"');
    output += `- V8 Options: \n${maxOld}\n`;
  } catch (error) {
    output += `- Error retrieving Node.js memory settings: ${error.message}\n`;
  }
  
  // 4. Recommendations
  output += '\nRecommendations:\n';
  output += '- Increase Node.js memory: NODE_OPTIONS=--max-old-space-size=4096 npm run dev\n';
  output += '- Use chunked file processing for large file uploads\n';
  output += '- Implement pagination for large dataset tables\n';
  output += '- Ensure proper cleanup of temporary files on the server\n';
  output += '- Monitor memory usage during file processing operations\n';
  
  // Write report to file
  fs.writeFileSync(outputFile, output);
  console.log(`Memory analysis complete. Report saved to ${outputFile}`);
  console.log(output);
}

// Run the analysis
analyzeMemoryUsage().catch(error => {
  console.error('Error running memory analysis:', error);
  process.exit(1);
});
