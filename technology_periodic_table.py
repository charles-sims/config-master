#!/usr/bin/env python3
"""
Technology Periodic Table Generator

Creates a visual representation of the ConfigMaster Organizational Technology
Maturity Framework (COTMF) similar to the chemical periodic table.

Each "element" represents a technology capability, organized by:
- Periods (Rows): Maturity stages (Startup → Enterprise)
- Groups (Columns): Technology categories
- Element properties: Cost, complexity, integration requirements
"""

import json
from typing import Dict, List, Any
from backend.maturity_framework import OrganizationalTechnologyFramework, MaturityStage, TechnologyCategory

class TechnologyPeriodicTable:
    """Generate visual and data representations of the technology framework"""

    def __init__(self):
        self.framework = OrganizationalTechnologyFramework()
        self.table_structure = self._build_table_structure()

    def _build_table_structure(self) -> Dict[str, Any]:
        """Build the periodic table structure"""

        # Define the "periods" (rows) - maturity stages
        periods = {
            1: {"name": "Startup", "stage": MaturityStage.STARTUP, "description": "Essential survival tools"},
            2: {"name": "Growing", "stage": MaturityStage.GROWING, "description": "Operational efficiency"},
            3: {"name": "Scaling", "stage": MaturityStage.SCALING, "description": "Process optimization"},
            4: {"name": "Established", "stage": MaturityStage.ESTABLISHED, "description": "Governance & compliance"},
            5: {"name": "Enterprise", "stage": MaturityStage.ENTERPRISE, "description": "Advanced operations"}
        }

        # Define the "groups" (columns) - technology categories
        groups = {
            1: {"name": "Communication", "category": TechnologyCategory.COMMUNICATION, "symbol": "Cm"},
            2: {"name": "File Storage", "category": TechnologyCategory.FILE_STORAGE, "symbol": "Fs"},
            3: {"name": "Financial", "category": TechnologyCategory.FINANCIAL, "symbol": "Fn"},
            4: {"name": "Project Mgmt", "category": TechnologyCategory.PROJECT_MGMT, "symbol": "Pm"},
            5: {"name": "CRM", "category": TechnologyCategory.CRM, "symbol": "Cr"},
            6: {"name": "HR", "category": TechnologyCategory.HR_BASIC, "symbol": "Hr"},
            7: {"name": "Analytics", "category": TechnologyCategory.ANALYTICS, "symbol": "An"},
            8: {"name": "Marketing", "category": TechnologyCategory.MARKETING, "symbol": "Mk"},
            9: {"name": "Support", "category": TechnologyCategory.SUPPORT, "symbol": "Sp"},
            10: {"name": "Security", "category": TechnologyCategory.SECURITY, "symbol": "Sc"},
            11: {"name": "Compliance", "category": TechnologyCategory.COMPLIANCE, "symbol": "Cp"},
            12: {"name": "DevOps", "category": TechnologyCategory.DEV_OPS, "symbol": "Do"},
            13: {"name": "Adv Analytics", "category": TechnologyCategory.ADVANCED_ANALYTICS, "symbol": "Aa"},
            14: {"name": "Integration", "category": TechnologyCategory.ENTERPRISE_INTEGRATION, "symbol": "In"},
            15: {"name": "Supply Chain", "category": TechnologyCategory.SUPPLY_CHAIN, "symbol": "Sc"}
        }

        # Build the table grid
        table = {
            "periods": periods,
            "groups": groups,
            "elements": {},
            "metadata": {
                "title": "ConfigMaster Technology Periodic Table",
                "subtitle": "Organizational Technology Maturity Framework",
                "version": "1.0"
            }
        }

        # Place capabilities as "elements" in the table
        element_counter = 1
        for capability_id, capability in self.framework.capabilities.items():

            # Find period (row) based on maturity stage
            period = None
            for p_num, p_info in periods.items():
                if p_info["stage"] == capability.required_stage:
                    period = p_num
                    break

            # Find group (column) based on category
            group = None
            for g_num, g_info in groups.items():
                if g_info["category"] == capability.category:
                    group = g_num
                    break

            if period and group:
                element = {
                    "atomic_number": element_counter,
                    "symbol": self._generate_symbol(capability.name),
                    "name": capability.name,
                    "period": period,
                    "group": group,
                    "category": capability.category.value,
                    "stage": capability.required_stage.value,

                    # "Atomic properties"
                    "priority": capability.priority,
                    "complexity": capability.integration_complexity.value,
                    "cost_weight": capability.monthly_cost_range[1],  # Max monthly cost
                    "productivity_factor": capability.productivity_impact,
                    "risk_reduction": capability.risk_reduction,

                    # Implementation details
                    "setup_time": capability.setup_time_days,
                    "typical_solutions": capability.typical_solutions,
                    "prerequisites": capability.prerequisites,
                    "synergies": capability.synergies,

                    # Business impact
                    "compliance_impact": capability.compliance_impact,
                    "description": capability.description
                }

                table["elements"][capability_id] = element
                element_counter += 1

        return table

    def _generate_symbol(self, name: str) -> str:
        """Generate a periodic table style symbol for each technology"""
        words = name.split()
        if len(words) == 1:
            return words[0][:2].capitalize()
        else:
            return ''.join(word[0] for word in words[:2]).upper()

    def generate_html_table(self) -> str:
        """Generate HTML representation of the periodic table"""

        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ConfigMaster Technology Periodic Table</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 2.5em;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }

        .periodic-table {
            display: grid;
            grid-template-columns: repeat(15, 1fr);
            gap: 2px;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }

        .element {
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 8px;
            padding: 8px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            min-height: 80px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            position: relative;
            background: rgba(255,255,255,0.1);
        }

        .element:hover {
            transform: scale(1.05);
            background: rgba(255,255,255,0.2);
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }

        .element.startup { background: rgba(255, 99, 132, 0.8); }
        .element.growing { background: rgba(54, 162, 235, 0.8); }
        .element.scaling { background: rgba(255, 206, 86, 0.8); }
        .element.established { background: rgba(75, 192, 192, 0.8); }
        .element.enterprise { background: rgba(153, 102, 255, 0.8); }

        .element.critical { border-color: #ff4444; border-width: 3px; }
        .element.high { border-color: #ff8800; }
        .element.medium { border-color: #ffcc00; }
        .element.low { border-color: #88ff88; }

        .symbol {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 2px;
        }

        .name {
            font-size: 0.7em;
            line-height: 1.1;
            margin-bottom: 2px;
        }

        .cost {
            font-size: 0.6em;
            opacity: 0.8;
        }

        .atomic-number {
            position: absolute;
            top: 2px;
            left: 3px;
            font-size: 0.6em;
            opacity: 0.7;
        }

        .legend {
            margin-top: 30px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }

        .legend-section {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
        }

        .legend-title {
            font-weight: bold;
            margin-bottom: 10px;
        }

        .stage-indicator {
            display: inline-block;
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border-radius: 3px;
        }

        .priority-indicator {
            display: inline-block;
            width: 15px;
            height: 15px;
            margin-right: 8px;
            border-radius: 50%;
        }

        .empty-cell {
            opacity: 0.3;
        }

        @media (max-width: 1200px) {
            .periodic-table {
                grid-template-columns: repeat(10, 1fr);
            }
        }

        @media (max-width: 800px) {
            .periodic-table {
                grid-template-columns: repeat(5, 1fr);
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>ConfigMaster Technology Periodic Table</h1>
        <p>Organizational Technology Maturity Framework (COTMF)</p>
        <p><em>Essential technologies for every stage of business growth</em></p>
    </div>

    <div class="periodic-table">
"""

        # Create grid with all possible positions
        max_period = 5
        max_group = 15

        for period in range(1, max_period + 1):
            for group in range(1, max_group + 1):
                # Find element at this position
                element = None
                for elem_id, elem_data in self.table_structure["elements"].items():
                    if elem_data["period"] == period and elem_data["group"] == group:
                        element = elem_data
                        break

                if element:
                    html += f"""
        <div class="element {element['stage']} {element['priority']}"
             title="{element['description']} | Cost: ${element['cost_weight']}/mo | Setup: {element['setup_time']} days">
            <div class="atomic-number">{element['atomic_number']}</div>
            <div class="symbol">{element['symbol']}</div>
            <div class="name">{element['name']}</div>
            <div class="cost">${element['cost_weight']}/mo</div>
        </div>
"""
                else:
                    html += '<div class="element empty-cell"></div>'

        html += """
    </div>

    <div class="legend">
        <div class="legend-section">
            <div class="legend-title">Maturity Stages (Periods)</div>
            <div><span class="stage-indicator startup"></span>Startup (1-10 people)</div>
            <div><span class="stage-indicator growing"></span>Growing (11-50 people)</div>
            <div><span class="stage-indicator scaling"></span>Scaling (51-200 people)</div>
            <div><span class="stage-indicator established"></span>Established (201-1000 people)</div>
            <div><span class="stage-indicator enterprise"></span>Enterprise (1000+ people)</div>
        </div>

        <div class="legend-section">
            <div class="legend-title">Priority Levels (Border Colors)</div>
            <div><span class="priority-indicator" style="background: #ff4444;"></span>Critical - Must have</div>
            <div><span class="priority-indicator" style="background: #ff8800;"></span>High - Should have</div>
            <div><span class="priority-indicator" style="background: #ffcc00;"></span>Medium - Nice to have</div>
            <div><span class="priority-indicator" style="background: #88ff88;"></span>Low - Future consideration</div>
        </div>

        <div class="legend-section">
            <div class="legend-title">Technology Categories (Groups)</div>
            <div style="font-size: 0.9em; line-height: 1.6;">
                Communication • File Storage • Financial • Project Management<br>
                CRM • HR • Analytics • Marketing • Support • Security<br>
                Compliance • DevOps • Advanced Analytics • Integration • Supply Chain
            </div>
        </div>

        <div class="legend-section">
            <div class="legend-title">How to Read Each Element</div>
            <div style="font-size: 0.9em; line-height: 1.6;">
                <strong>Symbol:</strong> Technology abbreviation<br>
                <strong>Name:</strong> Full technology name<br>
                <strong>Cost:</strong> Monthly cost estimate<br>
                <strong>Tooltip:</strong> Hover for description & setup time
            </div>
        </div>
    </div>

    <div style="text-align: center; margin-top: 30px; font-size: 0.9em; opacity: 0.8;">
        <p>ConfigMaster Organizational Technology Maturity Framework v1.0</p>
        <p>Like the chemical periodic table, this framework shows the fundamental "elements" of business technology</p>
    </div>

    <script>
        // Add click functionality to show detailed information
        document.querySelectorAll('.element:not(.empty-cell)').forEach(element => {
            element.addEventListener('click', function() {
                const name = this.querySelector('.name').textContent;
                const symbol = this.querySelector('.symbol').textContent;
                const description = this.getAttribute('title');

                alert(`${name} (${symbol})\\n\\n${description}`);
            });
        });
    </script>
</body>
</html>
"""
        return html

    def generate_json_export(self) -> str:
        """Generate JSON export of the complete framework"""

        export_data = {
            "framework_name": "ConfigMaster Organizational Technology Maturity Framework",
            "framework_version": "1.0",
            "description": "A comprehensive framework defining technology evolution paths for organizations",
            "generated_at": "2024-01-01T00:00:00Z",

            "maturity_stages": {
                stage.value: {
                    "name": stage.name,
                    "description": self._get_stage_description(stage)
                } for stage in MaturityStage
            },

            "technology_categories": {
                cat.value: {
                    "name": cat.name.replace('_', ' ').title(),
                    "description": self._get_category_description(cat)
                } for cat in TechnologyCategory
            },

            "capabilities": {
                cap_id: {
                    "name": cap.name,
                    "description": cap.description,
                    "category": cap.category.value,
                    "required_stage": cap.required_stage.value,
                    "priority": cap.priority,
                    "typical_solutions": cap.typical_solutions,
                    "integration_complexity": cap.integration_complexity.value,
                    "setup_time_days": cap.setup_time_days,
                    "monthly_cost_range": list(cap.monthly_cost_range),
                    "productivity_impact": cap.productivity_impact,
                    "risk_reduction": cap.risk_reduction,
                    "prerequisites": cap.prerequisites,
                    "synergies": cap.synergies,
                    "compliance_impact": cap.compliance_impact
                } for cap_id, cap in self.framework.capabilities.items()
            },

            "stage_gates": [
                {
                    "from_stage": gate.from_stage.value,
                    "to_stage": gate.to_stage.value,
                    "employee_count_min": gate.employee_count_min,
                    "revenue_threshold": gate.revenue_threshold,
                    "customer_count_min": gate.customer_count_min,
                    "business_indicators": list(gate.business_indicators),
                    "technology_requirements": list(gate.technology_requirements),
                    "compliance_requirements": list(gate.compliance_requirements),
                    "new_capabilities": list(gate.new_capabilities)
                } for gate in self.framework.stage_gates
            ],

            "integration_patterns": {
                pattern_id: {
                    "capabilities": pattern_data["capabilities"],
                    "pattern": pattern_data["pattern"],
                    "description": pattern_data["description"],
                    "complexity": pattern_data["complexity"].value if hasattr(pattern_data["complexity"], 'value') else str(pattern_data["complexity"]),
                    "business_value": pattern_data["business_value"]
                } for pattern_id, pattern_data in self.framework.integration_patterns.items()
            },

            "periodic_table": self.table_structure
        }

        return json.dumps(export_data, indent=2)

    def _get_stage_description(self, stage: MaturityStage) -> str:
        """Get description for maturity stage"""
        descriptions = {
            MaturityStage.STARTUP: "Essential survival tools for new businesses",
            MaturityStage.GROWING: "Operational efficiency tools for growing teams",
            MaturityStage.SCALING: "Process optimization for scaling operations",
            MaturityStage.ESTABLISHED: "Governance and compliance for mature organizations",
            MaturityStage.ENTERPRISE: "Advanced operations for complex enterprises"
        }
        return descriptions.get(stage, "Technology capability stage")

    def _get_category_description(self, category: TechnologyCategory) -> str:
        """Get description for technology category"""
        descriptions = {
            TechnologyCategory.COMMUNICATION: "Email, messaging, and collaboration tools",
            TechnologyCategory.FILE_STORAGE: "Document management and cloud storage",
            TechnologyCategory.FINANCIAL: "Accounting, payments, and financial management",
            TechnologyCategory.PROJECT_MGMT: "Task tracking and project planning",
            TechnologyCategory.CRM: "Customer relationship management",
            TechnologyCategory.HR_BASIC: "Human resources and employee management",
            TechnologyCategory.ANALYTICS: "Business intelligence and reporting",
            TechnologyCategory.MARKETING: "Marketing automation and campaigns",
            TechnologyCategory.SUPPORT: "Customer support and help desk",
            TechnologyCategory.SECURITY: "Security infrastructure and tools",
            TechnologyCategory.COMPLIANCE: "Governance, risk, and compliance",
            TechnologyCategory.DEV_OPS: "Development and operations automation",
            TechnologyCategory.ADVANCED_ANALYTICS: "AI, ML, and advanced analytics",
            TechnologyCategory.ENTERPRISE_INTEGRATION: "API management and integration",
            TechnologyCategory.SUPPLY_CHAIN: "ERP and supply chain management"
        }
        return descriptions.get(category, "Technology category")

def main():
    """Generate the periodic table and export formats"""

    table = TechnologyPeriodicTable()

    # Generate HTML periodic table
    html_content = table.generate_html_table()
    with open('/Users/charlessims/Documents/GitHub/config-master/technology_periodic_table.html', 'w') as f:
        f.write(html_content)

    # Generate JSON export
    json_content = table.generate_json_export()
    with open('/Users/charlessims/Documents/GitHub/config-master/cotmf_framework.json', 'w') as f:
        f.write(json_content)

    print("✅ Technology Periodic Table generated:")
    print("   📄 HTML: technology_periodic_table.html")
    print("   📊 JSON: cotmf_framework.json")
    print("\n🎯 Framework includes:")
    print(f"   • {len(table.framework.capabilities)} technology capabilities")
    print(f"   • {len(table.framework.stage_gates)} maturity stage gates")
    print(f"   • {len(list(MaturityStage))} organizational stages")
    print(f"   • {len(list(TechnologyCategory))} technology categories")

if __name__ == "__main__":
    main()