#!/usr/bin/env node

/**
 * PRP Validation Script
 * Validates PRPs against Constitutional AI standards and best practices
 * 
 * Usage: node prp-validator.js <prp-file>
 * Example: node prp-validator.js ../active/2024-01-28-payment-system.md
 */

const fs = require('fs');
const path = require('path');

// Validation criteria with weights
const VALIDATION_CRITERIA = {
  constitutional_ai: {
    weight: 0.30,
    checks: [
      { pattern: /MAXIMUM VELOCITY MODE/i, points: 10, message: 'Maximum Velocity Mode referenced' },
      { pattern: /CONTEXT ENGINEERING/i, points: 10, message: 'Context Engineering included' },
      { pattern: /ERROR HANDLING/i, points: 10, message: 'Error Handling strategy defined' },
      { pattern: /Constitutional AI|AI AGENT PROTOCOL/i, points: 10, message: 'Constitutional AI principles applied' }
    ]
  },
  system_integration: {
    weight: 0.30,
    checks: [
      { pattern: /\$[\d,]+|revenue|monetization/i, points: 10, message: 'Revenue/financial considerations' },
      { pattern: /agent|autonomous|ecosystem/i, points: 10, message: 'Agent/automation features' },
      { pattern: /performance|optimization|<\d+ms/i, points: 10, message: 'Performance optimization targets' },
      { pattern: /security|encryption|authentication/i, points: 10, message: 'Security measures included' }
    ]
  },
  mcp_integration: {
    weight: 0.20,
    checks: [
      { pattern: /REF Server|REF:|doc.*access/i, points: 5, message: 'REF Server integration' },
      { pattern: /SEMGREP|security.*scan/i, points: 5, message: 'SEMGREP integration' },
      { pattern: /PIECES|pattern.*store/i, points: 5, message: 'PIECES integration' },
      { pattern: /EXA|research|best.*practices/i, points: 5, message: 'EXA integration' },
      { pattern: /PLAYWRIGHT|ui.*test/i, points: 5, message: 'PLAYWRIGHT integration' }
    ]
  },
  quality_metrics: {
    weight: 0.20,
    checks: [
      { pattern: /SUCCESS CRITERIA|VALIDATION|METRICS/i, points: 10, message: 'Success criteria defined' },
      { pattern: /\[ \].*|checklist|TODO/i, points: 10, message: 'Actionable checklist items' },
      { pattern: /PHASE \d+|IMPLEMENTATION|BLUEPRINT/i, points: 10, message: 'Clear implementation phases' },
      { pattern: /```[\s\S]*?```/m, points: 10, message: 'Code examples provided' }
    ]
  }
};

