import enum

# Enum for Parent roles to ensure data consistency
class ParentRole(enum.Enum):
    DAD = "Dad"
    MOM = "Mom"

# Enum for Puppy status
class PuppyStatus(enum.Enum):
    AVAILABLE = "Available"
    RESERVED = "Reserved"
    SOLD = "Sold"