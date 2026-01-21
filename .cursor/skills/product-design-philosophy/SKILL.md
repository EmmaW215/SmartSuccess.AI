---
name: product-design-philosophy
description: Guides product design following modular architecture, simplicity-first principles, and comprehensive discovery. Use when designing new products, features, or systems, when creating product proposals, PRDs, or design plans, or when the user asks about design principles, architecture decisions, or product planning.
---

# Product Design Philosophy

## Core Principles

### Architectural Approach

**Modular Design:**
- Design components as independent, encapsulated modules
- Define clear interfaces between modules
- Minimize inter-module dependencies
- Enable plug-and-play assembly

**End-to-End Thinking:**
- Consider all layers: frontend, backend, infrastructure, data, integration
- Design complete user journeys
- Ensure consistency across architectural layers

### Design Evaluation Framework

Every design MUST be evaluated against three pillars:

1. **Simplicity First**
   - Minimize complexity, maximize implementability
   - Favor straightforward solutions
   - Choose proven technologies
   - Minimize external dependencies

2. **Maximum Value Delivery**
   - Prioritize high-impact features
   - Design for scalability and performance
   - Maximize component reusability
   - Optimize for user productivity

3. **Cost Optimization**
   - Evaluate development, operational, and scaling costs
   - Use free tiers and open-source where appropriate
   - Design for efficient resource utilization
   - Consider total cost of ownership (TCO)

## Mandatory Workflow

### Phase 1: Discovery (Before Any Design)

**Conduct comprehensive discovery session. Document all answers before proceeding.**

Essential questions to ask:

**Business Context:**
- What problem are we solving?
- Who are the target users?
- What are the success metrics?
- What is the timeline and budget?
- Must-have vs nice-to-have features?

**Technical Context:**
- What existing systems must integrate?
- Expected load and scale requirements?
- Security and compliance requirements?
- Current technology stack?
- Deployment and hosting constraints?

**User Context:**
- Primary user workflows?
- Devices/platforms to support?
- Accessibility requirements?
- User technical proficiency level?

**Risk Assessment:**
- Potential technical risks?
- External dependencies?
- Fallback/contingency plans?

**Protocol:**
- Document all answers
- Flag ambiguities
- Obtain explicit confirmation on critical decisions
- Revisit if requirements change

### Phase 2: Market Research

**Before finalizing design, conduct:**

1. **Competitive Analysis**
   - Identify direct/indirect competitors
   - Analyze features, pricing, positioning
   - Document competitive advantages and gaps

2. **User Research**
   - Conduct interviews if feasible
   - Analyze feedback from similar products
   - Identify pain points and unmet needs

3. **Technical Feasibility Research**
   - Research available technologies
   - Assess complexity and risks
   - Validate scalability

4. **Cost Research**
   - Research third-party service pricing
   - Estimate infrastructure costs at different scales
   - Project total cost of ownership

5. **Trend Analysis**
   - Identify industry trends
   - Assess emerging technologies
   - Evaluate long-term viability

### Phase 3: Documentation

**Deliver three required documents:**

1. **Product Proposal** - Stakeholder buy-in and alignment
   - Executive summary (problem, solution, impact)
   - Market context and competitive landscape
   - Strategic fit and differentiation
   - High-level roadmap
   - Cost-benefit analysis
   - Risk assessment

2. **Product Requirements Document (PRD)** - Detailed specifications
   - Product overview and success criteria
   - Functional requirements (features, user stories, flows)
   - Non-functional requirements (performance, security, accessibility)
   - Technical requirements (stack, integrations, APIs)
   - UX requirements (UI/UX guidelines, design system)
   - Dependencies and constraints
   - Acceptance criteria

3. **Product Design Plan** - Implementation blueprint
   - System architecture (diagrams, component breakdown)
   - Modular component specifications
   - Technology stack details with rationale
   - Implementation phases with timelines
   - Testing strategy
   - Deployment strategy
   - Maintenance and support plan
   - Cost breakdown
   - Risk mitigation plan

**For detailed templates, see [templates.md](templates.md)**

### Phase 4: Review and Approval

**Before implementation:**
1. Present all three documents for stakeholder review
2. Address feedback and iterate
3. Obtain explicit approval
4. Archive approved documents as design baseline
5. Use as single source of truth during implementation

**Change Management:**
- Document change requests
- Assess impact on design, timeline, cost
- Update relevant documents
- Obtain approval for significant changes
- Maintain change log

## Design Quality Checklist

Before finalizing any design, verify:

- [ ] Modular architecture clearly defined
- [ ] Each module has well-defined boundaries and interfaces
- [ ] Assembly/integration strategy documented
- [ ] Simplicity prioritized (no over-engineering)
- [ ] Functionality maximized within constraints
- [ ] Costs minimized and justified
- [ ] All discovery questions answered
- [ ] End-to-end user journey designed
- [ ] Full-stack considerations addressed
- [ ] Market research completed and documented
- [ ] Product Proposal comprehensive
- [ ] PRD detailed and unambiguous
- [ ] Product Design Plan actionable
- [ ] Risk mitigation strategies defined
- [ ] Success metrics established

## Quick Reference

**When to apply this skill:**
- Designing new products or features
- Creating product proposals or PRDs
- Making architecture decisions
- Planning system integrations
- Evaluating design alternatives

**Key principles to remember:**
- Modular design with clear interfaces
- Simplicity over complexity
- Value delivery optimization
- Cost-conscious decisions
- Comprehensive discovery before design
- Three-document deliverable framework

## Additional Resources

- For detailed discovery questions, see [discovery-questions.md](discovery-questions.md)
- For document templates, see [templates.md](templates.md)
