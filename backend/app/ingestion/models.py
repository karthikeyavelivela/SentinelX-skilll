from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, Index
from app.database import Base


class CVE(Base):
    __tablename__ = "cves"

    id = Column(Integer, primary_key=True, index=True)
    cve_id = Column(String(20), unique=True, index=True, nullable=False)  # CVE-2024-XXXX
    description = Column(Text)
    published_date = Column(DateTime)
    last_modified_date = Column(DateTime)

    # CVSS
    cvss_v3_score = Column(Float, default=0.0)
    cvss_v3_vector = Column(String(255))
    cvss_v3_severity = Column(String(20))
    attack_vector = Column(String(50))
    attack_complexity = Column(String(20))
    privileges_required = Column(String(20))
    user_interaction = Column(String(20))
    scope = Column(String(20))

    # CPE
    affected_cpes = Column(JSON, default=[])
    vendor = Column(String(255), index=True)
    product = Column(String(255), index=True)

    # Enrichment
    epss_score = Column(Float, default=0.0)
    epss_percentile = Column(Float, default=0.0)
    is_kev = Column(Boolean, default=False)
    kev_date_added = Column(DateTime, nullable=True)
    has_public_exploit = Column(Boolean, default=False)
    exploit_maturity = Column(String(50), default="none")
    references = Column(JSON, default=[])

    # ML prediction
    predicted_exploit_probability = Column(Float, default=0.0)
    prediction_confidence = Column(Float, default=0.0)

    # Metadata
    ingested_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_cve_severity", "cvss_v3_severity"),
        Index("ix_cve_epss", "epss_score"),
    )


class Exploit(Base):
    __tablename__ = "exploits"

    id = Column(Integer, primary_key=True, index=True)
    cve_id = Column(String(20), index=True)
    source = Column(String(50))  # exploitdb, github, metasploit
    source_url = Column(Text)
    title = Column(Text)
    description = Column(Text)
    exploit_type = Column(String(50))  # remote, local, webapps, dos
    platform = Column(String(100))
    verified = Column(Boolean, default=False)
    published_date = Column(DateTime)
    maturity = Column(String(50), default="poc")  # poc, weaponized, functional
    ingested_at = Column(DateTime, default=datetime.utcnow)


class KEVEntry(Base):
    __tablename__ = "kev_entries"

    id = Column(Integer, primary_key=True, index=True)
    cve_id = Column(String(20), unique=True, index=True, nullable=False)
    vendor_project = Column(String(255))
    product = Column(String(255))
    vulnerability_name = Column(Text)
    date_added = Column(DateTime)
    short_description = Column(Text)
    required_action = Column(Text)
    due_date = Column(DateTime)
    known_ransomware_use = Column(String(20))
    notes = Column(Text)
    ingested_at = Column(DateTime, default=datetime.utcnow)


class EPSSScore(Base):
    __tablename__ = "epss_scores"

    id = Column(Integer, primary_key=True, index=True)
    cve_id = Column(String(20), index=True, nullable=False)
    epss_score = Column(Float, nullable=False)
    percentile = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    ingested_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_epss_cve_date", "cve_id", "date", unique=True),
    )
