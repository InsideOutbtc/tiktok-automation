# [PROJECT] - PERFORMANCE OPTIMIZATION
**PRP ID**: PERF-[AREA]-[NUMBER]  
**Generated**: [DATE]  
**Purpose**: Achieve [SPECIFIC PERFORMANCE GOAL]  
**Target Metric**: [METRIC] < [TARGET]ms  

---

## ⚡ PERFORMANCE OBJECTIVE

[Clear description of performance goals, current bottlenecks, and expected improvements. Include specific metrics and user impact.]

**Current Performance**: [CURRENT METRICS]  
**Target Performance**: [TARGET METRICS]  
**Improvement**: [X]% faster  
**User Impact**: [DESCRIPTION]  

---

## 🎯 OPTIMIZATION STRATEGY

### PHASE 1: Performance Analysis
**Goal**: Identify and quantify performance bottlenecks

```javascript
// Performance profiling setup
const performanceConfig = {
  metrics: {
    ttfb: 'Time to First Byte',
    fcp: 'First Contentful Paint',
    lcp: 'Largest Contentful Paint',
    fid: 'First Input Delay',
    cls: 'Cumulative Layout Shift',
    tti: 'Time to Interactive'
  },
  targets: {
    ttfb: '<200ms',
    fcp: '<1000ms',
    lcp: '<2500ms',
    fid: '<100ms',
    cls: '<0.1',
    tti: '<3000ms'
  }
};
```

**Analysis Areas**:
- [ ] Frontend rendering performance
- [ ] Backend API response times
- [ ] Database query optimization
- [ ] Network latency reduction
- [ ] Resource loading optimization

### PHASE 2: Core Optimizations
**Goal**: Implement high-impact performance improvements

```javascript
// Optimization implementations
const optimizations = {
  frontend: {
    code_splitting: true,
    lazy_loading: true,
    tree_shaking: true,
    minification: true,
    compression: 'brotli',
    caching: 'aggressive'
  },
  backend: {
    query_optimization: true,
    connection_pooling: true,
    response_caching: true,
    async_processing: true,
    load_balancing: true
  },
  infrastructure: {
    cdn_implementation: true,
    edge_computing: true,
    auto_scaling: true,
    resource_optimization: true
  }
};
```

**Optimization Tasks**:
- [ ] Implement code splitting
- [ ] Optimize database queries
- [ ] Enable response caching
- [ ] Configure CDN
- [ ] Implement lazy loading

### PHASE 3: Advanced Performance Features
**Goal**: Push performance to the limits

```javascript
// Advanced optimizations
const advancedFeatures = {
  preloading: {
    critical_resources: true,
    predictive_prefetch: true,
    resource_hints: true,
    priority_hints: true
  },
  rendering: {
    virtual_scrolling: true,
    request_idle_callback: true,
    web_workers: true,
    offscreen_canvas: true
  },
  networking: {
    http3_quic: true,
    connection_coalescing: true,
    early_hints: true,
    server_push: true
  }
};
```

**Advanced Features**:
- [ ] Predictive prefetching
- [ ] Web Worker offloading
- [ ] HTTP/3 implementation
- [ ] Edge computing
- [ ] Real-time optimization

---

## 📊 PERFORMANCE METRICS

### Load Time Breakdown
| Component | Current | Target | Improvement |
|-----------|---------|--------|-------------|
| Server Response | 400ms | 100ms | 75% |
| JS Parse/Execute | 800ms | 300ms | 62.5% |
| CSS Processing | 200ms | 50ms | 75% |
| Image Loading | 1200ms | 400ms | 66.7% |
| Total Load Time | 2600ms | 850ms | 67.3% |

### Runtime Performance
```javascript
// Performance targets
const runtimeTargets = {
  fps: 60, // Smooth animations
  memory_usage: '<100MB',
  cpu_usage: '<30%',
  battery_impact: 'minimal',
  network_requests: '<50/page'
};
```

---

## 🚀 OPTIMIZATION TECHNIQUES

