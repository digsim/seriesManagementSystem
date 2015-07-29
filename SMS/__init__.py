import sys
from serieManagementSystem import SMS

def main():
    """Entry point for the application script"""
    sms = SMS()
    sms.getArguments(sys.argv[1:])