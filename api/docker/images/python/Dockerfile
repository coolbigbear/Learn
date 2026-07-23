FROM python:3.11-slim

# Create non-root sandbox user
RUN addgroup --system --gid 1001 sandbox \
    && adduser --system --uid 1001 --ingroup sandbox --disabled-password --no-create-home sandbox

# Install packages for exercises: ML libs (lessons 18+) and API libs (lessons 19-20, 26)
RUN pip install --no-cache-dir numpy pandas scikit-learn fastapi pydantic uvicorn sqlalchemy[asyncio] aiosqlite passlib[bcrypt] python-jose[cryptography] httpx

USER sandbox
WORKDIR /home/sandbox

# Verify nothing runs as root
RUN python3 -c "import os; assert os.geteuid() != 0, 'Must not run as root'"
