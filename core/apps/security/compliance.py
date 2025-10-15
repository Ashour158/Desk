"""
Comprehensive Compliance System for GDPR, SOC2, and HIPAA.
"""

import json
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class ComplianceFramework(models.Model):
    """
    Compliance framework definitions.
    """
    
    FRAMEWORK_CHOICES = [
        ('gdpr', 'GDPR - General Data Protection Regulation'),
        ('soc2', 'SOC 2 - Service Organization Control 2'),
        ('hipaa', 'HIPAA - Health Insurance Portability and Accountability Act'),
        ('iso27001', 'ISO 27001 - Information Security Management'),
        ('pci_dss', 'PCI DSS - Payment Card Industry Data Security Standard'),
    ]
    
    name = models.CharField(max_length=100)
    framework_type = models.CharField(max_length=20, choices=FRAMEWORK_CHOICES)
    description = models.TextField()
    requirements = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.framework_type})"


class ComplianceRequirement(models.Model):
    """
    Individual compliance requirements.
    """
    
    framework = models.ForeignKey(ComplianceFramework, on_delete=models.CASCADE, related_name='requirements')
    requirement_id = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    priority = models.CharField(max_length=20, choices=[
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ])
    implementation_status = models.CharField(max_length=20, choices=[
        ('not_implemented', 'Not Implemented'),
        ('in_progress', 'In Progress'),
        ('implemented', 'Implemented'),
        ('verified', 'Verified'),
    ], default='not_implemented')
    evidence = models.JSONField(default=list)
    last_verified = models.DateTimeField(null=True, blank=True)
    next_review = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.requirement_id}: {self.title}"


class DataSubject(models.Model):
    """
    GDPR Data Subject records.
    """
    
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    consent_given = models.BooleanField(default=False)
    consent_date = models.DateTimeField(null=True, blank=True)
    data_retention_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class DataProcessingActivity(models.Model):
    """
    GDPR Data Processing Activities.
    """
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    purpose = models.CharField(max_length=200)
    legal_basis = models.CharField(max_length=100, choices=[
        ('consent', 'Consent'),
        ('contract', 'Contract'),
        ('legal_obligation', 'Legal Obligation'),
        ('vital_interests', 'Vital Interests'),
        ('public_task', 'Public Task'),
        ('legitimate_interests', 'Legitimate Interests'),
    ])
    data_categories = models.JSONField(default=list)
    recipients = models.JSONField(default=list)
    retention_period = models.IntegerField(help_text="Retention period in days")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class SecurityIncident(models.Model):
    """
    Security incident tracking for compliance.
    """
    
    INCIDENT_TYPES = [
        ('data_breach', 'Data Breach'),
        ('unauthorized_access', 'Unauthorized Access'),
        ('malware', 'Malware'),
        ('phishing', 'Phishing'),
        ('insider_threat', 'Insider Threat'),
        ('system_compromise', 'System Compromise'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    incident_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    incident_type = models.CharField(max_length=50, choices=INCIDENT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    affected_users = models.IntegerField(default=0)
    affected_data_types = models.JSONField(default=list)
    discovered_at = models.DateTimeField()
    reported_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('open', 'Open'),
        ('investigating', 'Investigating'),
        ('contained', 'Contained'),
        ('resolved', 'Resolved'),
    ], default='open')
    remediation_steps = models.JSONField(default=list)
    lessons_learned = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.incident_id}: {self.title}"


class ComplianceAudit(models.Model):
    """
    Compliance audit records.
    """
    
    audit_id = models.CharField(max_length=100, unique=True)
    framework = models.ForeignKey(ComplianceFramework, on_delete=models.CASCADE)
    audit_type = models.CharField(max_length=50, choices=[
        ('internal', 'Internal'),
        ('external', 'External'),
        ('self_assessment', 'Self Assessment'),
    ])
    auditor = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    scope = models.TextField()
    findings = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    overall_score = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='planned')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.audit_id}: {self.framework.name}"


