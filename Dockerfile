FROM debian
RUN apt update >/dev/null 
RUN apt install -y pipx  >/dev/null 
RUN yes | adduser --quiet test
USER test
COPY --chown=test api /home/test/api
RUN mkdir -p /home/test/.local/bin
RUN sh -l -c "pipx ensurepath ; pipx install /home/test/api"
CMD  sh -l -c "temp_api" 

