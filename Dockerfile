FROM python:3.10-alpine

# TODO: Decide whether to run as non-root user or not
# https://medium.com/@DahlitzF/run-python-applications-as-non-root-user-in-docker-containers-by-example-cba46a0ff384

# Install the automx2 package, the application server gunicorn and the template engine Jinja2
# https://rseichter.github.io/automx2/#install
RUN pip install automx2 gunicorn Jinja2

# Copy custom files
COPY automx2.template.conf /etc/
COPY start.py /
COPY check.py /

# Start the container with a custom start script
CMD ["/start.py"]
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s CMD /check.py