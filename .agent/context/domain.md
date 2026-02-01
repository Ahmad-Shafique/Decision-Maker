# Domain Context - Values & Principles Framework

## Core Terminology

### Values
**Definition**: Fundamental beliefs that guide all decisions. These are the "why" behind actions.

**The 4 Core Values** (in priority order):
1. **Justice** - Being ethically good
2. **Contribution** - Enabling and helping others
3. **Family** - Having a thriving family
4. **Generosity** - Treating people as well as possible

**Optional Values**: Accuracy, Achievement, Autonomy, Challenge, Dependability, Forgiveness, 
Genuineness, Health, Humility, Moderation, Nonconformity, Purpose, Realism, Responsibility, 
Self-knowledge, Tolerance

### Principles
**Definition**: Actionable guidelines derived from values. These are the "how" of decision-making.

**Structure**: Each principle has:
- **ID**: Sequential number (1-45)
- **Title**: Short descriptive name
- **Sub-principles**: Lettered items (a, b, c...) with specific guidance
- **Related SOPs**: References to relevant procedures
- **Tags**: Categories for search/matching

**Categories of Principles**:
- Self-Management (1, 3, 16, 17, 21, 27)
- Communication (4, 15, 31, 33, 37)
- Decision-Making (7, 9, 13, 14, 30, 35)
- Relationships (5, 8, 18, 20, 38)
- Professional (6, 11, 23, 28, 34)
- Growth & Learning (2, 6, 22, 29)

### Standard Operating Procedures (SOPs)
**Definition**: Step-by-step processes for recurring situations. These are triggered by specific conditions.

**Structure**: Each SOP has:
- **Name**: Descriptive title
- **Purpose**: Which principle(s) it executes
- **Trigger**: When to activate this SOP
- **Steps**: Numbered procedural steps

**The 9 SOPs**:
1. Daily Targets & Review
2. Strategic Meeting Preparation
3. Building Trust & Discretion
4. Meeting Communication & Boundaries
5. Social Event Evaluation
6. Consequential Pauses
7. Alarm-Bell Verification
8. Information Consumption Audit
9. State & Energy Management

### Situations
**Definition**: Real-world scenarios that require principle application.

**Attributes**:
- **Description**: What happened / what is happening
- **Context**: Facts, constraints, stakeholders involved
- **Emotions**: Feelings associated (tracked separately for clarity)
- **Stakes**: Low / Medium / High / Critical
- **Domain**: Personal, Professional, Family, Financial, Health

## Business Rules

1. **Value Priority**: When principles conflict, prefer those aligned with higher-priority values
2. **SOP Triggers**: SOPs activate based on situation characteristics, not manual selection
3. **Principle Cascading**: Related principles often apply together
4. **Historical Comparison**: Past decisions can be re-evaluated against current principles

## Important Invariants

- Values are immutable during system operation
- Principles can be refined but core intent should remain
- Every decision recommendation must cite applicable principles
- Historical analysis must distinguish actual outcome from recommended action
