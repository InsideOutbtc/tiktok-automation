#!/usr/bin/env node

/**
 * PRP Generation Command
 * Usage: node prp-generate.js <template-type> <prp-name>
 * 
 * Example: node prp-generate.js revenue "payment-optimization"
 * This will create: 2024-01-28-payment-optimization.md in the active folder
 */

const fs = require('fs');
const path = require('path');

const PRP_TEMPLATES = {
  'base': 'General platform enhancement - Use for standard features',
  'revenue': 'Financial system optimization - Use for monetization features',
  'agent': 'Agent ecosystem development - Use for AI/autonomous features',
  'performance': 'Speed optimization - Use for performance improvements',
  'security': 'Security enhancement - Use for security features',
  'defi': 'DeFi protocol integration - Use for blockchain/crypto features'
};

const TEMPLATE_PLACEHOLDERS = {
  '[PROJECT NAME]': 'Project',
  '[BRIEF DESCRIPTION]': 'Enhancement',
  '[CATEGORY]': 'GENERAL',
  '[FEATURE]': 'FEATURE',
  '[NUMBER]': '001',
  '[DATE]': new Date().toISOString().split('T')[0],
  '[ONE LINE PURPOSE]': 'Implement new functionality',
  '[SPECIFIC GOAL/METRIC]': 'Achieve specific improvement',
  '[PROJECT]': 'Project',
  '[SPECIFIC APPROACH]': 'optimization approach',
  '[AMOUNT]': 'X',
  '[TIMEFRAME]': '30 days',
  '[TYPE]': 'SYSTEM',
  '[SPECIFIC FUNCTION]': 'task automation',
  '[CORE CAPABILITY]': 'autonomous decision making',
  '[AREA]': 'SYSTEM',
  '[SPECIFIC PERFORMANCE GOAL]': 'sub-second response time',
  '[METRIC]': 'Response time',
  '[TARGET]': '100',
  '[SPECIFIC SECURITY MEASURE]': 'comprehensive security audit',
  '[CRITICAL/HIGH/MEDIUM]': 'HIGH',
  '[STANDARDS: OWASP/PCI-DSS/HIPAA/SOC2]': 'OWASP',
  '[PROTOCOL]': 'LENDING',
  '[SPECIFIC DEFI FUNCTIONALITY]': 'yield optimization',
  '[ETHEREUM/POLYGON/ARBITRUM/ETC]': 'ETHEREUM',
  '[BLOCKCHAIN]': 'Ethereum'
};

function generatePRP(templateType, prpName) {
  // Validate template type
  if (!PRP_TEMPLATES[templateType]) {
    console.error(`❌ Invalid template type: ${templateType}`);
    console.log('\nAvailable templates:');
    Object.entries(PRP_TEMPLATES).forEach(([key, desc]) => {
      console.log(`  ${key}: ${desc}`);
    });
    process.exit(1);
  }

  // Read template
  const templatePath = path.join(__dirname, '../templates', `${templateType}-prp.md`);
  if (!fs.existsSync(templatePath)) {
    console.error(`❌ Template file not found: ${templatePath}`);
    process.exit(1);
  }

  let template = fs.readFileSync(templatePath, 'utf8');
  
  // Generate dynamic values
  const timestamp = new Date().toISOString().split('T')[0];
  const prpId = `${templateType.toUpperCase()}-${prpName.toUpperCase().replace(/[^A-Z0-9]/g, '-')}-001`;
  
  // Replace placeholders
  template = template.replace(/\[PROJECT NAME\]/g, prpName);
  template = template.replace(/\[PROJECT\]/g, prpName);
  template = template.replace(/\[DATE\]/g, timestamp);
  template = template.replace(/\[CATEGORY\]-\[FEATURE\]-\[NUMBER\]/g, prpId);
  template = template.replace(/\[TYPE\]-\[FEATURE\]-\[NUMBER\]/g, prpId);
  template = template.replace(/\[AREA\]-\[FEATURE\]-\[NUMBER\]/g, prpId);
  template = template.replace(/\[PROTOCOL\]-\[FEATURE\]-\[NUMBER\]/g, prpId);
  
  // Replace remaining placeholders with defaults
  Object.entries(TEMPLATE_PLACEHOLDERS).forEach(([placeholder, value]) => {
    const regex = new RegExp(placeholder.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
    template = template.replace(regex, value);
  });
  
  // Ensure active directory exists
  const activeDir = path.join(__dirname, '../active');
  if (!fs.existsSync(activeDir)) {
    fs.mkdirSync(activeDir, { recursive: true });
  }
  
  // Generate output filename
  const outputFilename = `${timestamp}-${prpName.toLowerCase().replace(/[^a-z0-9]/g, '-')}.md`;
  const outputPath = path.join(activeDir, outputFilename);
  
  // Write file
  fs.writeFileSync(outputPath, template);
  
  console.log(`✅ PRP generated successfully!`);
  console.log(`📄 File: ${outputPath}`);
  console.log(`🆔 PRP ID: ${prpId}`);
  console.log(`📋 Template: ${templateType}`);
  console.log(`\n🚀 Next steps:`);
  console.log(`1. Review and customize the PRP in ${outputFilename}`);
  console.log(`2. Run validation: node ../validation/prp-validator.js "${outputPath}"`);
  console.log(`3. Execute with Claude: "Execute PRP ${prpId}"`);
}

// CLI execution
const [,, templateType, ...prpNameParts] = process.argv;
const prpName = prpNameParts.join(' ');

if (!templateType || !prpName) {
  console.log('📋 PRP Generator - Create PRPs from templates\n');
  console.log('Usage: node prp-generate.js <template-type> <prp-name>\n');
  console.log('Available templates:');
  Object.entries(PRP_TEMPLATES).forEach(([key, desc]) => {
    console.log(`  ${key.padEnd(12)} - ${desc}`);
  });
  console.log('\nExamples:');
  console.log('  node prp-generate.js base "user dashboard"');
  console.log('  node prp-generate.js revenue "subscription system"');
  console.log('  node prp-generate.js agent "code analyzer"');
  console.log('  node prp-generate.js performance "api optimization"');
  console.log('  node prp-generate.js security "auth upgrade"');
  console.log('  node prp-generate.js defi "yield aggregator"');
  process.exit(1);
}

try {
  generatePRP(templateType, prpName);
} catch (error) {
  console.error(`❌ Error generating PRP: ${error.message}`);
  process.exit(1);
}