function validatePRP(prpPath) {
  // Check if file exists
  if (!fs.existsSync(prpPath)) {
    console.error(`❌ File not found: ${prpPath}`);
    process.exit(1);
  }

  const content = fs.readFileSync(prpPath, 'utf8');
  const results = {
    total_score: 0,
    max_score: 0,
    passed_checks: [],
    failed_checks: [],
    category_scores: {}
  };

  console.log(`\n🔍 Validating PRP: ${path.basename(prpPath)}\n`);
  console.log('─'.repeat(60));

  // Run validation checks
  Object.entries(VALIDATION_CRITERIA).forEach(([category, config]) => {
    console.log(`\n📋 ${category.replace(/_/g, ' ').toUpperCase()}`);
    
    let categoryScore = 0;
    let categoryMax = 0;

    config.checks.forEach(check => {
      categoryMax += check.points;
      
      if (check.pattern.test(content)) {
        categoryScore += check.points;
        results.passed_checks.push(`✅ ${check.message}`);
        console.log(`  ✅ ${check.message} (+${check.points} pts)`);
      } else {
        results.failed_checks.push(`❌ ${check.message}`);
        console.log(`  ❌ ${check.message} (0 pts)`);
      }
    });

    const weightedScore = (categoryScore / categoryMax) * config.weight * 100;
    results.category_scores[category] = {
      raw: categoryScore,
      max: categoryMax,
      percentage: (categoryScore / categoryMax) * 100,
      weighted: weightedScore
    };

    results.total_score += weightedScore;
    results.max_score += config.weight * 100;

    console.log(`  📊 Category Score: ${categoryScore}/${categoryMax} (${Math.round((categoryScore / categoryMax) * 100)}%)`);
  });

  // Additional content checks
  console.log(`\n📋 CONTENT ANALYSIS`);
  const lines = content.split('\n').length;
  const codeBlocks = (content.match(/```/g) || []).length / 2;
  const checklistItems = (content.match(/\[ \]/g) || []).length;
  const phases = (content.match(/PHASE \d+/gi) || []).length;

  console.log(`  📄 Document length: ${lines} lines`);
  console.log(`  💻 Code blocks: ${codeBlocks}`);
  console.log(`  ☑️  Checklist items: ${checklistItems}`);
  console.log(`  🎯 Implementation phases: ${phases}`);

  // Final score calculation
  console.log('\n' + '─'.repeat(60));
  console.log('\n📊 FINAL VALIDATION RESULTS\n');

  Object.entries(results.category_scores).forEach(([category, scores]) => {
    console.log(`${category.replace(/_/g, ' ').toUpperCase()}: ${Math.round(scores.percentage)}% (Weight: ${Math.round(scores.weighted)}%)`);
  });

  const finalScore = Math.round(results.total_score);
  console.log(`\n🎯 TOTAL SCORE: ${finalScore}%`);

  // Pass/Fail determination
  const passing = finalScore >= 80;
  
  if (passing) {
    console.log('\n✅ VALIDATION PASSED - Ready for execution!');
    console.log('\n🚀 Next steps:');
    console.log('1. Review any failed checks above');
    console.log('2. Make optional improvements if desired');
    console.log('3. Execute with Claude using Maximum Velocity Mode');
  } else {
    console.log('\n❌ VALIDATION FAILED - Improvements needed');
    console.log('\n📝 Required improvements:');
    results.failed_checks.forEach(check => console.log(`  ${check}`));
    console.log('\n💡 Tips:');
    console.log('- Add Constitutional AI principles (Maximum Velocity Mode)');
    console.log('- Include MCP server integrations');
    console.log('- Define clear success criteria');
    console.log('- Add implementation phases with code examples');
  }

  // Generate improvement suggestions
  if (finalScore < 100) {
    console.log('\n💡 IMPROVEMENT SUGGESTIONS:');
    
    if (results.category_scores.constitutional_ai.percentage < 100) {
      console.log('- Add more Constitutional AI references and patterns');
    }
    if (results.category_scores.mcp_integration.percentage < 100) {
      console.log('- Integrate more MCP servers (REF, SEMGREP, PIECES, EXA, PLAYWRIGHT)');
    }
    if (results.category_scores.quality_metrics.percentage < 100) {
      console.log('- Add more specific success metrics and validation criteria');
    }
    if (codeBlocks < 3) {
      console.log('- Include more code examples and implementation details');
    }
  }

  console.log('\n' + '─'.repeat(60) + '\n');

  return passing;
}

// CLI execution
const [,, prpPath] = process.argv;

if (!prpPath) {
  console.log('📋 PRP Validator - Validate PRPs against standards\n');
  console.log('Usage: node prp-validator.js <prp-file>\n');
  console.log('Examples:');
  console.log('  node prp-validator.js ../active/2024-01-28-payment-system.md');
  console.log('  node prp-validator.js /path/to/my-prp.md\n');
  console.log('Validation checks for:');
  console.log('  - Constitutional AI compliance (30%)');
  console.log('  - System integration features (30%)');
  console.log('  - MCP server integration (20%)');
  console.log('  - Quality standards (20%)');
  console.log('\nPassing score: 80% or higher');
  process.exit(1);
}

try {
  const passed = validatePRP(prpPath);
  process.exit(passed ? 0 : 1);
} catch (error) {
  console.error(`❌ Error validating PRP: ${error.message}`);
  process.exit(1);
}