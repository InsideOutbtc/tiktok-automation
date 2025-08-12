# [PROJECT] - DEFI PROTOCOL INTEGRATION
**PRP ID**: DEFI-[PROTOCOL]-[NUMBER]  
**Generated**: [DATE]  
**Purpose**: Integrate [SPECIFIC DEFI FUNCTIONALITY]  
**Protocol**: [ETHEREUM/POLYGON/ARBITRUM/ETC]  
**TVL Target**: $[AMOUNT]  

---

## 💎 DEFI OBJECTIVE

[Description of DeFi integration goals, protocol interactions, and financial mechanisms to implement. Include yield strategies and risk management.]

**Protocol Type**: [AMM/Lending/Yield/Derivatives/Aggregator]  
**Chain**: [BLOCKCHAIN]  
**Expected Yield**: [X]% APY  
**Risk Level**: [LOW/MEDIUM/HIGH]  
**Audit Status**: [REQUIRED/COMPLETED]  

---

## 🎯 DEFI IMPLEMENTATION

### PHASE 1: Smart Contract Architecture
**Goal**: Deploy secure and efficient smart contracts

```solidity
// Core DeFi contract structure
pragma solidity ^0.8.19;

contract DeFiProtocol {
    // State variables
    mapping(address => uint256) public balances;
    mapping(address => mapping(address => uint256)) public allowances;
    
    uint256 public totalSupply;
    uint256 public constant FEE_PERCENTAGE = 30; // 0.3%
    
    // Events
    event Deposit(address indexed user, uint256 amount);
    event Withdrawal(address indexed user, uint256 amount);
    event Swap(address indexed user, uint256 amountIn, uint256 amountOut);
    
    // Core functions
    function deposit() external payable {
        require(msg.value > 0, "Invalid amount");
        balances[msg.sender] += msg.value;
        emit Deposit(msg.sender, msg.value);
    }
}
```

**Smart Contract Components**:
- [ ] Core protocol contracts
- [ ] Proxy upgradeability pattern
- [ ] Access control implementation
- [ ] Emergency pause mechanism
- [ ] Fee management system

### PHASE 2: DeFi Integrations
**Goal**: Connect with major DeFi protocols

```javascript
// DeFi integration layer
const defiIntegrations = {
  dex: {
    uniswap_v3: {
      router: '0x...',
      factory: '0x...',
      positions_nft: '0x...'
    },
    sushiswap: {
      router: '0x...',
      masterchef: '0x...'
    }
  },
  lending: {
    aave_v3: {
      pool: '0x...',
      oracle: '0x...'
    },
    compound_v3: {
      comet: '0x...'
    }
  },
  yield: {
    yearn: {
      registry: '0x...',
      vaults: []
    },
    convex: {
      booster: '0x...'
    }
  }
};
```

**Integration Features**:
- [ ] DEX aggregation
- [ ] Lending protocol integration
- [ ] Yield optimization
- [ ] Liquidity provisioning
- [ ] Cross-protocol composability

### PHASE 3: Risk Management & Security
**Goal**: Implement comprehensive risk controls

```javascript
// Risk management system
const riskManagement = {
  monitoring: {
    price_oracles: ['chainlink', 'uniswap_twap', 'tellor'],
    health_factor: 1.5,
    liquidation_threshold: 0.8,
    slippage_protection: 0.03 // 3%
  },
  controls: {
    position_limits: true,
    withdrawal_timelock: 86400, // 24 hours
    emergency_shutdown: true,
    multisig_required: 3 // of 5
  },
  insurance: {
    protocol_coverage: 'nexus_mutual',
    funds_allocation: 0.02, // 2% of TVL
    claim_process: 'automated'
  }
};
```

**Risk Controls**:
- [ ] Oracle redundancy
- [ ] Liquidation engine
- [ ] Circuit breakers
- [ ] Insurance integration
- [ ] Audit completion

---

## 📊 DEFI ANALYTICS

### Protocol Metrics
```javascript
// Key DeFi metrics
const protocolMetrics = {
  tvl: {
    current: 0,
    target: 10000000, // $10M
    growth_rate: 0.15 // 15% monthly
  },
  volume: {
    daily: 0,
    fees_generated: 0,
    unique_users: 0
  },
  yield: {
    base_apy: 0.05,
    boost_apy: 0.12,
    total_apy: 0.17
  },
  health: {
    utilization_rate: 0,
    collateral_ratio: 0,
    bad_debt: 0
  }
};
```

