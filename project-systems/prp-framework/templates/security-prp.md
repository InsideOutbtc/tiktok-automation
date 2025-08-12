# [PROJECT] - SECURITY ENHANCEMENT
**PRP ID**: SEC-[FEATURE]-[NUMBER]  
**Generated**: [DATE]  
**Purpose**: Implement [SPECIFIC SECURITY MEASURE]  
**Security Level**: [CRITICAL/HIGH/MEDIUM]  
**Compliance**: [STANDARDS: OWASP/PCI-DSS/HIPAA/SOC2]  

---

## 🛡️ SECURITY OBJECTIVE

[Clear description of security vulnerabilities to address, compliance requirements to meet, and protective measures to implement.]

**Current Security Posture**: [ASSESSMENT]  
**Target Security Level**: [GOAL]  
**Risk Reduction**: [X]%  
**Compliance Target**: [SPECIFIC STANDARDS]  

---

## 🎯 SECURITY IMPLEMENTATION

### PHASE 1: Security Assessment & Hardening
**Goal**: Identify vulnerabilities and implement core security measures

```javascript
// Security configuration
const securityConfig = {
  authentication: {
    mfa_required: true,
    password_policy: {
      min_length: 12,
      complexity: 'high',
      rotation_days: 90,
      history: 5
    },
    session_management: {
      timeout: 900, // 15 minutes
      concurrent_sessions: false,
      secure_cookies: true
    }
  },
  encryption: {
    at_rest: 'AES-256-GCM',
    in_transit: 'TLS 1.3',
    key_management: 'HSM',
    key_rotation: 'quarterly'
  }
};
```

**Security Components**:
- [ ] Authentication system hardening
- [ ] Authorization framework
- [ ] Encryption implementation
- [ ] Input validation
- [ ] Output encoding

### PHASE 2: Advanced Security Features
**Goal**: Implement defense-in-depth security measures

```javascript
// Advanced security features
const advancedSecurity = {
  threat_detection: {
    anomaly_detection: true,
    behavior_analysis: true,
    ml_powered: true,
    real_time_alerts: true
  },
  protection_mechanisms: {
    waf: 'Web Application Firewall',
    ddos_protection: 'advanced',
    rate_limiting: 'intelligent',
    geo_blocking: 'configurable',
    bot_detection: 'ml-based'
  },
  incident_response: {
    automated_containment: true,
    forensics_collection: true,
    playbook_execution: true,
    stakeholder_notification: true
  }
};
```

**Advanced Features**:
- [ ] Intrusion detection system
- [ ] Security event monitoring
- [ ] Automated threat response
- [ ] Vulnerability scanning
- [ ] Penetration testing

### PHASE 3: Compliance & Audit
**Goal**: Ensure regulatory compliance and audit readiness

```javascript
// Compliance implementation
const complianceFramework = {
  standards: {
    owasp_top_10: 'fully_addressed',
    pci_dss: 'level_1_compliant',
    gdpr: 'privacy_by_design',
    soc2: 'type_2_ready',
    iso_27001: 'aligned'
  },
  audit_capabilities: {
    logging: 'comprehensive',
    trail: 'immutable',
    reporting: 'automated',
    evidence: 'collected',
    review: 'continuous'
  }
};
```

**Compliance Tasks**:
- [ ] Audit logging implementation
- [ ] Compliance reporting
- [ ] Privacy controls
- [ ] Data governance
- [ ] Regular assessments

---

## 🔐 SECURITY CONTROLS

### Access Control
```javascript
// RBAC implementation
const accessControl = {
  model: 'role-based',
  permissions: {
    granularity: 'fine-grained',
    inheritance: true,
    delegation: 'controlled',
    review: 'periodic'
  },
  authentication: {
    methods: ['password', 'biometric', 'token'],
    strength: 'adaptive',
    step_up: 'for sensitive operations'
  },
  authorization: {
    policy_engine: 'opa',
    decision_point: 'centralized',
    enforcement: 'distributed'
  }
};
```

### Data Protection
```javascript
// Data security measures
const dataProtection = {
  classification: {
    levels: ['public', 'internal', 'confidential', 'secret'],
    handling: 'policy-based',
    labeling: 'automatic'
  },
  encryption: {
    algorithms: {
      symmetric: 'AES-256-GCM',
      asymmetric: 'RSA-4096',
      hashing: 'SHA-256',
      kdf: 'Argon2id'
    }
  },
  privacy: {
    pii_detection: 'automatic',
    anonymization: 'available',
    pseudonymization: 'configurable',
    retention: 'policy-driven'
  }
};
```

