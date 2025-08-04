# app/models/enums.py
"""
Defines enumerated types used across various models to ensure data consistency
for fields with a predefined set of values.
"""

import enum

class ParentRole(enum.Enum):
    """Enumeration for the role of a parent dog (Sire or Dam)."""
    DAD = "Dad"
    MOM = "Mom"

class PuppyStatus(enum.Enum):
    """Enumeration for the availability status of a puppy."""
    AVAILABLE = "Available"
    RESERVED = "Reserved"
    SOLD = "Sold"