from fpdf import FPDF
import os

# Content for the Expanded Project Nova Brief
content = """
Project Nova: Internal Strategy & Execution Brief
Document ID: P-NOV-2025-01
Date: July 15, 2025
Author: Dr. Evelyn Reed, Managing Director

---

1. Executive Summary
Project Nova is a strategic initiative to build a state-of-the-art, client-facing analytics dashboard. The primary goal is to provide our customers with real-time data visualization and actionable insights. This platform will replace the legacy 'AlphaView' system.
Approved by: Eleanor Vance (CEO)

2. Project Timeline
- Start Date: August 1, 2025
- Phase 1 (Architecture & Design): August 1 - August 30, 2025
- Phase 2 (Backend Development - 'Orion'): September 1 - September 30, 2025
- Phase 3 (Frontend Development - 'Lyra'): October 1 - October 31, 2025
- Phase 4 (UAT & Deployment): November 15, 2025
- Go-Live Target: December 1, 2025
- Phase 5 (Mobile App & Scaling): January 5, 2026 (New!)

3. Key Team Members & Roles
- Project Lead: Dr. Evelyn Reed
- Backend Lead (Orion): David Chen
- Frontend Lead (Lyra): Pending
- Chief Designer: Sarah Jenkins (New!)
- DevOps Engineer: Marcus Thorne
- HR Manager: Sarah Miller

4. Technology Stack
- Backend (Orion): Python, FastAPI, PostgreSQL.
- Frontend (Lyra): React, TypeScript, TailwindCSS.
- Infrastructure: AWS (Lambda, RDS, S3).

5. Budget & Resources (Confidential) (New Section)
The total approved budget for Project Nova is $1.2 Million.
- Development: $800,000
- Infrastructure (Year 1): $150,000
- Design & Marketing: $150,000
- Contingency: $100,000

6. Risk Management (New Section)
- Risk: Scalability during peak traffic.
- Mitigation: Auto-scaling groups implemented by Marcus Thorne.
- Risk: Third-party API rate limits.
- Mitigation: Caching layer in Redis.

7. Future Roadmap (2026)
- Q1 2026: Launch Android and iOS mobile applications (Project 'Nebula').
- Q2 2026: AI-driven predictive analytics module.
- Q3 2026: Expansion into European markets (GDPR compliance focus).

8. Security & Data Privacy (New Section)
- Encryption: All data at rest must be encrypted using AES-256.
- Authentication: Multi-Factor Authentication (MFA) is mandatory for all admin access.
- Audit Logs: Logs must be retained for 7 years to meet financial regulations.
- Compliance: System must be SOC2 Type II compliant by launch.

9. External Vendors & Partners
- Cloud Provider: AWS (Managed by DevOps Team).
- UI/UX Design Agency: 'PixelPerfect Studios' (Consultant contract: $50,000).
- Security Auditing Firm: 'CyberGuard Solutions' (Audit scheduled for Nov 10).

10. Internal Communication Plan
- Daily Standup: 9:30 AM EST (Zoom Link #8842).
- Bi-weekly Sprint Review: Fridays at 3:00 PM EST.
- Documentation Hub: Confluence Space 'Project Nova'.
- Emergency Contact: Marcus Thorne (DevOps) - Ext 4492.
"""

def create_pdf(filename="project_nova_brief.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Project Nova Internal Brief", ln=True, align='C')
    
    pdf.set_font("Arial", size=12)
    # Write content line by line
    for line in content.strip().split('\n'):
        try:
            # Handle unicode characters if any (fpdf 1.7 is limited, but basic text is fine)
            safe_line = line.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 8, txt=safe_line)
        except Exception as e:
            print(f"Skipping line: {e}")

    pdf.output(filename)
    print(f"✅ Generated {filename} with expanded content!")

if __name__ == "__main__":
    create_pdf()
