# generated by datamodel-codegen:
#   filename:  entity/services/connections/messaging/saslMechanismType.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from enum import Enum


class SaslMechanismType(Enum):
    PLAIN = 'PLAIN'
    GSSAPI = 'GSSAPI'
    SCRAM_SHA_256 = 'SCRAM-SHA-256'
    SCRAM_SHA_512 = 'SCRAM-SHA-512'
    OAUTHBEARER = 'OAUTHBEARER'