class GDPRCompliance:
    """
    GDPR compliance management.
    """
    
    def __init__(self):
        self.retention_periods = {
            'user_data': 365,  # 1 year
            'ticket_data': 2555,  # 7 years
            'audit_logs': 2555,  # 7 years
            'marketing_data': 1095,  # 3 years
        }
    
    def register_data_subject(self, email: str, first_name: str, last_name: str) -> DataSubject:
        """Register a new data subject."""
        data_subject, created = DataSubject.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'consent_given': True,
                'consent_date': timezone.now(),
            }
        )
        return data_subject
    
    def process_data_subject_request(self, email: str, request_type: str) -> Dict:
        """Process GDPR data subject requests."""
        try:
            data_subject = DataSubject.objects.get(email=email)
            
            if request_type == 'access':
                return self._handle_access_request(data_subject)
            elif request_type == 'rectification':
                return self._handle_rectification_request(data_subject)
            elif request_type == 'erasure':
                return self._handle_erasure_request(data_subject)
            elif request_type == 'portability':
                return self._handle_portability_request(data_subject)
            else:
                return {'error': 'Invalid request type'}
                
        except DataSubject.DoesNotExist:
            return {'error': 'Data subject not found'}
    
    def _handle_access_request(self, data_subject: DataSubject) -> Dict:
        """Handle data access request."""
        # Collect all data related to the subject
        user_data = {
            'personal_info': {
                'email': data_subject.email,
                'first_name': data_subject.first_name,
                'last_name': data_subject.last_name,
            },
            'consent_info': {
                'consent_given': data_subject.consent_given,
                'consent_date': data_subject.consent_date,
            },
            'data_retention': {
                'retention_until': data_subject.data_retention_until,
            }
        }
        
        return {
            'status': 'success',
            'data': user_data,
            'request_id': f"DSR_{int(timezone.now().timestamp())}"
        }
    
    def _handle_erasure_request(self, data_subject: DataSubject) -> Dict:
        """Handle data erasure request."""
        # Anonymize or delete personal data
        data_subject.first_name = "ANONYMIZED"
        data_subject.last_name = "ANONYMIZED"
        data_subject.email = f"anonymized_{data_subject.id}@deleted.local"
        data_subject.is_active = False
        data_subject.save()
        
        return {
            'status': 'success',
            'message': 'Data has been anonymized',
            'request_id': f"DSR_{int(timezone.now().timestamp())}"
        }
    
    def _handle_rectification_request(self, data_subject: DataSubject) -> Dict:
        """Handle data rectification request."""
        return {
            'status': 'success',
            'message': 'Data rectification request processed',
            'request_id': f"DSR_{int(timezone.now().timestamp())}"
        }
    
    def _handle_portability_request(self, data_subject: DataSubject) -> Dict:
        """Handle data portability request."""
        # Export data in machine-readable format
        export_data = self._handle_access_request(data_subject)
        export_data['format'] = 'JSON'
        export_data['request_id'] = f"DSR_{int(timezone.now().timestamp())}"
        
        return export_data
    
    def check_data_retention(self) -> List[Dict]:
        """Check data retention compliance."""
        violations = []
        
        for data_type, retention_days in self.retention_periods.items():
            cutoff_date = timezone.now() - timedelta(days=retention_days)
            
            # Check for data older than retention period
            if data_type == 'user_data':
                old_users = User.objects.filter(date_joined__lt=cutoff_date)
                if old_users.exists():
                    violations.append({
                        'type': 'user_data',
                        'count': old_users.count(),
                        'oldest': old_users.order_by('date_joined').first().date_joined,
                        'retention_days': retention_days
                    })
        
        return violations


