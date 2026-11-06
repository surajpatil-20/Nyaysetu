"""
Utility functions for NYAYASETU authentication and OTP handling.
"""
from datetime import datetime


def print_otp_terminal(email: str, otp_code: str, expires_at: datetime = None) -> None:
    """
    Print the generated OTP clearly to the Django backend terminal for local dev/testing.
    Never exposes passwords.
    """
    exp_info = expires_at.strftime('%Y-%m-%d %H:%M:%S UTC') if expires_at else '5 minutes'
    banner = "=" * 54
    print(f"\n{banner}", flush=True)
    print("  [NYAYASETU EMAIL OTP VERIFICATION]", flush=True)
    print(f"  Email: {email}", flush=True)
    print(f"  OTP Code: {otp_code}", flush=True)
    print(f"  Valid for: 5 Minutes (Expires at: {exp_info})", flush=True)
    print(f"{banner}\n", flush=True)

