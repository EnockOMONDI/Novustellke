#!/usr/bin/env python
"""
Simple test to verify Mailtrap import works
"""

import sys
print("Python path:")
for path in sys.path:
    print(f"  {path}")

print("\nTrying to import pydantic...")
try:
    import pydantic
    print(f"✅ Pydantic version: {pydantic.VERSION}")
    print(f"✅ Pydantic location: {pydantic.__file__}")
except Exception as e:
    print(f"❌ Pydantic import failed: {e}")

print("\nTrying to import TypeAdapter from pydantic...")
try:
    from pydantic import TypeAdapter
    print("✅ TypeAdapter imported successfully")
except Exception as e:
    print(f"❌ TypeAdapter import failed: {e}")

print("\nTrying to import mailtrap...")
try:
    from mailtrap import Mail, Address, MailtrapClient
    print("✅ Mailtrap imported successfully")
    print(f"✅ MailtrapClient: {MailtrapClient}")
except Exception as e:
    print(f"❌ Mailtrap import failed: {e}")
