{
    "use_network": {
        "type": "bool",
        "required": true,
        "default": false,
        "comment": "Toggle Convection Secrets Manager connection over socket or network"
    },
    "tls_ca": {
        "type": "str",
        "required": true,
        "default": "",
        "comment": "TLS CA Cert for Connection"
    },
    "socket_path": {
        "type": "file",
        "required": true,
        "default": "/var/run/convection.secrets.sock",
        "comment": "Socket filename for IPC communication"
    },
    "network": {
        "type": "dict",
        "required": true,
        "default": {},
        "comment": "Convection Secrets Manager Network Configuration",
        "spec_chain": "global.secrets.client.network"
    },
    "log_file": {
        "type": "file",
        "required": true,
        "default": "./convection-secrets.client.log",
        "comment": "Log File Path"
    }
}