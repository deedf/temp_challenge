FROM debian
# Should probably use alpine instead

RUN apt update >/dev/null 
RUN apt install -y pipx  >/dev/null 
RUN yes | adduser --quiet test
USER test
COPY --chown=test . /home/test/temp_api
RUN mkdir -p /home/test/.local/bin
RUN sh -l -c "pipx ensurepath --force; pipx install /home/test/temp_api"
RUN rm -rf /home/test/temp_api
CMD  sh -l -c "temp_api" 

