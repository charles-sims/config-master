#!/usr/bin/env python3
"""
AI-Powered Platform Scanner

Uses LangChain, Exa.ai, Playwright, and Firecrawl to intelligently discover and analyze SaaS platforms like HubSpot.
"""

import os
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

# AI and LLM imports
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Search and web scraping
from exa_py import Exa
import firecrawl
from playwright.async_api import async_playwright, Browser, Page
from bs4 import BeautifulSoup
import httpx

# Core dependencies
try:
    from ..models import Application, AppType, Environment, Integration, ConfigurationItem, DiscoveryResult
    from .base import BaseScanner
except ImportError:
    from models import Application, AppType, Environment, Integration, ConfigurationItem, DiscoveryResult
    from base import BaseScanner

logger = logging.getLogger(__name__)

@dataclass
class PlatformInfo:
    """Information discovered about a platform"""
    name: str
    description: str
    category: str
    api_documentation: List[str]
    integration_capabilities: List[str]
    configuration_options: List[Dict[str, Any]]
    pricing_model: Optional[str] = None
    supported_integrations: List[str] = None
    security_features: List[str] = None

class AIPlatformScanner(BaseScanner):
    """Advanced AI-powered scanner for discovering and analyzing SaaS platforms"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.openai_api_key = config.get('openai_api_key') or os.getenv('OPENAI_API_KEY')
        self.exa_api_key = config.get('exa_api_key') or os.getenv('EXA_API_KEY')
        self.firecrawl_api_key = config.get('firecrawl_api_key') or os.getenv('FIRECRAWL_API_KEY')

        # Initialize AI clients
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            api_key=self.openai_api_key
        ) if self.openai_api_key else None

        self.exa = Exa(api_key=self.exa_api_key) if self.exa_api_key else None

        self.firecrawl_client = firecrawl.FireCrawlApp(
            api_key=self.firecrawl_api_key
        ) if self.firecrawl_api_key else None

        # Text processing
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=200
        )

    def can_scan(self) -> bool:
        """Check if scanner has required API keys"""
        return bool(self.openai_api_key and (self.exa_api_key or self.firecrawl_api_key))

    async def scan_platform(self, platform_name: str) -> Optional[PlatformInfo]:
        """
        Comprehensively scan a platform using AI tools

        Args:
            platform_name: Name of the platform to scan (e.g., "HubSpot", "Salesforce")
        """
        logger.info(f"Starting AI-powered scan of {platform_name}")

        try:
            # Step 1: Use Exa.ai to find comprehensive information
            exa_results = await self._search_with_exa(platform_name)

            # Step 2: Crawl official documentation with Firecrawl
            docs_content = await self._crawl_documentation(platform_name, exa_results)

            # Step 3: Use Playwright for interactive exploration
            interactive_data = await self._interactive_exploration(platform_name)

            # Step 4: Analyze all data with LLM
            platform_info = await self._analyze_with_llm(
                platform_name, exa_results, docs_content, interactive_data
            )

            return platform_info

        except Exception as e:
            logger.error(f"Error scanning platform {platform_name}: {e}")
            return None

    async def _search_with_exa(self, platform_name: str) -> Dict[str, Any]:
        """Use Exa.ai to find comprehensive platform information"""
        if not self.exa:
            return {}

        try:
            # Search for API documentation
            api_search = self.exa.search_and_contents(
                f"{platform_name} API documentation integration configuration",
                type="keyword",
                num_results=10,
                text=True
            )

            # Search for integration guides
            integration_search = self.exa.search_and_contents(
                f"{platform_name} integrations third-party connections webhooks",
                type="neural",
                num_results=8,
                text=True
            )

            # Search for configuration and setup guides
            config_search = self.exa.search_and_contents(
                f"{platform_name} configuration setup guide admin settings",
                type="keyword",
                num_results=6,
                text=True
            )

            return {
                "api_docs": api_search.results if api_search else [],
                "integrations": integration_search.results if integration_search else [],
                "configuration": config_search.results if config_search else []
            }

        except Exception as e:
            logger.warning(f"Exa.ai search failed for {platform_name}: {e}")
            return {}

    async def _crawl_documentation(self, platform_name: str, exa_results: Dict) -> Dict[str, str]:
        """Use Firecrawl to extract content from documentation pages"""
        if not self.firecrawl_client:
            return {}

        content = {}
        urls_to_crawl = []

        # Extract URLs from Exa results
        for category, results in exa_results.items():
            for result in results[:3]:  # Limit to top 3 per category
                if hasattr(result, 'url'):
                    urls_to_crawl.append((category, result.url))

        # Add common documentation URLs
        common_docs = [
            f"https://developers.{platform_name.lower()}.com",
            f"https://api.{platform_name.lower()}.com",
            f"https://docs.{platform_name.lower()}.com",
            f"https://{platform_name.lower()}.com/developers",
        ]

        for url in common_docs:
            urls_to_crawl.append(("docs", url))

        # Crawl each URL
        for category, url in urls_to_crawl:
            try:
                result = self.firecrawl_client.scrape_url(
                    url,
                    params={
                        'formats': ['markdown', 'html'],
                        'onlyMainContent': True,
                        'includeTags': ['h1', 'h2', 'h3', 'p', 'pre', 'code', 'li'],
                        'waitFor': 3000
                    }
                )

                if result and 'markdown' in result:
                    content[f"{category}_{url}"] = result['markdown']

            except Exception as e:
                logger.debug(f"Failed to crawl {url}: {e}")
                continue

        return content

    async def _interactive_exploration(self, platform_name: str) -> Dict[str, Any]:
        """Use Playwright to interactively explore platform interfaces"""
        data = {}

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()

                # Try to access login/signup pages to discover features
                urls_to_explore = [
                    f"https://{platform_name.lower()}.com",
                    f"https://app.{platform_name.lower()}.com",
                    f"https://{platform_name.lower()}.com/pricing",
                    f"https://{platform_name.lower()}.com/features",
                ]

                for url in urls_to_explore:
                    try:
                        await page.goto(url, wait_until="networkidle", timeout=10000)

                        # Extract visible text and structure
                        content = await page.content()
                        soup = BeautifulSoup(content, 'html.parser')

                        # Look for feature lists, pricing tiers, etc.
                        features = []
                        for elem in soup.find_all(['h1', 'h2', 'h3', 'li']):
                            if elem.text.strip():
                                features.append(elem.text.strip())

                        data[url] = {
                            "title": await page.title(),
                            "features": features[:20],  # Limit features
                            "forms": len(await page.query_selector_all("form")),
                            "buttons": len(await page.query_selector_all("button"))
                        }

                        # Look for API or developer links
                        api_links = await page.query_selector_all('a[href*="api"], a[href*="developer"], a[href*="docs"]')
                        if api_links:
                            data[url]["api_links"] = [
                                await link.get_attribute("href") for link in api_links[:5]
                            ]

                    except Exception as e:
                        logger.debug(f"Failed to explore {url}: {e}")
                        continue

                await browser.close()

        except Exception as e:
            logger.warning(f"Playwright exploration failed for {platform_name}: {e}")

        return data

    async def _analyze_with_llm(self, platform_name: str, exa_results: Dict,
                               docs_content: Dict, interactive_data: Dict) -> PlatformInfo:
        """Use LLM to analyze all gathered data and extract structured information"""

        if not self.llm:
            # Fallback to basic analysis without LLM
            return self._basic_analysis(platform_name, exa_results, docs_content, interactive_data)

        # Prepare context for LLM
        context = f"""
        Platform Name: {platform_name}

        Exa.ai Search Results:
        {json.dumps(exa_results, indent=2, default=str)[:3000]}

        Documentation Content:
        {str(docs_content)[:4000]}

        Interactive Exploration Data:
        {json.dumps(interactive_data, indent=2, default=str)[:2000]}
        """

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert analyst of SaaS platforms and business software.
            Analyze the provided information about a platform and extract structured data about its capabilities,
            integrations, configuration options, and technical features.

            Focus on:
            1. Core functionality and use cases
            2. API capabilities and integration options
            3. Configuration and customization features
            4. Security and compliance features
            5. Pricing model and tiers
            6. Supported third-party integrations

            Return a JSON object with the following structure:
            {
                "name": "platform name",
                "description": "detailed description",
                "category": "category (CRM, Marketing, Analytics, etc.)",
                "api_documentation": ["list of API doc URLs"],
                "integration_capabilities": ["list of integration types"],
                "configuration_options": [{"name": "option", "description": "desc", "type": "type"}],
                "pricing_model": "description of pricing",
                "supported_integrations": ["list of platforms it integrates with"],
                "security_features": ["list of security features"]
            }"""),
            HumanMessage(content=context)
        ])

        try:
            response = await self.llm.ainvoke(prompt.format_messages())
            result = json.loads(response.content)

            return PlatformInfo(
                name=result.get("name", platform_name),
                description=result.get("description", ""),
                category=result.get("category", "Unknown"),
                api_documentation=result.get("api_documentation", []),
                integration_capabilities=result.get("integration_capabilities", []),
                configuration_options=result.get("configuration_options", []),
                pricing_model=result.get("pricing_model"),
                supported_integrations=result.get("supported_integrations", []),
                security_features=result.get("security_features", [])
            )

        except Exception as e:
            logger.warning(f"LLM analysis failed for {platform_name}: {e}")
            return self._basic_analysis(platform_name, exa_results, docs_content, interactive_data)

    def _basic_analysis(self, platform_name: str, exa_results: Dict,
                       docs_content: Dict, interactive_data: Dict) -> PlatformInfo:
        """Fallback analysis without LLM"""

        # Extract API documentation URLs
        api_docs = []
        for category, results in exa_results.items():
            for result in results:
                if hasattr(result, 'url') and any(term in result.url.lower()
                    for term in ['api', 'developer', 'docs']):
                    api_docs.append(result.url)

        # Basic feature extraction from content
        integration_capabilities = []
        for content in docs_content.values():
            if isinstance(content, str):
                content_lower = content.lower()
                if 'webhook' in content_lower:
                    integration_capabilities.append("Webhooks")
                if 'rest api' in content_lower or 'restful' in content_lower:
                    integration_capabilities.append("REST API")
                if 'oauth' in content_lower:
                    integration_capabilities.append("OAuth Authentication")
                if 'graphql' in content_lower:
                    integration_capabilities.append("GraphQL")

        return PlatformInfo(
            name=platform_name,
            description=f"SaaS platform analysis for {platform_name}",
            category="Unknown",
            api_documentation=list(set(api_docs)),
            integration_capabilities=list(set(integration_capabilities)),
            configuration_options=[],
            pricing_model=None,
            supported_integrations=[],
            security_features=[]
        )

    def scan(self) -> DiscoveryResult:
        """Main scan method - discovers platforms and analyzes them"""
        applications = []
        errors = []

        # Get platforms to scan from config
        platforms_to_scan = self.config.get('platforms', ['HubSpot', 'Salesforce', 'Slack'])

        try:
            # Run async scanning
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            for platform_name in platforms_to_scan:
                try:
                    platform_info = loop.run_until_complete(self.scan_platform(platform_name))

                    if platform_info:
                        # Convert to Application object
                        app = Application(
                            id=f"ai_platform_{platform_name.lower()}",
                            name=platform_info.name,
                            type=AppType.SAAS_TOOL,
                            environment=Environment.PRODUCTION,
                            description=platform_info.description,
                            configuration=[
                                ConfigurationItem(
                                    key="category",
                                    value=platform_info.category,
                                    description="Platform category",
                                    source="ai_analysis"
                                ),
                                ConfigurationItem(
                                    key="pricing_model",
                                    value=platform_info.pricing_model,
                                    description="Pricing model",
                                    source="ai_analysis"
                                )
                            ],
                            integrations=[
                                Integration(
                                    name=cap,
                                    type="api",
                                    target_app=platform_name,
                                    configuration={"capability": cap}
                                ) for cap in platform_info.integration_capabilities
                            ],
                            documentation_url=platform_info.api_documentation[0] if platform_info.api_documentation else None,
                            discovered_at=datetime.now()
                        )

                        applications.append(app)

                except Exception as e:
                    error_msg = f"Failed to scan platform {platform_name}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)

            loop.close()

        except Exception as e:
            error_msg = f"AI Platform Scanner failed: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)

        return DiscoveryResult(
            target="ai_platforms",
            applications=applications,
            errors=errors,
            scan_duration=0.0  # Will be calculated by framework
        )