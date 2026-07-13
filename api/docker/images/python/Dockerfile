FROM python:3.11-slim

# Create non-root sandbox user
RUN addgroup --system --gid 1001 sandbox \
    && adduser --system --uid 1001 --ingroup sandbox --disabled-password --no-create-home sandbox

# No Python packages needed — all execution is stdlib-only
USER sandbox
WORKDIR /home/sandbox

# Verify nothing runs as root
RUN python3 -c "import os; assert os.geteuid() != 0, 'Must not run as root'"