"""
😈 DAEMON Module - The Core Vertical Slice

This is the ONLY module in DAEMON-ONE template.
Additional modules should be copied from DAEMON-ABYSS when needed.

Contains:
- Abstract base models (timestamps, soft delete)
- Domain events (Django Signals)
- Module configuration pattern
- Global templates and static files

Usage:
    from domains.daemon.interface import (
        TimestampedModel,
        SoftDeleteModel,
        domain_event,
        ModuleSettings,
    )
"""
