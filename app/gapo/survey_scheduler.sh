# Script to send survey every 2 minutes
while true; do
  curl http://localhost:8502/gapo/send_survey
  sleep 120  # Sleep for 2 minutes
done