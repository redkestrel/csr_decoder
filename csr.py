# -*- coding: utf-8 -*-
"""Provides a class to decode a PKCS#10

This module provides a class that takes a PKCS#10 in either DER or PEM format.
It provides methods to inspect the attributes of the PKCS#10 object.
"""

import re
import OpenSSL

__author__ = 'Phil Ratcliffe'
__copyright__ = 'Copyright 2018, Phil Ratcliffe'


PEM_DNS_SANS = re.compile(r"(DNS:.*?)$", re.MULTILINE)


class CSR(object):
    """Decodes PKCS#10 Certificate Signing Requests"""

    def __init__(self, x509):
        # The OpenSSL X509Req object
        self._x509 = x509

        # The Subject of the CSR represented as a DN
        self._subject = None

        # The CommonName RDN of the Subject DN
        self._cn = None

        # The OpenSSL text representation of the CSR
        self._openssl_text = None

    @classmethod
    def from_pem(cls, pem_csr):
        """Initialise from a PEM encoded CSR."""

        x509 = OpenSSL.crypto.load_certificate_request(
            OpenSSL.crypto.FILETYPE_PEM, pem_csr)
        return cls(x509)

    @classmethod
    def from_binary(cls, binary_csr):
        """Initialise from a binary CSR."""

        x509 = OpenSSL.crypto.load_certificate_request(
            OpenSSL.crypto.FILETYPE_ASN1, binary_csr)
        return cls(x509)

    def __str__(self):
        return self.openssl_text

    def get_pubkey_alg(self):
        """Get the public key's algorithm"""

        pk = self._x509.get_pubkey()
        type = pk.type()

        # OpenSSL does not yet have a type for EC, so google certs, for
        # example, will have alg type of UNKNOWN.
        types = {
            OpenSSL.crypto.TYPE_RSA: "RSA",
            OpenSSL.crypto.TYPE_DSA: "DSA",
        }
        return types.get(type, "UNKNOWN")

    @property
    def cn(self):
        """Returns the CN from the subject if present"""

        if self._cn is None:
            for rdn in self.subject:
                if rdn[0] == b"CN":
                    self._cn = rdn[1]
                    break
        return self._cn

    @property
    def subject(self):
        """Returns the subject of the CSR"""

        if self._subject is None:
            self._subject = self._x509.get_subject().get_components()
        return self._subject

    @property
    def openssl_text(self):
        """Returns the OpenSSL output for the CSR"""

        if self._openssl_text is None:
            self._openssl_text = OpenSSL.crypto.dump_certificate_request(
                OpenSSL.crypto.FILETYPE_TEXT,
                self._x509)
        return self._openssl_text
