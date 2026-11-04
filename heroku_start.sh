#!/usr/bin/env bash
set -euo pipefail

 echo "[startup] Heroku worker startup script entered."

required_vars=(
  OCI_USER
  OCI_TENANCY
  OCI_FINGERPRINT
  OCI_REGION
  OCI_API_PRIVATE_KEY
  OCI_SUBNET_ID
  OCI_SSH_PUBLIC_KEY
)

for var_name in "${required_vars[@]}"; do
  if [[ -z "${!var_name:-}" ]]; then
    echo "Missing required Heroku config var: $var_name" >&2
    exit 1
  fi
done

umask 077
echo "[startup] Required config vars are present; writing OCI config files."
printf '%s\n' "$OCI_API_PRIVATE_KEY" > "$PWD/oci_api_key.pem"
printf '%s\n' "$OCI_SSH_PUBLIC_KEY" > "$PWD/id_rsa.pub"

cat > "$PWD/oci_config" <<EOF
[DEFAULT]
user=$OCI_USER
fingerprint=$OCI_FINGERPRINT
tenancy=$OCI_TENANCY
region=$OCI_REGION
key_file=$PWD/oci_api_key.pem
EOF

if [[ -n "${EMAIL_FROM:-}" && -n "${EMAIL_TO:-}" && -n "${EMAIL_PASSWORD:-}" ]]; then
  NOTIFY_EMAIL=True
else
  NOTIFY_EMAIL=False
fi

cat > "$PWD/oci.env" <<EOF
OCI_CONFIG=$PWD/oci_config
OCT_FREE_AD=AD-1
DISPLAY_NAME=mohit
OCI_COMPUTE_SHAPE=VM.Standard.A1.Flex
SECOND_MICRO_INSTANCE=False
REQUEST_WAIT_TIME_SECS=120
SSH_AUTHORIZED_KEYS_FILE=$PWD/id_rsa.pub
OCI_SUBNET_ID=$OCI_SUBNET_ID
OCI_IMAGE_ID=
OPERATING_SYSTEM="Canonical Ubuntu"
OS_VERSION=22.04
ASSIGN_PUBLIC_IP=true
BOOT_VOLUME_SIZE=50
NOTIFY_EMAIL=$NOTIFY_EMAIL
EMAIL_FROM=${EMAIL_FROM:-}
EMAIL_TO=${EMAIL_TO:-}
EMAIL_PASSWORD=${EMAIL_PASSWORD:-}
EOF

echo "[startup] Config files prepared. Starting Python worker."
exec python -u heroku_worker.py
