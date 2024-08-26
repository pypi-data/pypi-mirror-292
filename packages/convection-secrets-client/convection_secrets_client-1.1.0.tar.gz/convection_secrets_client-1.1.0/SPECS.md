# Configuration Options

- [Configuration Options](#configuration-options)
  - [Spec for secrets-console](#spec-for-secrets-console)
  - [Spec for secrets-console.global](#spec-for-secrets-consoleglobal)
  - [Spec for secrets-console.global.secrets](#spec-for-secrets-consoleglobalsecrets)
  - [Spec for secrets-console.global.secrets.client](#spec-for-secrets-consoleglobalsecretsclient)

Auto generated from .spec files
## Spec for secrets-console

Option: `global` - 
 - Type: dict
 - Required: True
 - Default: {}
 - Additionally Validates With: `secrets-console.global`

## Spec for secrets-console.global

Option: `reporting` - Reporting and Logging configuration
 - Type: dict
 - Required: True
 - Default: {}
 - Additionally Validates With: `global.reporting`

Option: `secrets` - Secrets Configuration
 - Type: dict
 - Required: True
 - Default: {}
 - Additionally Validates With: `secrets-console.global.secrets`
 - 
## Spec for secrets-console.global.secrets

Option: `client` - Secrets Client Configuration
 - Type: dict
 - Required: True
 - Default: {}
 - Additionally Validates With: `secrets-console.global.secrets.client`


## Spec for secrets-console.global.secrets.client

Option: `use_network` - Toggle Convection Secrets Manager connection over socket or network
 - Type: bool
 - Required: True
 - Default: False

Option: `tls_ca` - TLS CA Cert for Connection
 - Type: file:exist
 - Required: True
 - Default: ./config/ca.pem

Option: `socket_path` - Socket filename for IPC communication
 - Type: file
 - Required: True
 - Default: /var/run/convection.secrets.sock

Option: `network` - Convection Secrets Manager Network Configuration
 - Type: dict
 - Required: True
 - Default: {}
 - Additionally Validates With: `global.secrets.client.network`

Option: `log_file` - Log File Path
 - Type: file
 - Required: True
 - Default: ./convection-secrets.client.log