### Frontend Optimizations
```javascript
// Bundle optimization
const bundleConfig = {
  chunks: {
    vendor: 'node_modules',
    common: 'shared components',
    routes: 'lazy loaded'
  },
  optimization: {
    usedExports: true,
    sideEffects: false,
    concatenateModules: true,
    minimize: true
  }
};

// Image optimization
const imageOptimization = {
  formats: ['webp', 'avif'],
  lazy_loading: true,
  responsive_images: true,
  compression: 85,
  cdn_delivery: true
};
```

### Backend Optimizations
```javascript
// Database optimization
const dbOptimization = {
  indexing: 'strategic',
  query_planning: 'optimized',
  connection_pooling: {
    min: 10,
    max: 100,
    idle_timeout: 30000
  },
  caching: {
    redis: true,
    query_cache: true,
    object_cache: true
  }
};

// API optimization
const apiOptimization = {
  response_compression: true,
  pagination: 'cursor-based',
  field_selection: 'graphql-like',
  batch_operations: true,
  rate_limiting: 'smart'
};
```

---

## ⚙️ PERFORMANCE MONITORING

### Real-Time Monitoring
```javascript
// Monitoring setup
const monitoring = {
  metrics: {
    apm: 'Application Performance Monitoring',
    rum: 'Real User Monitoring',
    synthetic: 'Synthetic Monitoring',
    logging: 'Structured Logging'
  },
  alerts: {
    response_time: '>500ms',
    error_rate: '>1%',
    cpu_usage: '>80%',
    memory_usage: '>90%'
  },
  dashboards: {
    executive: 'High-level metrics',
    technical: 'Detailed performance',
    user: 'User experience metrics'
  }
};
```

### Performance Budgets
```javascript
// Budget enforcement
const performanceBudget = {
  javascript: '170KB',
  css: '50KB',
  images: '500KB',
  fonts: '100KB',
  total: '1MB',
  enforcement: 'strict'
};
```

---

## 🔧 INFRASTRUCTURE OPTIMIZATION

### Scaling Strategy
```yaml
# Auto-scaling configuration
scaling:
  horizontal:
    min_instances: 2
    max_instances: 100
    target_cpu: 70%
    target_memory: 80%
  vertical:
    cpu_upgrade: auto
    memory_upgrade: auto
    disk_upgrade: auto
```

### CDN Configuration
```javascript
// CDN optimization
const cdnConfig = {
  providers: ['cloudflare', 'fastly'],
  caching: {
    static: '1 year',
    dynamic: '5 minutes',
    api: 'varies'
  },
  optimization: {
    minification: true,
    compression: true,
    image_optimization: true,
    http2_push: true
  }
};
```

---

## 🔄 MCP INTEGRATION FOR PERFORMANCE

### REF Server
- Performance optimization guides
- Framework-specific tips
- Caching strategies

### SEMGREP
- Performance anti-pattern detection
- Security-performance balance
- Resource leak detection

### PIECES
- Optimization patterns
- Performance snippets
- Proven solutions

### EXA
- Performance best practices
- Benchmark comparisons
- Latest techniques

### PLAYWRIGHT
- Performance testing
- Load testing
- User experience validation

---

## 📋 PERFORMANCE VALIDATION

### Testing Strategy
- [ ] Load testing completed
- [ ] Stress testing passed
- [ ] Endurance testing verified
- [ ] Spike testing successful
- [ ] Volume testing confirmed

### Performance Checklist
- [ ] Core Web Vitals passing
- [ ] Lighthouse score > 95
- [ ] Page weight < 1MB
- [ ] Time to Interactive < 3s
- [ ] No memory leaks

---

## 🎯 EXECUTION COMMAND

```bash
# Execute performance optimization:
"Implement this performance PRP targeting sub-second load times with Maximum Velocity Mode"
```

---

**PERFORMANCE GAIN**: [X]% improvement  
**LOAD TIME**: [CURRENT]ms → [TARGET]ms  
**USER EXPERIENCE**: [RATING] improvement  
**COMPLEXITY**: [LOW/MEDIUM/HIGH]