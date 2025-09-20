#!/usr/bin/env python3
"""
ConfigMaster Organizational Technology Maturity Assessment Demo

Demonstrates the complete COTMF framework including:
1. Maturity stage assessment
2. Technology gap analysis
3. Growth roadmap generation
4. Integration recommendations
"""

import json
from typing import Dict, Any
from backend.maturity_framework import OrganizationalTechnologyFramework, MaturityStage

class MaturityAssessmentDemo:
    """Demo the complete maturity assessment process"""

    def __init__(self):
        self.framework = OrganizationalTechnologyFramework()

    def run_assessment_demo(self):
        """Run complete assessment demo with example organizations"""

        print("🏢 ConfigMaster Organizational Technology Maturity Assessment")
        print("=" * 65)
        print()

        # Demo organizations at different stages
        organizations = [
            {
                "name": "TechStart Inc.",
                "description": "Early-stage SaaS startup",
                "employee_count": 8,
                "annual_revenue": 200000,
                "customer_count": 25,
                "current_technology_tools": ["Gmail", "Google Drive", "Slack", "QuickBooks"]
            },
            {
                "name": "GrowthCorp",
                "description": "Scaling e-commerce company",
                "employee_count": 75,
                "annual_revenue": 3500000,
                "customer_count": 500,
                "current_technology_tools": [
                    "Google Workspace", "Dropbox", "HubSpot", "Asana",
                    "QuickBooks", "Zendesk", "Mailchimp"
                ]
            },
            {
                "name": "Enterprise Solutions Ltd.",
                "description": "Established B2B software company",
                "employee_count": 450,
                "annual_revenue": 25000000,
                "customer_count": 2500,
                "current_technology_tools": [
                    "Microsoft 365", "Salesforce", "NetSuite", "Jira",
                    "Tableau", "Okta", "ServiceNow", "Marketo"
                ]
            }
        ]

        for org in organizations:
            self.assess_organization(org)
            print("\n" + "─" * 65 + "\n")

    def assess_organization(self, org_data: Dict[str, Any]):
        """Assess a single organization"""

        print(f"🔍 Assessing: {org_data['name']}")
        print(f"📋 {org_data['description']}")
        print(f"👥 Employees: {org_data['employee_count']}")
        print(f"💰 Revenue: ${org_data['annual_revenue']:,}")
        print(f"🎯 Customers: {org_data['customer_count']}")
        print()

        # Assess current maturity stage
        current_stage, recommendations = self.framework.assess_organization_maturity(org_data)

        print(f"📊 Current Maturity Stage: {current_stage.value.upper()}")
        self._display_stage_characteristics(current_stage)

        # Show technology gap analysis
        print(f"\n🔧 Technology Gap Analysis:")
        self._analyze_technology_gaps(org_data, current_stage)

        # Determine next stage and roadmap
        next_stage = self._get_next_stage(current_stage)
        if next_stage:
            print(f"\n🚀 Growth Roadmap to {next_stage.value.upper()}:")
            roadmap = self.framework.get_technology_roadmap(current_stage, next_stage)
            self._display_roadmap(roadmap)

        # Show integration recommendations
        print(f"\n🔗 Integration Recommendations:")
        self._show_integration_recommendations(org_data, current_stage)

    def _display_stage_characteristics(self, stage: MaturityStage):
        """Display characteristics of the current stage"""

        stage_info = {
            MaturityStage.STARTUP: {
                "focus": "Survival & MVP development",
                "priorities": ["Basic communication", "Financial tracking", "File management"],
                "team_size": "1-10 people",
                "revenue_range": "$0-500K"
            },
            MaturityStage.GROWING: {
                "focus": "Operational efficiency & team scaling",
                "priorities": ["Project management", "Customer tracking", "HR systems"],
                "team_size": "11-50 people",
                "revenue_range": "$500K-2M"
            },
            MaturityStage.SCALING: {
                "focus": "Process optimization & automation",
                "priorities": ["Marketing automation", "Business intelligence", "Security"],
                "team_size": "51-200 people",
                "revenue_range": "$2M-10M"
            },
            MaturityStage.ESTABLISHED: {
                "focus": "Governance & compliance",
                "priorities": ["Enterprise systems", "Compliance", "Advanced security"],
                "team_size": "201-1000 people",
                "revenue_range": "$10M-50M"
            },
            MaturityStage.ENTERPRISE: {
                "focus": "Advanced operations & innovation",
                "priorities": ["AI/ML", "Enterprise integration", "Supply chain"],
                "team_size": "1000+ people",
                "revenue_range": "$50M+"
            }
        }

        info = stage_info.get(stage, {})
        print(f"   Focus: {info.get('focus', 'N/A')}")
        print(f"   Typical Size: {info.get('team_size', 'N/A')}")
        print(f"   Revenue Range: {info.get('revenue_range', 'N/A')}")
        print(f"   Key Priorities: {', '.join(info.get('priorities', []))}")

    def _analyze_technology_gaps(self, org_data: Dict[str, Any], current_stage: MaturityStage):
        """Analyze technology gaps for current stage"""

        current_tools = [tool.lower() for tool in org_data.get('current_technology_tools', [])]

        # Get all capabilities for current stage and below
        stage_values = [s.value for s in MaturityStage]
        current_stage_index = stage_values.index(current_stage.value)

        relevant_capabilities = []
        for cap in self.framework.capabilities.values():
            cap_stage_index = stage_values.index(cap.required_stage.value)
            if cap_stage_index <= current_stage_index:
                relevant_capabilities.append(cap)

        # Categorize capabilities
        implemented = []
        missing_critical = []
        missing_high = []
        missing_other = []

        for cap in relevant_capabilities:
            # Check if any typical solution is implemented
            has_solution = any(
                any(tool_word in solution.lower() for tool_word in current_tools)
                for solution in cap.typical_solutions
            )

            if has_solution:
                implemented.append(cap)
            else:
                if cap.priority == "critical":
                    missing_critical.append(cap)
                elif cap.priority == "high":
                    missing_high.append(cap)
                else:
                    missing_other.append(cap)

        print(f"   ✅ Implemented: {len(implemented)} capabilities")
        if implemented:
            for cap in implemented[:3]:  # Show first 3
                print(f"      • {cap.name}")
            if len(implemented) > 3:
                print(f"      • ... and {len(implemented) - 3} more")

        if missing_critical:
            print(f"   🚨 Missing Critical: {len(missing_critical)} capabilities")
            for cap in missing_critical:
                print(f"      • {cap.name} - {cap.description}")

        if missing_high:
            print(f"   ⚠️  Missing High Priority: {len(missing_high)} capabilities")
            for cap in missing_high[:2]:  # Show first 2
                print(f"      • {cap.name}")

        if missing_other:
            print(f"   📝 Other Opportunities: {len(missing_other)} capabilities")

    def _display_roadmap(self, roadmap: Dict[str, Any]):
        """Display the technology roadmap"""

        print(f"   🎯 Target: {roadmap['target_stage'].title()}")
        print(f"   ⏱️  Timeline: ~{roadmap['total_timeline_days']} days")
        print(f"   💰 Estimated Cost: ${roadmap['total_estimated_cost']:,}/year")
        print()

        for phase in roadmap['phases']:
            if phase['capabilities']:
                print(f"   📋 {phase['stage'].title()} Phase:")
                print(f"      Timeline: {phase['timeline_days']} days")
                print(f"      Annual Cost: ${phase['estimated_cost']:,}")
                print(f"      Key Additions:")

                # Show top 3 critical/high priority items
                critical_items = [cap for cap in phase['capabilities'] if cap['priority'] in ['critical', 'high']]
                for cap in critical_items[:3]:
                    print(f"        • {cap['name']} ({cap['priority']})")

                if len(phase['capabilities']) > 3:
                    print(f"        • ... and {len(phase['capabilities']) - 3} more capabilities")
                print()

    def _show_integration_recommendations(self, org_data: Dict[str, Any], stage: MaturityStage):
        """Show integration recommendations based on current tools"""

        current_tools = org_data.get('current_technology_tools', [])

        # Common integration patterns by stage
        integration_suggestions = {
            MaturityStage.STARTUP: [
                "Connect email with file storage for seamless document sharing",
                "Integrate accounting with payment processing for automated bookkeeping",
                "Link video conferencing with calendar for meeting scheduling"
            ],
            MaturityStage.GROWING: [
                "Sync CRM with email marketing for lead nurturing campaigns",
                "Connect project management with time tracking for better estimates",
                "Integrate HR system with email for automated onboarding workflows"
            ],
            MaturityStage.SCALING: [
                "Connect marketing automation with analytics for campaign optimization",
                "Integrate customer support with CRM for unified customer view",
                "Link business intelligence with financial systems for real-time reporting"
            ],
            MaturityStage.ESTABLISHED: [
                "Integrate compliance system with all business applications",
                "Connect identity management with security monitoring",
                "Link enterprise CRM with advanced analytics for predictive insights"
            ],
            MaturityStage.ENTERPRISE: [
                "Integrate AI/ML platform with all data sources",
                "Connect API management with enterprise integration platform",
                "Link ERP system with supply chain and customer systems"
            ]
        }

        suggestions = integration_suggestions.get(stage, [])

        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion}")

        # Show tool-specific recommendations
        print(f"\n   🔧 Based on your current tools:")
        tool_recommendations = self._get_tool_specific_recommendations(current_tools)
        for rec in tool_recommendations[:3]:
            print(f"   • {rec}")

    def _get_tool_specific_recommendations(self, current_tools: list) -> list:
        """Generate tool-specific integration recommendations"""

        recommendations = []
        tools_lower = [tool.lower() for tool in current_tools]

        # Common integration patterns
        patterns = {
            ("hubspot", "mailchimp"): "Sync HubSpot contacts with Mailchimp for unified email marketing",
            ("salesforce", "tableau"): "Connect Salesforce data to Tableau for sales analytics",
            ("slack", "asana"): "Integrate Slack with Asana for project notifications",
            ("quickbooks", "stripe"): "Connect QuickBooks with Stripe for automated revenue tracking",
            ("zendesk", "salesforce"): "Link Zendesk tickets with Salesforce accounts",
            ("okta", "google"): "Implement Okta SSO for Google Workspace access",
            ("jira", "github"): "Connect Jira with GitHub for development workflow tracking"
        }

        for (tool1, tool2), recommendation in patterns.items():
            if any(tool1 in tool for tool in tools_lower) and any(tool2 in tool for tool in tools_lower):
                recommendations.append(recommendation)

        # Generic recommendations based on tool categories
        if any("hubspot" in tool or "salesforce" in tool for tool in tools_lower):
            recommendations.append("Consider adding marketing automation integration for lead nurturing")

        if any("slack" in tool or "teams" in tool for tool in tools_lower):
            recommendations.append("Set up automated notifications from business applications to your team chat")

        return recommendations

    def _get_next_stage(self, current_stage: MaturityStage) -> MaturityStage:
        """Get the next maturity stage"""

        stages = list(MaturityStage)
        try:
            current_index = stages.index(current_stage)
            if current_index < len(stages) - 1:
                return stages[current_index + 1]
        except ValueError:
            pass

        return None

def main():
    """Run the maturity assessment demo"""
    demo = MaturityAssessmentDemo()
    demo.run_assessment_demo()

    print("\n🎯 Next Steps:")
    print("1. Run assessment on your actual organization")
    print("2. Review technology gaps and priorities")
    print("3. Plan implementation timeline based on roadmap")
    print("4. Start with critical missing capabilities")
    print("5. Set up key integrations for maximum impact")

    print("\n📊 Framework Features:")
    print("• 30+ technology capabilities across 5 maturity stages")
    print("• Automated gap analysis and recommendations")
    print("• Cost and timeline estimates for each capability")
    print("• Integration patterns and best practices")
    print("• Visual periodic table representation")

if __name__ == "__main__":
    main()