---
description: Performance optimization workflow. Profiling, bottleneck identification, optimization implementation.
---

# /performance - Performance Optimization Workflow

Systematic approach to identifying and fixing performance issues.

// turbo-all

## Steps

### 1. Define Metrics
Ask the user:
- What's slow? (page load, API, build)
- What's the current performance?
- What's the target performance?
- How do you measure? (Lighthouse, APM, custom)

### 2. Establish Baseline
```bash
# Web: Lighthouse
npx lighthouse https://your-site.com --output=json --output-path=./baseline.json

# Node.js: Profile
node --prof app.js
node --prof-process isolate-*.log > profile.txt

# Build time
time npm run build
```

### 3. Profile & Identify Bottlenecks

**Web Performance:**
- Largest Contentful Paint (LCP)
- First Input Delay (FID)
- Cumulative Layout Shift (CLS)
- Time to First Byte (TTFB)

**Backend Performance:**
- Response time (p50, p95, p99)
- Throughput (requests/second)
- Memory usage
- CPU utilization
- Database query time

### 4. Common Optimization Patterns

**Frontend:**
| Issue | Solution |
|-------|----------|
| Large bundle | Code splitting, tree shaking |
| Slow images | WebP, lazy loading, CDN |
| Render blocking | Defer scripts, critical CSS |
| Layout shifts | Set dimensions, font-display |
| Too many requests | HTTP/2, bundling, caching |

**Backend:**
| Issue | Solution |
|-------|----------|
| Slow queries | Indexes, query optimization |
| N+1 queries | Eager loading, batching |
| No caching | Redis, in-memory cache |
| Sync operations | Async, queues |
| Memory leaks | Profiling, proper cleanup |

### 5. Implement Fixes

Priority order:
1. Quick wins (high impact, low effort)
2. Critical bottlenecks
3. Incremental improvements

For each fix:
1. Implement change
2. Measure improvement
3. Document before/after

### 6. Verify Improvements
```bash
# Re-run Lighthouse
npx lighthouse https://your-site.com --output=json --output-path=./after.json

# Compare
node -e "
const before = require('./baseline.json');
const after = require('./after.json');
console.log('LCP:', before.audits['largest-contentful-paint'].numericValue, '->', after.audits['largest-contentful-paint'].numericValue);
"
```

### 7. Set Up Monitoring

Implement ongoing monitoring:
- Core Web Vitals tracking
- APM (New Relic, Datadog)
- Custom metrics
- Alerting for regressions

## Performance Checklist

- [ ] Baseline established
- [ ] Bottlenecks identified
- [ ] Fixes implemented
- [ ] Improvements verified
- [ ] Monitoring in place
- [ ] Documentation updated