### Financial Projections
| Month | TVL | Daily Volume | Fees Generated | APY |
|-------|-----|--------------|----------------|-----|
| Month 1 | $1M | $100K | $300 | 12% |
| Month 3 | $5M | $500K | $1,500 | 15% |
| Month 6 | $10M | $1M | $3,000 | 17% |
| Month 12 | $25M | $2.5M | $7,500 | 20% |

---

## 🔐 SECURITY ARCHITECTURE

### Smart Contract Security
```solidity
// Security patterns implementation
abstract contract SecurityBase {
    // Reentrancy guard
    uint256 private constant _NOT_ENTERED = 1;
    uint256 private constant _ENTERED = 2;
    uint256 private _status;
    
    modifier nonReentrant() {
        require(_status != _ENTERED, "ReentrancyGuard: reentrant call");
        _status = _ENTERED;
        _;
        _status = _NOT_ENTERED;
    }
    
    // Access control
    mapping(bytes32 => mapping(address => bool)) private _roles;
    
    modifier onlyRole(bytes32 role) {
        require(hasRole(role, msg.sender), "Access denied");
        _;
    }
    
    // Pause mechanism
    bool private _paused;
    
    modifier whenNotPaused() {
        require(!_paused, "Contract paused");
        _;
    }
}
```

### Audit Requirements
- [ ] Code review by security team
- [ ] Automated security scanning
- [ ] Formal verification
- [ ] Bug bounty program
- [ ] External audit (Tier 1 firm)

---

## 💰 TOKENOMICS

### Token Distribution
```javascript
// Token economics
const tokenomics = {
  total_supply: 100000000, // 100M tokens
  distribution: {
    liquidity_mining: 0.40, // 40%
    team: 0.15, // 15% (vested)
    treasury: 0.20, // 20%
    investors: 0.15, // 15%
    community: 0.10 // 10%
  },
  emissions: {
    schedule: 'halving_yearly',
    initial_rate: 1000, // tokens/day
    burn_mechanism: true
  },
  utility: {
    governance: true,
    fee_sharing: true,
    boosting: true,
    collateral: true
  }
};
```

---

## 🌉 CROSS-CHAIN FEATURES

### Bridge Integration
```javascript
// Cross-chain functionality
const crossChain = {
  bridges: {
    native: 'LayerZero',
    supported: ['Ethereum', 'Polygon', 'Arbitrum', 'Optimism'],
    security: 'optimistic_validation'
  },
  liquidity: {
    unified: true,
    rebalancing: 'automatic',
    incentives: 'cross_chain_rewards'
  }
};
```

---

## 🔄 MCP INTEGRATION FOR DEFI

### REF Server
- Solidity documentation
- DeFi protocol docs
- Web3 library references
- Security best practices

### SEMGREP Server
- Smart contract scanning
- Vulnerability detection
- Gas optimization
- Upgrade safety checks

### PIECES Server
- DeFi patterns library
- Tested integrations
- Security templates
- Yield strategies

### EXA Server
- Protocol research
- Yield comparisons
- Security incidents
- Market analysis

### PLAYWRIGHT Server
- dApp UI testing
- Wallet integration testing
- Transaction flow validation
- Multi-chain testing

---

## 📋 DEFI VALIDATION

### Protocol Testing
- [ ] Unit tests (100% coverage)
- [ ] Integration tests completed
- [ ] Mainnet fork testing
- [ ] Stress testing passed
- [ ] Economic attack vectors tested

### Launch Checklist
- [ ] Smart contracts deployed
- [ ] Liquidity bootstrapped
- [ ] Oracles configured
- [ ] Monitoring active
- [ ] Documentation complete

---

## 🎯 EXECUTION COMMAND

```bash
# Deploy DeFi protocol:
"Deploy this DeFi PRP with maximum security and optimal yield generation strategies"
```

---

**PROJECTED TVL**: $[AMOUNT]  
**EXPECTED APY**: [X]%  
**SECURITY SCORE**: [A-F]  
**RISK RATING**: [1-5]