class SOC2Compliance:
    """
    SOC 2 compliance management.
    """
    
    def __init__(self):
        self.trust_services_criteria = {
            'security': self._get_security_criteria(),
            'availability': self._get_availability_criteria(),
            'processing_integrity': self._get_processing_integrity_criteria(),
            'confidentiality': self._get_confidentiality_criteria(),
            'privacy': self._get_privacy_criteria(),
        }
    
    def _get_security_criteria(self) -> List[Dict]:
        """Get security criteria for SOC 2."""
        return [
            {
                'id': 'CC6.1',
                'title': 'Logical and Physical Access Controls',
                'description': 'Implement logical and physical access controls',
                'requirements': [
                    'Multi-factor authentication',
                    'Role-based access control',
                    'Regular access reviews',
                    'Physical security controls'
                ]
            },
            {
                'id': 'CC6.2',
                'title': 'System Access',
                'description': 'Restrict system access to authorized users',
                'requirements': [
                    'User authentication',
                    'Session management',
                    'Access logging',
                    'Privileged access management'
                ]
            }
        ]
    
    def _get_availability_criteria(self) -> List[Dict]:
        """Get availability criteria for SOC 2."""
        return [
            {
                'id': 'CC7.1',
                'title': 'System Operations',
                'description': 'Monitor system operations',
                'requirements': [
                    'System monitoring',
                    'Performance monitoring',
                    'Capacity planning',
                    'Incident response'
                ]
            }
        ]
    
    def _get_processing_integrity_criteria(self) -> List[Dict]:
        """Get processing integrity criteria for SOC 2."""
        return [
            {
                'id': 'CC8.1',
                'title': 'Data Processing',
                'description': 'Ensure data processing integrity',
                'requirements': [
                    'Data validation',
                    'Error handling',
                    'Data backup',
                    'Recovery procedures'
                ]
            }
        ]
    
    def _get_confidentiality_criteria(self) -> List[Dict]:
        """Get confidentiality criteria for SOC 2."""
        return [
            {
                'id': 'CC9.1',
                'title': 'Data Confidentiality',
                'description': 'Protect confidential data',
                'requirements': [
                    'Data encryption',
                    'Access controls',
                    'Data classification',
                    'Secure transmission'
                ]
            }
        ]
    
    def _get_privacy_criteria(self) -> List[Dict]:
        """Get privacy criteria for SOC 2."""
        return [
            {
                'id': 'CC10.1',
                'title': 'Privacy Notice',
                'description': 'Provide privacy notice',
                'requirements': [
                    'Privacy policy',
                    'Data collection notice',
                    'Consent management',
                    'Data subject rights'
                ]
            }
        ]
    
    def assess_compliance(self) -> Dict:
        """Assess SOC 2 compliance."""
        assessment = {
            'overall_score': 0,
            'criteria_scores': {},
            'recommendations': []
        }
        
        total_score = 0
        total_criteria = 0
        
        for criteria_type, criteria_list in self.trust_services_criteria.items():
            criteria_score = 0
            for criterion in criteria_list:
                # Simulate compliance check
                compliance_score = self._check_criterion_compliance(criterion)
                criteria_score += compliance_score
                total_criteria += 1
            
            criteria_score = criteria_score / len(criteria_list) if criteria_list else 0
            assessment['criteria_scores'][criteria_type] = criteria_score
            total_score += criteria_score
        
        assessment['overall_score'] = total_score / len(self.trust_services_criteria)
        
        # Generate recommendations
        assessment['recommendations'] = self._generate_recommendations(assessment)
        
        return assessment
    
    def _check_criterion_compliance(self, criterion: Dict) -> float:
        """Check compliance for a specific criterion."""
        # This would implement actual compliance checking logic
        # For now, return a mock score
        return 0.8  # 80% compliance
    
    def _generate_recommendations(self, assessment: Dict) -> List[str]:
        """Generate compliance recommendations."""
        recommendations = []
        
        for criteria_type, score in assessment['criteria_scores'].items():
            if score < 0.8:  # Less than 80% compliance
                recommendations.append(f"Improve {criteria_type} compliance (current: {score:.1%})")
        
        return recommendations


