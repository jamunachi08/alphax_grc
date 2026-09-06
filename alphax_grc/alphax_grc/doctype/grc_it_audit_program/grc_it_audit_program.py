import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate


# 146-control library from IT General Controls Audit Program Tool (Shahidul Islam CISA/CISM/CISSP/CCSP)
IT_CONTROLS_LIBRARY = [
    # GLBA 501(b) Compliance
    ("GLBA Compliance", "GLBA", 1, "Board and management oversight", "BoD/SLT meeting minutes past 12 months", True, False, False, True, False),
    ("GLBA Compliance", "GLBA", 2, "Board and management oversight", "Supervisory Committee meeting minutes past 12 months", True, False, False, True, False),
    ("GLBA Compliance", "GLBA", 3, "Board and management oversight", "IT Steering Committee minutes/agendas past 12 months", True, False, False, True, False),
    ("GLBA Compliance", "GLBA", 4, "Board and management oversight", "Impact of organizational changes on InfoSec program", True, False, False, True, False),
    ("GLBA Compliance", "GLBA", 5, "Employee education and security awareness/training", "Phishing test results past 12 months", True, True, False, True, False),
    ("GLBA Compliance", "GLBA", 6, "Employee education and security awareness/training", "Call center procedures to authenticate members", True, False, False, False, False),
    ("GLBA Compliance", "GLBA", 7, "Employee education and security awareness/training", "Security awareness training records", True, False, False, True, False),
    ("GLBA Compliance", "GLBA", 8, "Risk Management", "ERM program documentation, policies and procedures", True, False, False, True, True),
    ("GLBA Compliance", "GLBA", 9, "Risk Management", "Risk assessments conducted past year", False, False, False, False, False),
    ("GLBA Compliance", "GLBA", 10, "Risk Management", "Risk register showing all IT related items", False, False, False, False, False),
    ("GLBA Compliance", "GLBA", 11, "Risk Management", "List of critical IT assets and identified security risks", False, False, False, False, False),
    ("GLBA Compliance", "GLBA", 12, "Risk Management", "ERM minutes/agendas and reports", False, False, False, False, False),
    ("GLBA Compliance", "GLBA", 13, "User Access Management", "Core application user accounts and permission matrix", True, True, False, False, False),
    ("GLBA Compliance", "GLBA", 14, "User Access Management", "HOST computer user accounts and permissions", False, False, False, False, False),
    ("GLBA Compliance", "GLBA", 15, "User Access Management", "Authentication and access control policies", False, False, False, False, False),
    ("GLBA Compliance", "GLBA", 16, "User Access Management", "Remote access policies and procedures", False, False, False, False, False),
    ("GLBA Compliance", "GLBA", 17, "Monitoring and Logging", "Vulnerability Management policies and procedures", True, False, True, False, True),
    ("GLBA Compliance", "GLBA", 18, "User Access Management", "Log Management policies including roles and responsibilities", False, False, False, False, False),
    ("GLBA Compliance", "GLBA", 19, "User Access Management", "Vulnerability assessment report past 12 months", False, False, False, False, False),
    ("GLBA Compliance", "GLBA", 20, "User Access Management", "SIEM solution evidence and monitoring reports", False, False, False, False, False),
    ("GLBA Compliance", "GLBA", 21, "User Access Management", "Penetration test results past 12 months", False, False, False, False, False),
    ("GLBA Compliance", "GLBA", 22, "Annual compliance review", "Annual GLBA compliance review documentation", True, False, False, True, False),
    # Data Loss Prevention
    ("Data Loss Prevention", "DLP", 23, "Data Loss Prevention strategy", "DLP policy and implementation plan", True, False, False, True, False),
    ("Data Loss Prevention", "DLP", 24, "Data Loss Prevention strategy", "DLP tool configuration documentation", False, False, False, False, False),
    ("Data Loss Prevention", "DLP", 25, "Data Loss Prevention strategy", "DLP incident log past 12 months", False, False, False, False, False),
    ("Data Loss Prevention", "DLP", 26, "Data Loss Prevention strategy", "DLP exception report", False, False, False, False, False),
    ("Data Loss Prevention", "DLP", 27, "Data Loss Prevention strategy", "Data classification policy", False, False, False, False, False),
    ("Data Loss Prevention", "DLP", 28, "Processes for locating and classifying sensitive data", "Data discovery and classification tool evidence", True, False, False, True, False),
    ("Data Loss Prevention", "DLP", 29, "Processes for locating and classifying sensitive data", "Sensitive data inventory", False, False, False, False, False),
    ("Data Loss Prevention", "DLP", 30, "Processes for locating and classifying sensitive data", "Data mapping and flow diagrams", False, False, False, False, False),
    ("Data Loss Prevention", "DLP", 31, "Processes for locating and classifying sensitive data", "Data retention schedule", False, False, False, False, False),
    ("Data Loss Prevention", "DLP", 32, "Firewall and Proxy controls to block uploads", "Firewall ruleset restricting file sharing sites", True, True, False, True, False),
    ("Data Loss Prevention", "DLP", 33, "Firewall and Proxy controls to block uploads", "Proxy filter configuration and block list", False, False, False, False, False),
    ("Data Loss Prevention", "DLP", 34, "Firewall and Proxy controls to block uploads", "Email exfiltration blocking policy evidence", False, False, False, False, False),
    ("Data Loss Prevention", "DLP", 35, "Firewall and Proxy controls to block uploads", "Cloud storage restriction controls", False, False, False, False, False),
    ("Data Loss Prevention", "DLP", 36, "Firewall and Proxy controls to block uploads", "Proxy logs showing blocked transfers", False, False, False, False, False),
    ("Data Loss Prevention", "DLP", 37, "Management of removable media", "Removable media policy and endpoint controls", True, True, False, True, False),
    ("Data Loss Prevention", "DLP", 38, "Management of removable media", "USB/CD/DVD access restriction evidence", False, False, False, False, False),
    ("Data Loss Prevention", "DLP", 39, "Outbound email exfiltration", "Email security gateway configuration (Proofpoint/ForcePoint)", True, True, False, True, False),
    ("Data Loss Prevention", "DLP", 40, "Outbound email exfiltration", "Outbound email filtering logs", False, False, False, False, False),
    ("Data Loss Prevention", "DLP", 41, "Disposal of Media", "Media disposal policy and procedure", True, True, False, True, False),
    ("Data Loss Prevention", "DLP", 42, "Disposal of Media", "Certificate of destruction records", False, False, False, False, False),
    ("Data Loss Prevention", "DLP", 43, "Securing facilities with sensitive information", "Physical access controls to data areas", True, False, True, True, False),
    ("Data Loss Prevention", "DLP", 44, "Securing facilities with sensitive information", "CCTV/access log evidence", False, False, False, False, False),
    ("Data Loss Prevention", "DLP", 45, "Securing facilities with sensitive information", "Clean desk policy compliance evidence", False, False, False, False, False),
    # Patch Management
    ("Patch Management", "PM", 46, "Patch Management Policy", "Patch management policy document", True, False, False, True, False),
    ("Patch Management", "PM", 47, "Patch Management Process", "Patch management procedure and schedule", True, False, False, True, False),
    ("Patch Management", "PM", 48, "Patch Management Process", "Current patch status report for all critical systems", False, False, False, False, False),
    ("Patch Management", "PM", 49, "Patch Management Process", "Emergency/critical patch procedure", False, False, False, False, False),
    ("Patch Management", "PM", 50, "Patch Management Process", "Patch test and rollback procedure", False, False, False, False, False),
    ("Patch Management", "PM", 51, "Uninstalled Patches", "List of uninstalled/deferred patches with risk justification", True, False, False, False, False),
    ("Patch Management", "PM", 52, "Inventory of assets patched", "Asset inventory showing patch levels", True, False, False, False, True),
    ("Patch Management", "PM", 53, "3rd Party Service providers", "Vendor patch management SLA evidence", True, False, False, True, False),
    ("Patch Management", "PM", 54, "Patch Management metrics", "Patch compliance metrics and KPIs", True, False, False, True, False),
    ("Patch Management", "PM", 55, "Patch Management metrics", "Mean time to patch (MTTP) report", False, False, False, False, False),
    # Vendor Management
    ("Vendor Management", "VM", 56, "Vendor Listing", "Complete vendor/third-party inventory", True, False, False, True, False),
    ("Vendor Management", "VM", 57, "Vendor Management Program", "Third-party risk management policy and program", True, False, False, True, False),
    ("Vendor Management", "VM", 58, "Vendor Risk Assessments", "Vendor risk assessment methodology", True, False, False, True, False),
    ("Vendor Management", "VM", 59, "Vendor Risk Assessments", "Completed vendor risk assessments past 12 months", False, False, False, False, False),
    ("Vendor Management", "VM", 60, "Vendor Risk Assessments", "Critical vendor risk tier classification", False, False, False, False, False),
    ("Vendor Management", "VM", 61, "Vendor Exception Report", "Vendor exceptions and risk acceptances", True, False, False, True, False),
    ("Vendor Management", "VM", 62, "Vendor Survey and Review", "Vendor security questionnaire results", True, True, False, False, False),
    ("Vendor Management", "VM", 63, "Vendor Contracts", "Vendor contracts with security requirements/SLAs", True, False, False, True, False),
    ("Vendor Management", "VM", 64, "Vendor Reviews", "Annual vendor review documentation", False, False, False, True, False),
    ("Vendor Management", "VM", 65, "Cloud Vendors", "Cloud vendor security assessments (CSPM evidence)", True, False, False, True, False),
    ("Vendor Management", "VM", 66, "Cloud Vendors", "Cloud shared responsibility matrix", False, False, False, False, False),
    # Network Security
    ("Network Security", "NS", 67, "Network Security Management", "Network security policy and architecture diagram", True, True, False, True, True),
    ("Network Security", "NS", 68, "Network Security Management", "Network segmentation documentation", False, False, False, False, False),
    ("Network Security", "NS", 69, "Network Security Management", "DMZ architecture evidence", False, False, False, False, False),
    ("Network Security", "NS", 70, "Network Security Management", "Network change management records", False, False, False, False, False),
    ("Network Security", "NS", 71, "Network Security Management", "Network monitoring tool evidence", False, False, False, False, False),
    ("Network Security", "NS", 72, "Network Security Management", "Network incident log", False, False, False, False, False),
    ("Network Security", "NS", 73, "Network Internet Protocol addressing", "IP address management scheme and NAT configuration", False, True, False, False, True),
    ("Network Security", "NS", 74, "Managed Firewall", "Firewall policy and ruleset review", True, True, True, True, True),
    ("Network Security", "NS", 75, "Managed Firewall", "Firewall rule change log past 12 months", False, False, False, False, False),
    ("Network Security", "NS", 76, "Change vendor-supplied defaults", "Hardening standard / CIS baseline documentation", False, True, False, True, False),
    ("Network Security", "NS", 77, "Change vendor-supplied defaults", "Device configuration audit results", False, False, False, False, False),
    ("Network Security", "NS", 78, "Anti-Virus Management", "AV/EDR solution evidence and signature update logs", False, True, False, True, True),
    ("Network Security", "NS", 79, "Cryptography", "Encryption policy (data at rest and in transit)", True, True, False, True, False),
    ("Network Security", "NS", 80, "Cryptography", "TLS/SSL certificate inventory", False, False, False, False, False),
    ("Network Security", "NS", 81, "Cryptography", "Key management procedure", False, False, False, False, False),
    ("Network Security", "NS", 82, "Cryptography", "Encryption algorithm standards", False, False, False, False, False),
    ("Network Security", "NS", 83, "IDS/IPS", "IDS/IPS implementation and alert evidence", True, True, True, False, True),
    ("Network Security", "NS", 84, "IDS/IPS", "IDS/IPS tuning and false positive management", False, False, False, False, False),
    ("Network Security", "NS", 85, "IDS/IPS", "IDS/IPS incident response integration", False, False, False, False, False),
    ("Network Security", "NS", 86, "Restrict physical access to network", "Data center physical access controls", True, False, True, True, False),
    ("Network Security", "NS", 87, "Restrict physical access to network", "Server room access log evidence", False, False, False, False, False),
    ("Network Security", "NS", 88, "Restrict physical access to network", "Visitor access management procedure", False, False, False, False, False),
    ("Network Security", "NS", 89, "Remote Access", "VPN/remote access policy and MFA evidence", True, True, False, True, False),
    ("Network Security", "NS", 90, "Remote Access", "Remote access user list and permissions", False, False, False, False, False),
    ("Network Security", "NS", 91, "Wireless Access", "Wireless network security policy (WPA3/enterprise)", True, True, False, True, False),
    ("Network Security", "NS", 92, "Wireless Access", "Guest wireless network segmentation", False, False, False, False, False),
    ("Network Security", "NS", 93, "Wireless Access", "Rogue wireless access point detection", False, False, False, False, False),
    ("Network Security", "NS", 94, "Admin Privileges", "Privileged account management policy (PAM)", True, False, False, True, False),
    ("Network Security", "NS", 95, "Admin Privileges", "Privileged account inventory and review", False, False, False, False, False),
    ("Network Security", "NS", 96, "Active Directory settings", "AD/LDAP configuration and security settings", False, True, False, True, False),
    ("Network Security", "NS", 97, "Authorized Software", "Software whitelist/application control policy", True, False, False, True, False),
    ("Network Security", "NS", 98, "Authorized Software", "Unauthorized software detection evidence", False, False, False, False, False),
    ("Network Security", "NS", 99, "End-of-Life operating systems", "EOL/EOS software inventory and mitigation plan", True, True, False, True, False),
    ("Network Security", "NS", 100, "DDoS", "DDoS protection solution evidence", True, True, False, True, False),
    ("Network Security", "NS", 101, "SIEM and Log Management", "SIEM solution implementation evidence", True, True, False, False, True),
    ("Network Security", "NS", 102, "SIEM and Log Management", "Log retention policy (90 days online / 1 year archive)", False, False, False, False, False),
    ("Network Security", "NS", 103, "SIEM and Log Management", "SIEM alert and use case documentation", False, False, False, False, False),
    ("Network Security", "NS", 104, "Password Management", "Password policy (complexity, length, rotation)", False, True, False, True, False),
    ("Network Security", "NS", 105, "Configuration Standards", "Configuration management standards and baseline", True, True, False, True, False),
    # Information Security Program
    ("Info Security Program", "ISP", 106, "Information Security Governance", "Information security policy (parent policy)", True, False, False, True, False),
    ("Info Security Program", "ISP", 107, "Information Security Governance", "CISO/security leadership organizational chart", False, False, False, False, False),
    ("Info Security Program", "ISP", 108, "Information Security Governance", "Security committee charter and meeting minutes", False, False, False, False, False),
    ("Info Security Program", "ISP", 109, "Information Security Governance", "Security budget and resource allocation", False, False, False, False, False),
    ("Info Security Program", "ISP", 110, "Information Security Governance", "Security roadmap and strategic plan", False, False, False, False, False),
    ("Info Security Program", "ISP", 111, "BoD Reporting", "Board-level security reporting package past 12 months", True, False, False, True, False),
    ("Info Security Program", "ISP", 112, "Security Awareness and Training", "Security training program and completion records", True, False, False, True, False),
    ("Info Security Program", "ISP", 113, "Asset Management", "Asset management policy and procedure", True, False, False, True, False),
    ("Info Security Program", "ISP", 114, "Asset Management", "Hardware asset inventory", False, False, False, False, False),
    ("Info Security Program", "ISP", 115, "Asset Management", "Software asset inventory / CMDB", False, False, False, False, False),
    ("Info Security Program", "ISP", 116, "Asset Management", "Asset classification and labeling standard", False, False, False, False, False),
    ("Info Security Program", "ISP", 117, "Access Control", "Access control policy", True, True, False, True, False),
    ("Info Security Program", "ISP", 118, "Access Control", "User access provisioning/de-provisioning procedure", False, False, False, False, False),
    ("Info Security Program", "ISP", 119, "Access Control", "Quarterly access review evidence", False, False, False, False, False),
    ("Info Security Program", "ISP", 120, "Access Control", "Privileged access management evidence", False, False, False, False, False),
    ("Info Security Program", "ISP", 121, "Access Control", "Terminated user access removal records", False, False, False, False, False),
    ("Info Security Program", "ISP", 122, "Access Control", "Service account inventory and review", False, False, False, False, False),
    ("Info Security Program", "ISP", 123, "Cryptography", "Encryption key management policy", True, True, False, True, False),
    ("Info Security Program", "ISP", 124, "Cryptography", "Data-at-rest encryption evidence", False, False, False, False, False),
    ("Info Security Program", "ISP", 125, "Cryptography", "Data-in-transit encryption (TLS) evidence", False, False, False, False, False),
    ("Info Security Program", "ISP", 126, "Cryptography", "Certificate lifecycle management process", False, False, False, False, False),
    ("Info Security Program", "ISP", 127, "Cybersecurity", "Security operations center (SOC) capability evidence", True, False, False, True, False),
    ("Info Security Program", "ISP", 128, "Third Party interconnectivity", "Third-party interconnection agreements (ISAs)", True, True, False, True, False),
    ("Info Security Program", "ISP", 129, "Third Party interconnectivity", "API security controls evidence", False, False, False, False, False),
    ("Info Security Program", "ISP", 130, "Third Party interconnectivity", "Third-party access monitoring logs", False, False, False, False, False),
    ("Info Security Program", "ISP", 131, "Physical and Environmental Security", "Physical security policy and datacenter controls", True, False, True, True, False),
    ("Info Security Program", "ISP", 132, "Authentication", "Multi-factor authentication (MFA) deployment evidence", True, False, False, True, False),
    ("Info Security Program", "ISP", 133, "Authentication", "MFA coverage report (critical systems)", False, False, False, False, False),
    ("Info Security Program", "ISP", 134, "Authentication", "Biometric/SSO implementation evidence", False, False, False, False, False),
    ("Info Security Program", "ISP", 135, "Information Security Resources", "InfoSec team headcount and org structure", True, False, False, True, False),
    ("Info Security Program", "ISP", 136, "Information Security Resources", "Security certifications held (CISA, CISM, CISSP, etc.)", False, False, False, False, False),
    ("Info Security Program", "ISP", 137, "Information Security Resources", "External security services/MSSP contracts", False, False, False, False, False),
    ("Info Security Program", "ISP", 138, "Information Security Resources", "Security tooling budget allocation", False, False, False, False, False),
    # Incident Response
    ("Incident Response", "IR", 139, "Incident Response Plan", "Incident response plan document", True, False, False, True, False),
    ("Incident Response", "IR", 140, "Incident Response Training", "IR team training records and tabletop exercise results", True, False, False, True, False),
    ("Incident Response", "IR", 141, "Incident Response Testing", "IR plan test evidence (tabletop/simulation) past 12 months", True, False, False, True, False),
    ("Incident Response", "IR", 142, "Incident Response Handling", "Active incident tracking system evidence", True, True, False, False, True),
    ("Incident Response", "IR", 143, "Incident Response Handling", "Incident classification and severity matrix", False, False, False, False, False),
    ("Incident Response", "IR", 144, "Incident Response Monitoring", "24/7 monitoring capability evidence", True, False, False, True, False),
    ("Incident Response", "IR", 145, "Incident Response Reporting", "Regulatory breach notification procedure (72-hour)", True, False, False, True, False),
    ("Incident Response", "IR", 146, "Incident Response Reporting", "Post-incident review reports past 12 months", False, False, False, False, False),
]


