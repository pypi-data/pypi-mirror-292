"""
Exceptions sub-module of the Jacobi Library.
"""
from __future__ import annotations
__all__ = ['JacobiLicenseError', 'JacobiLoadProjectError']
class JacobiLicenseError(Exception):
    pass
class JacobiLoadProjectError(Exception):
    pass