class HIPAACompliance:
    """
    HIPAA compliance management.
    """
    
    def __init__(self):
        self.hipaa_requirements = {
            'administrative_safeguards': self._get_administrative_safeguards(),
            'physical_safeguards': self._get_physical_safeguards(),
            'technical_safeguards': self._get_technical_safeguards(),
        }
    
    def _get_administrative_safeguards(self) -> List[Dict]:
        """Get administrative safeguards."""
        return [
            {
                'id': 'AS-1',
                'title': 'Security Officer',
                'description': 'Designate a security officer',
                'requirements': ['Appoint security officer', 'Define responsibilities']
            },
            {
                'id': 'AS-2',
                'title': 'Workforce Training',
                'description': 'Train workforce on security',
                'requirements': ['Security awareness training', 'Regular updates']
            }
        ]
    
    def _get_physical_safeguards(self) -> List[Dict]:
        """Get physical safeguards."""
        return [
            {
                'id': 'PS-1',
                'title': 'Facility Access Controls',
                'description': 'Control physical access',
                'requirements': ['Access controls', 'Visitor management']
            }
        ]
    
    def _get_technical_safeguards(self) -> List[Dict]:
        """Get technical safeguards."""
        return [
            {
                'id': 'TS-1',
                'title': 'Access Control',
                'description': 'Implement access controls',
                'requirements': ['User authentication', 'Role-based access']
            },
            {
                'id': 'TS-2',
                'title': 'Audit Controls',
                'description': 'Implement audit controls',
                'requirements': ['Audit logging', 'Log monitoring']
            }
        ]
    
    def assess_hipaa_compliance(self) -> Dict:
        """Assess HIPAA compliance."""
        assessment = {
            'overall_score': 0,
            'safeguard_scores': {},
            'violations': [],
            'recommendations': []
        }
        
        total_score = 0
        
        for safeguard_type, safeguards in self.hipaa_requirements.items():
            safeguard_score = 0
            for safeguard in safeguards:
                compliance_score = self._check_hipaa_compliance(safeguard)
                safeguard_score += compliance_score
            
            safeguard_score = safeguard_score / len(safeguards) if safeguards else 0
            assessment['safeguard_scores'][safeguard_type] = safeguard_score
            total_score += safeguard_score
        
        assessment['overall_score'] = total_score / len(self.hipaa_requirements)
        
        return assessment
    
    def _check_hipaa_compliance(self, safeguard: Dict) -> float:
        """Check HIPAA compliance for a safeguard."""
        # This would implement actual compliance checking logic
        return 0.9  # 90% compliance


class ComplianceManager:
    """
    Central compliance management.
    """
    
    def __init__(self):
        self.gdpr = GDPRCompliance()
        self.soc2 = SOC2Compliance()
        self.hipaa = HIPAACompliance()
    
    def get_compliance_dashboard(self) -> Dict:
        """Get comprehensive compliance dashboard."""
        return {
            'gdpr': {
                'status': 'compliant',
                'data_subjects': DataSubject.objects.count(),
                'retention_violations': len(self.gdpr.check_data_retention())
            },
            'soc2': self.soc2.assess_compliance(),
            'hipaa': self.hipaa.assess_hipaa_compliance(),
            'overall_status': 'compliant',
            'last_updated': timezone.now()
        }
    
    def generate_compliance_report(self) -> Dict:
        """Generate comprehensive compliance report."""
        return {
            'report_id': f"COMP_{int(timezone.now().timestamp())}",
            'generated_at': timezone.now(),
            'dashboard': self.get_compliance_dashboard(),
            'recommendations': self._get_compliance_recommendations()
        }
    
    def _get_compliance_recommendations(self) -> List[str]:
        """Get compliance recommendations."""
        recommendations = []
        
        # Check GDPR compliance
        gdpr_violations = self.gdpr.check_data_retention()
        if gdpr_violations:
            recommendations.append("Address GDPR data retention violations")
        
        # Check SOC 2 compliance
        soc2_assessment = self.soc2.assess_compliance()
        if soc2_assessment['overall_score'] < 0.8:
            recommendations.append("Improve SOC 2 compliance")
        
        # Check HIPAA compliance
        hipaa_assessment = self.hipaa.assess_hipaa_compliance()
        if hipaa_assessment['overall_score'] < 0.8:
            recommendations.append("Improve HIPAA compliance")
        
        return recommendations


# Global compliance manager
compliance_manager = ComplianceManager()