class GRCITAuditProgram(Document):
    def validate(self):
        self._calculate_stats()

    def _calculate_stats(self):
        items = self.control_items or []
        total = len(items)
        delivered = sum(1 for i in items if i.delivery_status == "Delivered")
        na = sum(1 for i in items if i.delivery_status == "Not Applicable")
        effective_total = total - na
        self.total_controls = total
        self.artifacts_requested = total
        self.artifacts_delivered = delivered
        self.delivery_pct = round((delivered / effective_total * 100) if effective_total > 0 else 0, 1)

    @frappe.whitelist()
    def seed_controls_from_library(self, domains=None):
        """Populate control items from the standard 146-control library."""
        if not self.has_permission("write"):
            frappe.throw("You are not permitted to modify this Audit Programme.",
                         frappe.PermissionError)
        scope_map = {
            "GLBA Compliance": self.in_scope_glba,
            "Data Loss Prevention": self.in_scope_dlp,
            "Patch Management": self.in_scope_patch,
            "Vendor Management": self.in_scope_vendor,
            "Network Security": self.in_scope_network,
            "Info Security Program": self.in_scope_isp,
            "Incident Response": self.in_scope_ir,
        }
        self.control_items = []
        for ctrl in IT_CONTROLS_LIBRARY:
            domain, code, item_num, name, artifacts, is_mgmt, is_tech, is_phys, is_prev, is_det = ctrl
            if not scope_map.get(domain, True):
                continue
            self.append("control_items", {
                "domain": domain,
                "domain_code": code,
                "item_number": item_num,
                "control_name": name,
                "requested_artifacts": artifacts,
                "delivery_status": "Not Started",
                "control_type_mgmt": 1 if is_mgmt else 0,
                "control_type_tech": 1 if is_tech else 0,
                "control_type_phys": 1 if is_phys else 0,
                "timing_preventive": 1 if is_prev else 0,
                "timing_detective": 1 if is_det else 0,
            })
        self._calculate_stats()
        self.save()
        return {"controls_added": len(self.control_items)}
