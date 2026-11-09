#!/bin/bash
# Post-deploy smoke test for the local-gateway integration
# (docker-compose.gateway.yml). Run after any `docker compose ... up -d`
# that rebuilds/recreates theta-lab-web, to catch the gateway losing its
# route to this container (502s on every path) before finding out from a
# blank/stuck dashboard tab - see the 2026-11-04 incident documented in
# docker-compose.gateway.yml.
set -e

BASE="http://localhost:9000/theta-lab"
PATHS=("/" "/today" "/us" "/india" "/api/us/position-heat")

fail=0
for p in "${PATHS[@]}"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE$p")
  if [ "$code" = "200" ]; then
    echo "OK   $BASE$p -> $code"
  else
    echo "FAIL $BASE$p -> $code"
    fail=1
  fi
done

if [ "$fail" -ne 0 ]; then
  echo ""
  echo "Gateway smoke test FAILED. Likely cause: theta-lab-web was recreated"
  echo "without the docker-compose.gateway.yml overlay. Re-deploy with:"
  echo "  docker compose -f docker-compose.yml -f docker-compose.gateway.yml up -d --build"
  exit 1
fi

echo ""
echo "Gateway smoke test passed."
