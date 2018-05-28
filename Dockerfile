FROM alpine:3.7

RUN apk add --no-cache openssh-client

RUN apk add --no-cache vsftpd

RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache

RUN echo apk --no-cache upgrade &&\
	apk --no-cache add rethinkdb su-exec &&\
	mkdir /data &&\
	chown daemon:daemon /data 

RUN echo "echo Host *" >> /etc/ssh/ssh_config &&\
    echo "    StrictHostKeyChecking no" >> /etc/ssh/ssh_config

RUN adduser -h /home/./files -s /bin/false -D files
RUN echo "local_enable=YES" >> /etc/vsftpd/vsftpd.conf &&\
    echo "chroot_local_user=YES" >> /etc/vsftpd/vsftpd.conf &&\
    echo "write_enable=YES" >> /etc/vsftpd/vsftpd.conf &&\
    echo "local_umask=022" >> /etc/vsftpd/vsftpd.conf &&\
    echo "passwd_chroot_enable=yes" >> /etc/vsftpd/vsftpd.conf &&\
    echo 'seccomp_sandbox=NO' >> /etc/vsftpd/vsftpd.conf &&\
    echo 'pasv_enable=Yes' >> /etc/vsftpd/vsftpd.conf &&\
    echo 'pasv_max_port=10100' >> /etc/vsftpd/vsftpd.conf &&\
    echo 'pasv_min_port=10090' >> /etc/vsftpd/vsftpd.conf &&\
    sed -i "s/anonymous_enable=YES/anonymous_enable=NO/" /etc/vsftpd/vsftpd.conf

RUN pip install flask rethinkdb requests

VOLUME /home/files
