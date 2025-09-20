#!/usr/bin/env python3
"""
ConfigMaster Integration Recommendation Engine

Uses AI analysis to recommend optimal integrations between discovered platforms
based on their capabilities, configurations, and business logic.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import json

# AI/ML imports
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.messages import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Database models
from database.models import (
    Application, PlatformCapability, IntegrationRecommendation,
    PlatformAnalysis, ConfigurationOption
)

logger = logging.getLogger(__name__)

class IntegrationRecommendationEngine:
    """AI-powered engine for generating integration recommendations"""

    def __init__(self, db_session, config: Dict[str, Any] = None):
        self.db = db_session
        self.config = config or {}

        # Initialize AI components
        self.openai_key = self.config.get('openai_api_key')
        self.llm = None

        if LANGCHAIN_AVAILABLE and self.openai_key:
            self.llm = ChatOpenAI(
                model=self.config.get('model', 'gpt-4o-mini'),
                temperature=0.2,
                api_key=self.openai_key
            )

        # Recommendation weights
        self.weights = {
            'business_value': 0.4,
            'technical_feasibility': 0.3,
            'effort_vs_benefit': 0.2,
            'strategic_alignment': 0.1
        }

    def generate_recommendations_for_organization(self) -> List[Dict[str, Any]]:
        """Generate integration recommendations for all applications in the organization"""
        logger.info("Generating organization-wide integration recommendations")

        # Get all active applications
        applications = self.db.query(Application).filter(
            Application.is_active == True
        ).all()

        all_recommendations = []

        # Generate recommendations between all pairs of applications
        for i, source_app in enumerate(applications):
            for target_app in applications[i+1:]:
                recommendations = self._analyze_integration_opportunity(source_app, target_app)
                all_recommendations.extend(recommendations)

        # Generate external platform recommendations
        for app in applications:
            external_recommendations = self._suggest_external_integrations(app)
            all_recommendations.extend(external_recommendations)

        # Score and rank all recommendations
        scored_recommendations = self._score_recommendations(all_recommendations)

        # Save to database
        self._save_recommendations(scored_recommendations)

        return scored_recommendations

    def _analyze_integration_opportunity(self, app1: Application, app2: Application) -> List[Dict[str, Any]]:
        """Analyze potential integrations between two applications"""

        # Get platform analyses and capabilities
        analysis1 = self._get_platform_analysis(app1)
        analysis2 = self._get_platform_analysis(app2)

        capabilities1 = self._get_platform_capabilities(app1)
        capabilities2 = self._get_platform_capabilities(app2)

        if not analysis1 or not analysis2:
            return []

        opportunities = []

        # Check for common integration patterns
        integration_patterns = [
            self._check_data_sync_opportunity(app1, app2, analysis1, analysis2),
            self._check_workflow_automation_opportunity(app1, app2, analysis1, analysis2),
            self._check_notification_opportunity(app1, app2, analysis1, analysis2),
            self._check_reporting_aggregation_opportunity(app1, app2, analysis1, analysis2),
        ]

        for pattern in integration_patterns:
            if pattern:
                opportunities.append(pattern)

        return opportunities

    def _check_data_sync_opportunity(self, app1: Application, app2: Application,
                                   analysis1: Dict, analysis2: Dict) -> Optional[Dict[str, Any]]:
        """Check if apps should sync data (e.g., CRM to Marketing automation)"""

        # Define synergy patterns
        sync_patterns = {
            ('CRM', 'Marketing'): {
                'data_flow': 'bidirectional',
                'use_case': 'Lead nurturing and customer journey tracking',
                'complexity': 'medium',
                'business_value': 0.8
            },
            ('CRM', 'Analytics'): {
                'data_flow': 'crm_to_analytics',
                'use_case': 'Sales performance and customer analytics',
                'complexity': 'low',
                'business_value': 0.7
            },
            ('Marketing', 'Analytics'): {
                'data_flow': 'marketing_to_analytics',
                'use_case': 'Campaign performance and ROI tracking',
                'complexity': 'low',
                'business_value': 0.6
            }
        }

        cat1 = analysis1.get('category', '').split()[0]  # Get first word
        cat2 = analysis2.get('category', '').split()[0]

        pattern_key = (cat1, cat2) if (cat1, cat2) in sync_patterns else (cat2, cat1)

        if pattern_key in sync_patterns:
            pattern = sync_patterns[pattern_key]

            return {
                'type': 'data_sync',
                'source_app': app1,
                'target_app': app2,
                'purpose': pattern['use_case'],
                'complexity': pattern['complexity'],
                'business_value_score': pattern['business_value'],
                'data_flow': pattern['data_flow']
            }

        return None

    def _check_workflow_automation_opportunity(self, app1: Application, app2: Application,
                                             analysis1: Dict, analysis2: Dict) -> Optional[Dict[str, Any]]:
        """Check for workflow automation opportunities"""

        # Look for webhook capabilities
        caps1 = self._get_platform_capabilities(app1)
        caps2 = self._get_platform_capabilities(app2)

        has_webhooks_1 = any(cap.capability_type == 'webhook' for cap in caps1)
        has_webhooks_2 = any(cap.capability_type == 'webhook' for cap in caps2)

        if has_webhooks_1 or has_webhooks_2:
            return {
                'type': 'workflow_automation',
                'source_app': app1,
                'target_app': app2,
                'purpose': 'Automated workflow triggers and actions',
                'complexity': 'medium',
                'business_value_score': 0.6,
                'implementation_notes': 'Use webhooks for real-time automation'
            }

        return None

    def _check_notification_opportunity(self, app1: Application, app2: Application,
                                      analysis1: Dict, analysis2: Dict) -> Optional[Dict[str, Any]]:
        """Check for notification/alert opportunities"""

        # Communication tools should receive notifications from business apps
        communication_types = ['Communication', 'Collaboration', 'Team']
        business_types = ['CRM', 'Marketing', 'Sales', 'Support']

        cat1 = analysis1.get('category', '')
        cat2 = analysis2.get('category', '')

        is_comm_1 = any(comm_type in cat1 for comm_type in communication_types)
        is_business_1 = any(biz_type in cat1 for biz_type in business_types)

        is_comm_2 = any(comm_type in cat2 for comm_type in communication_types)
        is_business_2 = any(biz_type in cat2 for biz_type in business_types)

        if (is_comm_1 and is_business_2) or (is_comm_2 and is_business_1):
            comm_app = app1 if is_comm_1 else app2
            business_app = app2 if is_comm_1 else app1

            return {
                'type': 'notification',
                'source_app': business_app,
                'target_app': comm_app,
                'purpose': 'Send notifications and alerts to team communication channels',
                'complexity': 'low',
                'business_value_score': 0.5,
                'use_cases': ['Deal updates', 'New leads', 'Support tickets', 'Campaign results']
            }

        return None

    def _check_reporting_aggregation_opportunity(self, app1: Application, app2: Application,
                                               analysis1: Dict, analysis2: Dict) -> Optional[Dict[str, Any]]:
        """Check for reporting and analytics aggregation opportunities"""

        analytics_types = ['Analytics', 'BI', 'Reporting', 'Dashboard']
        data_source_types = ['CRM', 'Marketing', 'Sales', 'Support', 'E-commerce']

        cat1 = analysis1.get('category', '')
        cat2 = analysis2.get('category', '')

        is_analytics_1 = any(analytics_type in cat1 for analytics_type in analytics_types)
        is_data_source_1 = any(source_type in cat1 for source_type in data_source_types)

        is_analytics_2 = any(analytics_type in cat2 for analytics_type in analytics_types)
        is_data_source_2 = any(source_type in cat2 for source_type in data_source_types)

        if (is_analytics_1 and is_data_source_2) or (is_analytics_2 and is_data_source_1):
            analytics_app = app1 if is_analytics_1 else app2
            data_app = app2 if is_analytics_1 else app1

            return {
                'type': 'reporting_aggregation',
                'source_app': data_app,
                'target_app': analytics_app,
                'purpose': 'Aggregate data for comprehensive reporting and analytics',
                'complexity': 'medium',
                'business_value_score': 0.7,
                'benefits': ['Unified reporting', 'Better insights', 'Data correlation']
            }

        return None

    def _suggest_external_integrations(self, app: Application) -> List[Dict[str, Any]]:
        """Suggest integrations with external platforms not in our system"""

        analysis = self._get_platform_analysis(app)
        if not analysis:
            return []

        category = analysis.get('category', '')
        suggestions = []

        # Common external integrations by category
        external_suggestions = {
            'CRM': [
                {'platform': 'Zapier', 'purpose': 'Connect to 2000+ apps', 'complexity': 'low'},
                {'platform': 'Slack', 'purpose': 'Team notifications', 'complexity': 'low'},
                {'platform': 'Gmail', 'purpose': 'Email integration', 'complexity': 'low'},
            ],
            'Marketing': [
                {'platform': 'Google Analytics', 'purpose': 'Track campaign performance', 'complexity': 'medium'},
                {'platform': 'Facebook Ads', 'purpose': 'Social media advertising', 'complexity': 'medium'},
                {'platform': 'Mailchimp', 'purpose': 'Email marketing automation', 'complexity': 'low'},
            ],
            'Analytics': [
                {'platform': 'Google Sheets', 'purpose': 'Export reports and data', 'complexity': 'low'},
                {'platform': 'Tableau', 'purpose': 'Advanced data visualization', 'complexity': 'high'},
                {'platform': 'Power BI', 'purpose': 'Business intelligence dashboards', 'complexity': 'medium'},
            ]
        }

        for category_key, platforms in external_suggestions.items():
            if category_key.lower() in category.lower():
                for platform in platforms:
                    suggestions.append({
                        'type': 'external_integration',
                        'source_app': app,
                        'target_app': None,
                        'target_platform_name': platform['platform'],
                        'purpose': platform['purpose'],
                        'complexity': platform['complexity'],
                        'business_value_score': 0.6  # Default for external integrations
                    })

        return suggestions

    def _score_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score and rank all recommendations"""

        for rec in recommendations:
            # Calculate technical feasibility
            rec['technical_feasibility_score'] = self._calculate_technical_feasibility(rec)

            # Calculate effort vs benefit
            rec['effort_vs_benefit_score'] = self._calculate_effort_benefit_ratio(rec)

            # Calculate strategic alignment
            rec['strategic_alignment_score'] = self._calculate_strategic_alignment(rec)

            # Calculate overall score
            rec['overall_score'] = (
                rec['business_value_score'] * self.weights['business_value'] +
                rec['technical_feasibility_score'] * self.weights['technical_feasibility'] +
                rec['effort_vs_benefit_score'] * self.weights['effort_vs_benefit'] +
                rec['strategic_alignment_score'] * self.weights['strategic_alignment']
            )

        # Sort by overall score
        recommendations.sort(key=lambda x: x['overall_score'], reverse=True)

        return recommendations

    def _calculate_technical_feasibility(self, recommendation: Dict[str, Any]) -> float:
        """Calculate how technically feasible an integration is"""

        source_app = recommendation['source_app']
        target_app = recommendation.get('target_app')

        # Check API capabilities
        source_caps = self._get_platform_capabilities(source_app)
        api_score = 0.5  # Default

        # Higher score if REST API available
        if any(cap.capability_type == 'api' for cap in source_caps):
            api_score = 0.8

        # Even higher if webhooks available
        if any(cap.capability_type == 'webhook' for cap in source_caps):
            api_score = 1.0

        # Complexity modifier
        complexity = recommendation.get('complexity', 'medium')
        complexity_modifiers = {'low': 1.0, 'medium': 0.8, 'high': 0.6}

        return api_score * complexity_modifiers.get(complexity, 0.8)

    def _calculate_effort_benefit_ratio(self, recommendation: Dict[str, Any]) -> float:
        """Calculate effort vs benefit ratio"""

        business_value = recommendation.get('business_value_score', 0.5)
        complexity = recommendation.get('complexity', 'medium')

        # Effort estimates
        effort_estimates = {'low': 10, 'medium': 40, 'high': 100}  # hours
        estimated_effort = effort_estimates.get(complexity, 40)

        # Higher business value / lower effort = better score
        if estimated_effort > 0:
            ratio = business_value / (estimated_effort / 100)  # Normalize effort
            return min(ratio, 1.0)  # Cap at 1.0

        return 0.5

    def _calculate_strategic_alignment(self, recommendation: Dict[str, Any]) -> float:
        """Calculate how well this aligns with organizational strategy"""

        # This could be enhanced with organization-specific rules
        # For now, use some simple heuristics

        rec_type = recommendation.get('type', '')

        # Prioritize certain types of integrations
        type_priorities = {
            'data_sync': 0.9,
            'workflow_automation': 0.8,
            'reporting_aggregation': 0.7,
            'notification': 0.6,
            'external_integration': 0.5
        }

        return type_priorities.get(rec_type, 0.5)

    def _get_platform_analysis(self, app: Application) -> Optional[Dict[str, Any]]:
        """Get the latest platform analysis for an application"""

        analysis = self.db.query(PlatformAnalysis).filter(
            PlatformAnalysis.application_id == app.id
        ).order_by(PlatformAnalysis.analysis_timestamp.desc()).first()

        if analysis:
            return {
                'category': analysis.category,
                'primary_functions': analysis.primary_functions,
                'api_capabilities': analysis.api_capabilities,
                'integration_ecosystem': analysis.integration_ecosystem,
                'confidence_score': analysis.confidence_score
            }

        # Fallback to basic analysis from application data
        return {
            'category': app.type.replace('_', ' ').title(),
            'primary_functions': [],
            'api_capabilities': [],
            'integration_ecosystem': [],
            'confidence_score': 0.5
        }

    def _get_platform_capabilities(self, app: Application) -> List:
        """Get all capabilities for a platform"""

        return self.db.query(PlatformCapability).filter(
            PlatformCapability.application_id == app.id,
            PlatformCapability.is_active == True
        ).all()

    def _save_recommendations(self, recommendations: List[Dict[str, Any]]):
        """Save recommendations to the database"""

        for rec_data in recommendations:
            # Check if recommendation already exists
            existing = self.db.query(IntegrationRecommendation).filter(
                IntegrationRecommendation.source_app_id == rec_data['source_app'].id,
                IntegrationRecommendation.target_app_id == getattr(rec_data.get('target_app'), 'id', None),
                IntegrationRecommendation.target_platform_name == rec_data.get('target_platform_name'),
                IntegrationRecommendation.recommendation_type == rec_data['type']
            ).first()

            if existing:
                # Update existing recommendation
                existing.purpose = rec_data['purpose']
                existing.complexity = rec_data['complexity']
                existing.ai_confidence = rec_data.get('overall_score', 0.5)
                existing.business_value_score = rec_data['business_value_score']
                existing.technical_feasibility_score = rec_data['technical_feasibility_score']
                existing.updated_at = datetime.utcnow()
            else:
                # Create new recommendation
                recommendation = IntegrationRecommendation(
                    source_app_id=rec_data['source_app'].id,
                    target_app_id=getattr(rec_data.get('target_app'), 'id', None),
                    target_platform_name=rec_data.get('target_platform_name'),
                    recommendation_type=rec_data['type'],
                    purpose=rec_data['purpose'],
                    complexity=rec_data['complexity'],
                    priority='high' if rec_data.get('overall_score', 0) > 0.7 else 'medium',
                    benefits=rec_data.get('benefits', []),
                    use_cases=rec_data.get('use_cases', []),
                    ai_confidence=rec_data.get('overall_score', 0.5),
                    business_value_score=rec_data['business_value_score'],
                    technical_feasibility_score=rec_data['technical_feasibility_score']
                )
                self.db.add(recommendation)

        self.db.commit()
        logger.info(f"Saved {len(recommendations)} integration recommendations")

    def get_recommendations_for_app(self, app_id: str) -> List[Dict[str, Any]]:
        """Get all recommendations for a specific application"""

        recommendations = self.db.query(IntegrationRecommendation).filter(
            IntegrationRecommendation.source_app_id == app_id,
            IntegrationRecommendation.status == 'suggested'
        ).order_by(IntegrationRecommendation.business_value_score.desc()).all()

        return [self._recommendation_to_dict(rec) for rec in recommendations]

    def _recommendation_to_dict(self, rec: IntegrationRecommendation) -> Dict[str, Any]:
        """Convert recommendation model to dictionary"""

        return {
            'id': rec.id,
            'type': rec.recommendation_type,
            'purpose': rec.purpose,
            'target_platform': rec.target_platform_name or (rec.target_app.name if rec.target_app else None),
            'complexity': rec.complexity,
            'priority': rec.priority,
            'business_value_score': rec.business_value_score,
            'technical_feasibility_score': rec.technical_feasibility_score,
            'ai_confidence': rec.ai_confidence,
            'benefits': rec.benefits,
            'use_cases': rec.use_cases,
            'estimated_effort_hours': rec.estimated_effort_hours,
            'status': rec.status,
            'created_at': rec.created_at.isoformat()
        }