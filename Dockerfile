FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app user (non-root for security)
RUN useradd -m -u 1000 appuser
USER appuser
WORKDIR /home/appuser

# Install optics-toolbox
RUN pip install --user git+https://github.com/MichaelAkridge-NOAA/optics-toolbox.git

# Add user's pip bin to PATH
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Create data directories
RUN mkdir -p /home/appuser/data/downloads /home/appuser/data/credentials

# Expose Streamlit port
EXPOSE 8501

# Set Streamlit configuration
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Default command - run web interface
CMD ["gcs-browser-web"]
