#!/usr/bin/env python3
"""
Security Audit Suite for LAIT Platform
Comprehensive security review and vulnerability assessment
"""

import os
import json
import hashlib
import re
import subprocess
import requests
from typing import Dict, List, Any
from pathlib import Path

class SecurityAuditor:
    def __init__(self):
        self.audit_results = {
            "authentication": {},
            "authorization": {},
            "input_validation": {},
            "data_protection": {},
            "api_security": {},
            "dependencies": {},
            "configuration": {},
            "overall_score": 0,
            "critical_issues": [],
            "high_issues": [],
            "medium_issues": [],
            "low_issues": []
        }
        
    def log(self, message: str, level: str = "INFO"):
        print(f"[SECURITY] [{level}] {message}")
    
    def audit_authentication(self):
        """Audit authentication mechanisms"""
        self.log("Auditing Authentication", "AUDIT")
        
        issues = []
        score = 100
        
        # Check JWT implementation
        jwt_files = [
            "backend/auth.py",
            "backend/routes/auth.py"
        ]
        
        for file_path in jwt_files:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                    # Check for hardcoded secrets
                    if re.search(r'secret.*=.*["\'][^"\']{10,}["\']', content):
                        issues.append(f"Hardcoded secret found in {file_path}")
                        score -= 20
                    
                    # Check for weak JWT configuration
                    if 'JWT_SECRET_KEY' in content and 'test' in content.lower():
                        issues.append(f"Test JWT secret in {file_path}")
                        score -= 15
                    
                    # Check for proper token expiration
                    if 'expires_delta' not in content and 'exp' not in content:
                        issues.append(f"No token expiration found in {file_path}")
                        score -= 10
        
        self.audit_results["authentication"] = {
            "score": max(0, score),
            "issues": issues,
            "recommendations": [
                "Use environment variables for secrets",
                "Implement proper token expiration",
                "Add rate limiting for auth endpoints",
                "Use HTTPS in production"
            ]
        }
    
    def audit_authorization(self):
        """Audit authorization mechanisms"""
        self.log("Auditing Authorization", "AUDIT")
        
        issues = []
        score = 100
        
        # Check role-based access control
        auth_files = [
            "backend/routes/admin.py",
            "backend/routes/analytics.py"
        ]
        
        for file_path in auth_files:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                    # Check for proper role checks
                    if '@role_required' not in content and 'admin' in content.lower():
                        issues.append(f"Missing role checks in {file_path}")
                        score -= 15
                    
                    # Check for proper JWT validation
                    if '@jwt_required' not in content and 'get_jwt_identity' in content:
                        issues.append(f"Missing JWT validation in {file_path}")
                        score -= 10
        
        self.audit_results["authorization"] = {
            "score": max(0, score),
            "issues": issues,
            "recommendations": [
                "Implement proper role-based access control",
                "Add JWT validation to all protected endpoints",
                "Use principle of least privilege",
                "Audit access logs regularly"
            ]
        }
    
    def audit_input_validation(self):
        """Audit input validation"""
        self.log("Auditing Input Validation", "AUDIT")
        
        issues = []
        score = 100
        
        # Check for SQL injection vulnerabilities
        route_files = [
            "backend/routes/analytics.py",
            "backend/routes/vendors.py",
            "backend/routes/invoices.py"
        ]
        
        for file_path in route_files:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                    # Check for direct string concatenation in queries
                    if re.search(r'query.*\+.*request\.', content):
                        issues.append(f"Potential SQL injection in {file_path}")
                        score -= 25
                    
                    # Check for proper parameter validation
                    if 'request.args.get' in content and 'validation' not in content:
                        issues.append(f"Missing input validation in {file_path}")
                        score -= 10
        
        self.audit_results["input_validation"] = {
            "score": max(0, score),
            "issues": issues,
            "recommendations": [
                "Use parameterized queries",
                "Validate all user inputs",
                "Implement input sanitization",
                "Use ORM for database operations"
            ]
        }
    
    def audit_data_protection(self):
        """Audit data protection measures"""
        self.log("Auditing Data Protection", "AUDIT")
        
        issues = []
        score = 100
        
        # Check for sensitive data exposure
        config_files = [
            "backend/config.py",
            "backend/enhanced_app.py"
        ]
        
        for file_path in config_files:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                    # Check for hardcoded database credentials
                    if re.search(r'password.*=.*["\'][^"\']+["\']', content):
                        issues.append(f"Hardcoded credentials in {file_path}")
                        score -= 20
                    
                    # Check for debug mode in production
                    if 'DEBUG = True' in content:
                        issues.append(f"Debug mode enabled in {file_path}")
                        score -= 15
        
        self.audit_results["data_protection"] = {
            "score": max(0, score),
            "issues": issues,
            "recommendations": [
                "Use environment variables for sensitive data",
                "Encrypt data at rest",
                "Implement proper logging without sensitive data",
                "Use HTTPS for data transmission"
            ]
        }
    
    def audit_api_security(self):
        """Audit API security"""
        self.log("Auditing API Security", "AUDIT")
        
        issues = []
        score = 100
        
        # Check for CORS configuration
        app_file = "backend/enhanced_app.py"
        if os.path.exists(app_file):
            with open(app_file, 'r') as f:
                content = f.read()
                
                # Check for overly permissive CORS
                if 'CORS' in content and '*' in content:
                    issues.append("Overly permissive CORS configuration")
                    score -= 15
                
                # Check for rate limiting
                if 'Limiter' not in content:
                    issues.append("No rate limiting configured")
                    score -= 10
        
        self.audit_results["api_security"] = {
            "score": max(0, score),
            "issues": issues,
            "recommendations": [
                "Implement proper CORS policy",
                "Add rate limiting",
                "Use API versioning",
                "Implement request validation"
            ]
        }
    
    def audit_dependencies(self):
        """Audit dependencies for vulnerabilities"""
        self.log("Auditing Dependencies", "AUDIT")
        
        issues = []
        score = 100
        
        # Check Python dependencies
        requirements_file = "backend/requirements.txt"
        if os.path.exists(requirements_file):
            try:
                result = subprocess.run(
                    ["pip", "list", "--outdated"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.stdout:
                    outdated_packages = len(result.stdout.strip().split('\n')) - 1
                    if outdated_packages > 0:
                        issues.append(f"{outdated_packages} outdated packages found")
                        score -= min(20, outdated_packages * 2)
            except Exception as e:
                issues.append(f"Could not check dependencies: {str(e)}")
                score -= 5
        
        self.audit_results["dependencies"] = {
            "score": max(0, score),
            "issues": issues,
            "recommendations": [
                "Update outdated packages",
                "Use dependency scanning tools",
                "Pin dependency versions",
                "Regular security updates"
            ]
        }
    
    def audit_configuration(self):
        """Audit configuration security"""
        self.log("Auditing Configuration", "AUDIT")
        
        issues = []
        score = 100
        
        # Check for secure configuration
        config_issues = []
        
        # Check if debug mode is disabled
        if os.path.exists("backend/enhanced_app.py"):
            with open("backend/enhanced_app.py", 'r') as f:
                content = f.read()
                if 'debug=True' in content or 'DEBUG = True' in content:
                    config_issues.append("Debug mode enabled")
                    score -= 15
        
        # Check for proper error handling
        if not config_issues:
            score += 10
        
        self.audit_results["configuration"] = {
            "score": max(0, score),
            "issues": config_issues,
            "recommendations": [
                "Disable debug mode in production",
                "Use secure headers",
                "Implement proper error handling",
                "Use environment-specific configurations"
            ]
        }
    
    def calculate_overall_score(self):
        """Calculate overall security score"""
        categories = [
            "authentication",
            "authorization", 
            "input_validation",
            "data_protection",
            "api_security",
            "dependencies",
            "configuration"
        ]
        
        total_score = 0
        for category in categories:
            if category in self.audit_results:
                total_score += self.audit_results[category]["score"]
        
        self.audit_results["overall_score"] = total_score / len(categories)
        
        # Categorize issues by severity
        for category in categories:
            if category in self.audit_results:
                for issue in self.audit_results[category]["issues"]:
                    if "SQL injection" in issue or "Hardcoded secret" in issue:
                        self.audit_results["critical_issues"].append(f"{category}: {issue}")
                    elif "Missing" in issue and "validation" in issue:
                        self.audit_results["high_issues"].append(f"{category}: {issue}")
                    elif "outdated" in issue.lower():
                        self.audit_results["medium_issues"].append(f"{category}: {issue}")
                    else:
                        self.audit_results["low_issues"].append(f"{category}: {issue}")
    
    def generate_report(self):
        """Generate security audit report"""
        self.log("Generating Security Audit Report", "REPORT")
        
        report = {
            "timestamp": "2025-06-22",
            "overall_score": self.audit_results["overall_score"],
            "critical_issues_count": len(self.audit_results["critical_issues"]),
            "high_issues_count": len(self.audit_results["high_issues"]),
            "medium_issues_count": len(self.audit_results["medium_issues"]),
            "low_issues_count": len(self.audit_results["low_issues"]),
            "detailed_results": self.audit_results
        }
        
        # Save report
        with open("security_audit_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("SECURITY AUDIT RESULTS SUMMARY")
        print("="*60)
        print(f"Overall Security Score: {report['overall_score']:.1f}/100")
        print(f"Critical Issues: {report['critical_issues_count']}")
        print(f"High Issues: {report['high_issues_count']}")
        print(f"Medium Issues: {report['medium_issues_count']}")
        print(f"Low Issues: {report['low_issues_count']}")
        
        if report['critical_issues_count'] > 0:
            print("\n🚨 CRITICAL ISSUES:")
            for issue in self.audit_results["critical_issues"][:3]:
                print(f"  - {issue}")
        
        if report['high_issues_count'] > 0:
            print("\n⚠️ HIGH PRIORITY ISSUES:")
            for issue in self.audit_results["high_issues"][:3]:
                print(f"  - {issue}")
        
        print("="*60)
        print("Detailed report saved to: security_audit_report.json")
        
        return report
    
    def run_audit(self):
        """Run complete security audit"""
        self.log("Starting Comprehensive Security Audit", "START")
        
        self.audit_authentication()
        self.audit_authorization()
        self.audit_input_validation()
        self.audit_data_protection()
        self.audit_api_security()
        self.audit_dependencies()
        self.audit_configuration()
        
        self.calculate_overall_score()
        self.generate_report()

def main():
    """Main function to run security audit"""
    auditor = SecurityAuditor()
    auditor.run_audit()

if __name__ == "__main__":
    main() 