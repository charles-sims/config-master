#!/usr/bin/env python3
"""
ConfigMaster AI Scanner Demo

Demonstrates the advanced AI-powered scanning capabilities for SaaS platforms like HubSpot.
This script showcases how the system can:
1. Use Exa.ai to find comprehensive API documentation
2. Use Firecrawl to extract structured content from documentation
3. Use Playwright to explore platform interfaces
4. Use LangChain/OpenAI to analyze and structure all discovered information

To run with real APIs, set these environment variables:
- OPENAI_API_KEY
- EXA_API_KEY
- FIRECRAWL_API_KEY
"""

import asyncio
import json
import os
from typing import Dict, List, Any
from datetime import datetime

# AI and LLM imports (with fallbacks)
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.messages import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Search and web scraping (with fallbacks)
try:
    from exa_py import Exa
    EXA_AVAILABLE = True
except ImportError:
    EXA_AVAILABLE = False

try:
    import firecrawl
    FIRECRAWL_AVAILABLE = True
except ImportError:
    FIRECRAWL_AVAILABLE = False

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

class PlatformAnalysisDemo:
    """Demo of AI-powered platform analysis"""

    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.exa_key = os.getenv('EXA_API_KEY')
        self.firecrawl_key = os.getenv('FIRECRAWL_API_KEY')

        print("🚀 ConfigMaster AI Scanner Demo")
        print("=" * 50)

        # Check available services
        self.check_services()

    def check_services(self):
        """Check which AI services are available"""
        print("\n🔍 Checking AI Services:")

        services = [
            ("LangChain/OpenAI", LANGCHAIN_AVAILABLE and bool(self.openai_key)),
            ("Exa.ai Search", EXA_AVAILABLE and bool(self.exa_key)),
            ("Firecrawl", FIRECRAWL_AVAILABLE and bool(self.firecrawl_key)),
            ("Playwright", PLAYWRIGHT_AVAILABLE)
        ]

        for service, available in services:
            status = "✅ Available" if available else "❌ Not Available"
            print(f"  {service}: {status}")

        if not any(available for _, available in services):
            print("\n⚠️  No AI services available. Running in demo mode.")

        print()

    async def demo_hubspot_analysis(self):
        """Demonstrate comprehensive HubSpot platform analysis"""
        platform = "HubSpot"
        print(f"🔍 Analyzing {platform} Platform")
        print("-" * 30)

        # Step 1: Simulated Exa.ai search
        await self._demo_exa_search(platform)

        # Step 2: Simulated Firecrawl documentation extraction
        await self._demo_firecrawl(platform)

        # Step 3: Simulated Playwright exploration
        await self._demo_playwright(platform)

        # Step 4: Simulated LLM analysis
        await self._demo_llm_analysis(platform)

        # Step 5: Show final results
        self._show_analysis_results(platform)

    async def _demo_exa_search(self, platform: str):
        """Demo Exa.ai search capabilities"""
        print(f"📡 Step 1: Exa.ai Search for {platform} Documentation")

        if EXA_AVAILABLE and self.exa_key:
            try:
                exa = Exa(api_key=self.exa_key)
                results = exa.search_and_contents(
                    f"{platform} API documentation integration",
                    num_results=5,
                    text=True
                )

                print(f"  ✅ Found {len(results.results)} documentation sources:")
                for i, result in enumerate(results.results[:3], 1):
                    print(f"     {i}. {result.title}")
                    print(f"        URL: {result.url}")

            except Exception as e:
                print(f"  ❌ Exa search failed: {e}")
        else:
            # Simulated results
            print("  🎭 Simulated Results:")
            simulated_results = [
                "HubSpot API Documentation - developers.hubspot.com",
                "HubSpot Integration Guide - knowledge.hubspot.com",
                "HubSpot Webhooks Documentation - developers.hubspot.com/docs/api/webhooks"
            ]
            for i, result in enumerate(simulated_results, 1):
                print(f"     {i}. {result}")
        print()

    async def _demo_firecrawl(self, platform: str):
        """Demo Firecrawl content extraction"""
        print(f"🔥 Step 2: Firecrawl Content Extraction for {platform}")

        if FIRECRAWL_AVAILABLE and self.firecrawl_key:
            try:
                app = firecrawl.FireCrawlApp(api_key=self.firecrawl_key)
                url = f"https://developers.{platform.lower()}.com"

                result = app.scrape_url(
                    url,
                    params={
                        'formats': ['markdown'],
                        'onlyMainContent': True
                    }
                )

                if result and 'markdown' in result:
                    content_preview = result['markdown'][:200] + "..."
                    print(f"  ✅ Extracted content from {url}")
                    print(f"     Preview: {content_preview}")

            except Exception as e:
                print(f"  ❌ Firecrawl failed: {e}")
        else:
            # Simulated extraction
            print("  🎭 Simulated Content Extraction:")
            simulated_content = [
                "API Endpoints: /contacts, /companies, /deals, /tickets",
                "Authentication: OAuth 2.0, API Keys supported",
                "Rate Limits: 100 requests per 10 seconds",
                "Webhooks: Real-time notifications for CRM events"
            ]
            for item in simulated_content:
                print(f"     • {item}")
        print()

    async def _demo_playwright(self, platform: str):
        """Demo Playwright web exploration"""
        print(f"🎭 Step 3: Playwright Web Exploration of {platform}")

        if PLAYWRIGHT_AVAILABLE:
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()

                    url = f"https://{platform.lower()}.com/pricing"
                    await page.goto(url, timeout=10000)

                    title = await page.title()
                    print(f"  ✅ Explored {url}")
                    print(f"     Page Title: {title}")

                    # Look for feature indicators
                    buttons = await page.query_selector_all("button")
                    forms = await page.query_selector_all("form")

                    print(f"     Interactive Elements: {len(buttons)} buttons, {len(forms)} forms")

                    await browser.close()

            except Exception as e:
                print(f"  ❌ Playwright exploration failed: {e}")
        else:
            # Simulated exploration
            print("  🎭 Simulated Web Exploration:")
            simulated_features = [
                "Pricing Tiers: Starter, Professional, Enterprise",
                "Key Features: CRM, Marketing Hub, Sales Hub, Service Hub",
                "Integration Marketplace: 1000+ apps available",
                "API Access: Available in Professional tier and above"
            ]
            for feature in simulated_features:
                print(f"     • {feature}")
        print()

    async def _demo_llm_analysis(self, platform: str):
        """Demo LLM-powered analysis and structuring"""
        print(f"🧠 Step 4: AI Analysis and Structuring for {platform}")

        if LANGCHAIN_AVAILABLE and self.openai_key:
            try:
                llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    temperature=0.1,
                    api_key=self.openai_key
                )

                prompt = f"""Analyze the {platform} platform and provide a structured summary of:
                1. Core functionality
                2. API capabilities
                3. Integration options
                4. Configuration features

                Return as JSON format."""

                response = await llm.ainvoke([HumanMessage(content=prompt)])
                print(f"  ✅ AI Analysis completed")
                print(f"     Analysis preview: {response.content[:100]}...")

            except Exception as e:
                print(f"  ❌ LLM analysis failed: {e}")
        else:
            # Simulated analysis
            print("  🎭 Simulated AI Analysis:")
            simulated_analysis = {
                "platform": platform,
                "category": "CRM & Marketing Automation",
                "core_functions": ["Contact Management", "Email Marketing", "Sales Pipeline"],
                "api_capabilities": ["REST API", "GraphQL", "Webhooks"],
                "integrations": ["Salesforce", "Slack", "Zapier", "Gmail"],
                "configuration": ["Custom Properties", "Workflows", "Reporting Dashboards"]
            }
            print(f"     {json.dumps(simulated_analysis, indent=6)}")
        print()

    def _show_analysis_results(self, platform: str):
        """Show final analysis results"""
        print(f"📊 Final Analysis Results for {platform}")
        print("=" * 40)

        # Simulated comprehensive analysis
        analysis = {
            "platform_name": platform,
            "discovery_timestamp": datetime.now().isoformat(),
            "category": "Customer Relationship Management",
            "confidence_score": 0.95,
            "api_documentation": [
                "https://developers.hubspot.com/docs/api/overview",
                "https://developers.hubspot.com/docs/api/contacts",
                "https://developers.hubspot.com/docs/api/crm"
            ],
            "integration_capabilities": [
                "REST API with OAuth 2.0",
                "Real-time Webhooks",
                "GraphQL (Beta)",
                "Bulk Import/Export APIs"
            ],
            "configuration_options": [
                {
                    "name": "Custom Properties",
                    "description": "Create custom fields for contacts, companies, deals",
                    "type": "customization"
                },
                {
                    "name": "Automated Workflows",
                    "description": "Set up automated marketing and sales sequences",
                    "type": "automation"
                },
                {
                    "name": "API Rate Limits",
                    "description": "Configure rate limiting for API calls",
                    "type": "technical"
                }
            ],
            "recommended_integrations": [
                {
                    "platform": "Slack",
                    "purpose": "Team notifications for deals and contacts",
                    "complexity": "Low"
                },
                {
                    "platform": "Salesforce",
                    "purpose": "CRM data synchronization",
                    "complexity": "Medium"
                },
                {
                    "platform": "Zapier",
                    "purpose": "Connect to 2000+ other apps",
                    "complexity": "Low"
                }
            ]
        }

        print(json.dumps(analysis, indent=2))

        print(f"\n🎯 Integration Recommendations:")
        for rec in analysis["recommended_integrations"]:
            print(f"  • {rec['platform']}: {rec['purpose']} (Complexity: {rec['complexity']})")

        print(f"\n✅ Analysis Complete! ConfigMaster now understands:")
        print(f"  • {len(analysis['api_documentation'])} API documentation sources")
        print(f"  • {len(analysis['integration_capabilities'])} integration methods")
        print(f"  • {len(analysis['configuration_options'])} configuration options")
        print(f"  • {len(analysis['recommended_integrations'])} integration recommendations")

async def main():
    """Run the AI scanner demo"""
    demo = PlatformAnalysisDemo()
    await demo.demo_hubspot_analysis()

    print(f"\n🚀 Next Steps:")
    print("1. Set up API keys to enable real-time analysis")
    print("2. Add more platforms to your discovery list")
    print("3. Configure integration recommendations based on your organization's needs")
    print("4. Set up automated discovery scans on a schedule")

if __name__ == "__main__":
    asyncio.run(main())