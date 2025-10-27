"""Accounts app models.

This file intentionally does not define a Profile model to avoid clashing with
the canonical Profile implementation in the `profiles` app. Import the
Profile where needed from `profiles.models`.
"""

from profiles.models import Profile  # re-export for import compatibility