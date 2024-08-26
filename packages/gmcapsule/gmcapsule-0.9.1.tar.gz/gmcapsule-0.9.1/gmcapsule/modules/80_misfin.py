# Copyright (c) 2024 Jaakko Keränen <jaakko.keranen@iki.fi>
# License: BSD-2-Clause

"""Misfin Email Bridge"""

import gmcapsule
import hashlib
import re
import subprocess
from pathlib import Path
from OpenSSL import SSL, crypto


def get_fingerprint(x509_cert):
    h = hashlib.sha256()
    h.update(crypto.dump_certificate(crypto.FILETYPE_ASN1, x509_cert))
    return h.hexdigest()


def parse_identity(cert) -> tuple:
    """Returns: (mailbox, host, blurb)"""
    host = None

    comps = {}
    for (comp, value) in cert.get_subject().get_components():
        comps[comp.decode('utf-8')] = value.decode('utf-8')
    i = 0
    while i < cert.get_extension_count():
        ext = cert.get_extension(i)
        if ext.get_short_name() == b'subjectAltName':
            host = str(ext)
            if not host.startswith('DNS:'):
                raise Exception(f"{cert}: subject alternative name must specify a DNS hostname")
            host = host[4:]
            break
        i += 1
    if not host:
        raise Exception(f"{cert}: subject alternative name not specified")

    return (comps['UID'], host, comps['CN'])



class MisfinError (Exception):
    def __init__(self, status, meta):
        self.status = status
        self.meta = meta

    def __str__(self):
        return f'{self.status} {self.meta}'


class Recipient:
    # Note: Generating a recipient certificate:
    # openssl req -x509 -key misfin.key -outform PEM -out misfin.pem -sha256 -days 100000 -addext 'subjectAltName=DNS:example.com' -subj '/CN=blurb/UID=mailbox'

    def __init__(self, name, cert, key, email):
        self.name = name
        self.email = email

        if not cert:
            raise Exception(self.name + ': recipient certificate not specified')
        if not key:
            raise Exception(self.name + ': recipient private key not specified')

        self.cert = crypto.load_certificate(crypto.FILETYPE_PEM, open(cert, 'rb').read())
        self.key = crypto.load_privatekey(crypto.FILETYPE_PEM, open(key, 'rb').read())

        if not self.cert:
            raise Exception(cert + ": invalid certificate")
        if not self.key:
            raise Exception(key + ": invalid private key")

        self.fingerprint = get_fingerprint(self.cert)

        crt_uid, crt_host, crt_blurb = parse_identity(self.cert)
        if crt_uid != self.name:
            raise Exception(f"{cert}: certificate user ID must match mailbox name ({name})")
        self.host = crt_host
        self.blurb = crt_blurb


class MisfinHandler:
    def __init__(self, context):
        cfg = context.config().section('misfin')

        self.context = context
        self.email_cmd = cfg.get('email.cmd', fallback='/usr/sbin/sendmail')
        self.email_from = cfg.get('email.from', fallback=None)
        self.trust_file = Path.home() / '.misfin-known-senders'
        self.reject = cfg.get('reject', fallback='').split()
        self.always_trust = set()
        self.recipients = {}

        # Configure.
        cfg = context.config()
        for section in cfg.prefixed_sections('misfin.').values():
            name = section.name[7:]
            cert = section.get('cert', fallback=None)
            key = section.get('key', fallback=None)
            email = section.get('email', fallback=None)
            if not email:
                raise Exception("Misfin recipients must have an email forwarding address")
            recp = Recipient(name, cert, key, email)
            self.always_trust.add(recp.fingerprint)
            self.recipients[name] = recp

    def check_sender(self, identity):
        if not identity:
            raise MisfinError(60, 'Certificate required')

        fp = identity.fp_cert
        uid, host, blurb = parse_identity(crypto.load_certificate(crypto.FILETYPE_ASN1,
                                                                  identity.cert))
        addr = uid + '@' + host

        if fp in self.always_trust:
            return True
        if fp in self.reject:
            return False

        if re.search(r'\s', uid):
            raise MisfinError(62, 'Invalid sender mailbox')
        if re.search(r'\s', host):
            raise MisfinError(62, 'Invalid sender hostname')

        try:
            for line in open(self.trust_file, 'rt').readlines():
                m = re.match(r'([0-9a-f]{64}) ([^\s]+) .*', line)
                if m:
                    if m[1] == fp:
                        return True
                    if m[2] == addr:
                        if m[1] != fp:
                            raise MisfinError(63, 'Certificate does not match known identity')
                        return True
        except FileNotFoundError:
            pass

        # Never seen this before, TOFU it.
        print(f"{fp} {addr} {blurb}", file=open(self.trust_file, 'at'))

        return True

    def __call__(self, request_data):
        resp_status = 20
        resp_meta = ''

        sender = request_data.identity
        request = request_data.request

        try:
            # If we've seen this before, check that the fingerprint is the same.
            if not self.check_sender(sender):
                raise MisfinError(61, 'Unauthorized sender')

            # Parse the request.
            version = 'B'
            m = re.match(r'misfin://([^@]+)@([^@\s]+) (.*)', request, re.DOTALL)
            if m:
                message = m[3]
            else:
                m = re.match(r'misfin://([^@]+)@([^@\s]+)\t(\d+)', request)
                if not m:
                    raise MisfinError(59, "Bad request")
                if not request_data.receive_data(int(m[3])):
                    raise MisfinError(59, 'Invalid content length')
                version = 'C'
                message = request_data.buffered_data.decode('utf-8')

            mailbox = m[1]
            host    = m[2]

            if mailbox not in self.recipients:
                raise MisfinError(51, 'Mailbox not found')

            recp = self.recipients[mailbox]

            if host != recp.host:
                raise MisfinError(53, 'Domain not serviced')

            resp_meta = recp.fingerprint

            if len(message) > 0:
                # Forward as email.
                try:
                    uid, host, blurb = parse_identity(crypto.load_certificate(crypto.FILETYPE_ASN1,
                                                                              sender.cert))
                    subject = f"[misfin] Message from {uid}@{host}"

                    msg = f'From: {self.email_from}\n' + \
                        f'To: {recp.email}\n' + \
                        f'Subject: {subject}\n\n' + \
                        message.rstrip() + "\n\n" + \
                            f"=> misfin://{uid}@{host} {blurb}\n"

                    args = [self.email_cmd, '-i', recp.email]
                    if self.email_cmd == 'stdout':
                        print(args, msg)
                    else:
                        subprocess.check_output(args, input=msg, encoding='utf-8')
                except Exception as x:
                    print('Error sending email:', x)
                    raise MisfinError(42, 'Internal error')

        except MisfinError as er:
            resp_status = er.status
            resp_meta = er.meta

        return f'{resp_status} {resp_meta}\r\n'.encode('utf-8')


def init(context):
    if context.config().prefixed_sections('misfin.').values():
        context.add_protocol('misfin', MisfinHandler(context))