---

## 📊 SECURITY METRICS

### Vulnerability Metrics
| Category | Current | Target | Reduction |
|----------|---------|--------|-----------|
| Critical | 12 | 0 | 100% |
| High | 28 | 0 | 100% |
| Medium | 45 | 5 | 89% |
| Low | 67 | 20 | 70% |
| Info | 123 | N/A | N/A |

### Security KPIs
```javascript
// Security performance indicators
const securityKPIs = {
  mttr: '< 30 minutes', // Mean Time To Respond
  mttd: '< 5 minutes', // Mean Time To Detect
  false_positive_rate: '< 5%',
  patch_compliance: '> 99%',
  security_training: '100% completion'
};
```

---

## 🚨 THREAT MODELING

### Threat Categories
```javascript
// STRIDE threat model
const threats = {
  spoofing: {
    mitigations: ['MFA', 'certificate_pinning', 'token_validation'],
    risk_level: 'high'
  },
  tampering: {
    mitigations: ['integrity_checks', 'code_signing', 'audit_logs'],
    risk_level: 'medium'
  },
  repudiation: {
    mitigations: ['comprehensive_logging', 'digital_signatures'],
    risk_level: 'low'
  },
  information_disclosure: {
    mitigations: ['encryption', 'access_control', 'data_masking'],
    risk_level: 'high'
  },
  denial_of_service: {
    mitigations: ['rate_limiting', 'ddos_protection', 'auto_scaling'],
    risk_level: 'medium'
  },
  elevation_of_privilege: {
    mitigations: ['least_privilege', 'rbac', 'input_validation'],
    risk_level: 'critical'
  }
};
```

### Attack Surface Reduction
- [ ] Remove unnecessary services
- [ ] Disable unused features
- [ ] Minimize exposed APIs
- [ ] Implement network segmentation
- [ ] Apply principle of least privilege

---

## 🔄 SECURITY AUTOMATION

### DevSecOps Integration
```yaml
# Security pipeline
security_pipeline:
  pre_commit:
    - secret_scanning
    - dependency_check
  build:
    - sast_analysis
    - container_scanning
  deploy:
    - dast_testing
    - compliance_check
  runtime:
    - runtime_protection
    - continuous_monitoring
```

### Automated Response
```javascript
// Incident response automation
const incidentResponse = {
  detection: {
    sources: ['waf', 'ids', 'siem', 'ueba'],
    correlation: 'ml-powered',
    priority: 'risk-based'
  },
  response: {
    containment: ['isolate', 'block', 'quarantine'],
    investigation: ['collect_evidence', 'analyze_timeline'],
    remediation: ['patch', 'reconfigure', 'restore'],
    communication: ['notify_team', 'update_status']
  }
};
```

---

## 🔄 MCP INTEGRATION FOR SECURITY

### SEMGREP Server
- Continuous security scanning
- Vulnerability detection
- Secure coding patterns
- Compliance checking

### REF Server
- Security best practices
- Framework security guides
- Vulnerability databases
- Compliance documentation

### PIECES Server
- Security patterns library
- Incident response playbooks
- Secure code templates
- Compliance checklists

### EXA Server
- Threat intelligence
- Security research
- Vulnerability trends
- Attack pattern analysis

### PLAYWRIGHT Server
- Security testing automation
- Authentication flow testing
- Authorization verification
- XSS/CSRF testing

---

## 📋 SECURITY VALIDATION

### Security Testing
- [ ] Penetration testing completed
- [ ] Vulnerability assessment passed
- [ ] Security code review done
- [ ] Compliance audit passed
- [ ] Incident response tested

### Security Checklist
- [ ] All OWASP Top 10 addressed
- [ ] Encryption properly implemented
- [ ] Access controls verified
- [ ] Audit logging functional
- [ ] Incident response ready

---

## 🎯 EXECUTION COMMAND

```bash
# Execute security enhancement:
"Implement this security PRP with zero-trust architecture and continuous compliance monitoring"
```

---

**RISK REDUCTION**: [X]% decrease  
**COMPLIANCE LEVEL**: [STANDARD] compliant  
**SECURITY SCORE**: [CURRENT] → [TARGET]  
**PRIORITY**: [CRITICAL/HIGH/MEDIUM/LOW]