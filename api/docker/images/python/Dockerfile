FROM python:3.11-slim

# Create non-root sandbox user
RUN addgroup --system --gid 1001 sandbox \
    && adduser --system --uid 1001 --ingroup sandbox --disabled-password --no-create-home sandbox

# Install xmltodict for XML exercises (not in stdlib)
RUN pip install --no-cache-dir xmltodict

USER sandbox
WORKDIR /home/sandbox

# Verify nothing runs as root
RUN python3 -c "import os; assert os.geteuid() != 0, 'Must not run as root'"