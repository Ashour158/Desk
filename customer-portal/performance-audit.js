/**
 * Performance audit script for the customer portal
 */

const fs = require('fs');
const path = require('path');

/**
 * Analyze bundle sizes
 */
function analyzeBundleSizes() {
  const buildDir = path.join(__dirname, 'build', 'static', 'js');
  const files = fs.readdirSync(buildDir).filter(file => file.endsWith('.js'));
  
  const bundleAnalysis = {
    totalFiles: files.length,
    totalSize: 0,
    files: [],
    recommendations: []
  };
  
  files.forEach(file => {
    const filePath = path.join(buildDir, file);
    const stats = fs.statSync(filePath);
    const sizeKB = Math.round(stats.size / 1024);
    
    bundleAnalysis.files.push({
      name: file,
      size: sizeKB,
      sizeFormatted: formatBytes(stats.size)
    });
    
    bundleAnalysis.totalSize += stats.size;
  });
  
  // Sort by size
  bundleAnalysis.files.sort((a, b) => b.size - a.size);
  
  // Add recommendations
  if (bundleAnalysis.totalSize > 500 * 1024) { // 500KB
    bundleAnalysis.recommendations.push({
      type: 'warning',
      message: 'Total bundle size is large. Consider code splitting and lazy loading.'
    });
  }
  
  const largeFiles = bundleAnalysis.files.filter(file => file.size > 100);
  if (largeFiles.length > 0) {
    bundleAnalysis.recommendations.push({
      type: 'info',
      message: `Large files detected: ${largeFiles.map(f => f.name).join(', ')}`
    });
  }
  
  return bundleAnalysis;
}

/**
 * Format bytes to human readable format
 */
function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Check for performance optimizations
 */
function checkPerformanceOptimizations() {
  const optimizations = {
    codeSplitting: false,
    lazyLoading: false,
    memoization: false,
    debouncing: false,
    imageOptimization: false,
    caching: false
  };
  
  // Check for code splitting
  const appFile = path.join(__dirname, 'src', 'App.js');
  if (fs.existsSync(appFile)) {
    const content = fs.readFileSync(appFile, 'utf8');
    if (content.includes('lazy(') && content.includes('Suspense')) {
      optimizations.codeSplitting = true;
    }
  }
  
  // Check for memoization
  const componentsDir = path.join(__dirname, 'src', 'components');
  if (fs.existsSync(componentsDir)) {
    const files = fs.readdirSync(componentsDir);
    files.forEach(file => {
      if (file.endsWith('.jsx') || file.endsWith('.js')) {
        const filePath = path.join(componentsDir, file);
        const content = fs.readFileSync(filePath, 'utf8');
        if (content.includes('React.memo') || content.includes('useMemo') || content.includes('useCallback')) {
          optimizations.memoization = true;
        }
      }
    });
  }
  
  // Check for debouncing
  const hooksDir = path.join(__dirname, 'src', 'hooks');
  if (fs.existsSync(hooksDir)) {
    const files = fs.readdirSync(hooksDir);
    files.forEach(file => {
      if (file.includes('debounce')) {
        optimizations.debouncing = true;
      }
    });
  }
  
  // Check for image optimization
  const componentsDir2 = path.join(__dirname, 'src', 'components');
  if (fs.existsSync(componentsDir2)) {
    const files = fs.readdirSync(componentsDir2);
    files.forEach(file => {
      if (file.includes('Image') || file.includes('Lazy')) {
        optimizations.imageOptimization = true;
      }
    });
  }
  
  // Check for caching
  const utilsDir = path.join(__dirname, 'src', 'utils');
  if (fs.existsSync(utilsDir)) {
    const files = fs.readdirSync(utilsDir);
    files.forEach(file => {
      if (file.includes('cache') || file.includes('serviceWorker')) {
        optimizations.caching = true;
      }
    });
  }
  
  return optimizations;
}

/**
 * Generate performance report
 */
function generatePerformanceReport() {
  console.log('🚀 Frontend Performance Audit Report');
  console.log('=====================================\n');
  
  // Bundle analysis
  console.log('📦 Bundle Analysis:');
  console.log('-------------------');
  const bundleAnalysis = analyzeBundleSizes();
  
  console.log(`Total Files: ${bundleAnalysis.totalFiles}`);
  console.log(`Total Size: ${formatBytes(bundleAnalysis.totalSize)}`);
  console.log('\nLargest Files:');
  
  bundleAnalysis.files.slice(0, 5).forEach(file => {
    console.log(`  ${file.name}: ${file.sizeFormatted}`);
  });
  
  console.log('\n📊 Bundle Size Assessment:');
  if (bundleAnalysis.totalSize < 200 * 1024) {
    console.log('✅ Excellent: Bundle size is under 200KB');
  } else if (bundleAnalysis.totalSize < 500 * 1024) {
    console.log('⚠️  Good: Bundle size is under 500KB');
  } else {
    console.log('❌ Needs Improvement: Bundle size is over 500KB');
  }
  
  // Performance optimizations
  console.log('\n🔧 Performance Optimizations:');
  console.log('------------------------------');
  const optimizations = checkPerformanceOptimizations();
  
  Object.entries(optimizations).forEach(([key, value]) => {
    const status = value ? '✅' : '❌';
    const name = key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase());
    console.log(`${status} ${name}`);
  });
  
  // Recommendations
  console.log('\n💡 Recommendations:');
  console.log('-------------------');
  
  if (!optimizations.codeSplitting) {
    console.log('• Implement code splitting with React.lazy() and Suspense');
  }
  
  if (!optimizations.memoization) {
    console.log('• Add React.memo(), useMemo(), and useCallback() for performance');
  }
  
  if (!optimizations.debouncing) {
    console.log('• Implement debouncing for search inputs and API calls');
  }
  
  if (!optimizations.imageOptimization) {
    console.log('• Add lazy loading and WebP support for images');
  }
  
  if (!optimizations.caching) {
    console.log('• Implement service worker caching and data caching');
  }
  
  // Bundle recommendations
  if (bundleAnalysis.recommendations.length > 0) {
    console.log('\n📋 Bundle Recommendations:');
    bundleAnalysis.recommendations.forEach(rec => {
      const icon = rec.type === 'warning' ? '⚠️' : 'ℹ️';
      console.log(`${icon} ${rec.message}`);
    });
  }
  
  // Performance score
  const score = calculatePerformanceScore(bundleAnalysis, optimizations);
  console.log(`\n🎯 Performance Score: ${score}/100`);
  
  if (score >= 90) {
    console.log('🏆 Excellent performance!');
  } else if (score >= 70) {
    console.log('👍 Good performance with room for improvement');
  } else {
    console.log('🔧 Performance needs significant improvement');
  }
}

/**
 * Calculate performance score
 */
function calculatePerformanceScore(bundleAnalysis, optimizations) {
  let score = 0;
  
  // Bundle size score (40 points)
  if (bundleAnalysis.totalSize < 200 * 1024) {
    score += 40;
  } else if (bundleAnalysis.totalSize < 500 * 1024) {
    score += 30;
  } else if (bundleAnalysis.totalSize < 1000 * 1024) {
    score += 20;
  } else {
    score += 10;
  }
  
  // Optimization score (60 points)
  const optimizationCount = Object.values(optimizations).filter(Boolean).length;
  score += (optimizationCount / 6) * 60;
  
  return Math.round(score);
}

// Run the audit
generatePerformanceReport();
