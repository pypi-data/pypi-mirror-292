# forked from https://github.com/WebOfTrustInfo/ld-signatures-python

import base64
import json

from Crypto.Hash import SHA256
from collections.abc import MutableMapping
from copy import deepcopy
from pyld import jsonld
from typing import TYPE_CHECKING, Any

from .misc import MessageDate

if TYPE_CHECKING:
	from .algorithms import HS2019


def b64safe_encode(payload: bytes) -> bytes:
	return base64.urlsafe_b64encode(payload).rstrip(b"=")


def b64safe_decode(payload: bytes) -> bytes:
	return base64.urlsafe_b64decode(payload + b"=" * (4 - len(payload) % 4))


def normalize_json(payload: MutableMapping[str, Any]) -> bytes:
	return json.dumps(
		payload,
		separators = (",", ":"),
		sort_keys = True
	).encode("utf-8")


def normalize_jsonld(jld_document: MutableMapping[str, Any]) -> bytes:
	options = {"algorithm": "URDNA2015", "format": "application/nquads"}
	normalized = jsonld.normalize(jld_document, options=options)
	return SHA256.new(normalized.encode("utf-8")).digest()


def sign(message: MutableMapping[str, Any], algo: HS2019) -> MutableMapping[str, Any]:
	new_doc = deepcopy(message)
	header = {"alg": "RS256", "b64": False, "crit": ["b64"]}
	encoded_header = b64safe_encode(normalize_json(header))
	prepared_payload = b".".join([encoded_header, normalize_jsonld(new_doc)])
	sigdata = algo.sign_data(algo.hash_data(prepared_payload))

	new_doc.update({
		"signature": {
			"type": "RsaSignatureSuite2017",
			"created": MessageDate.new_utc().to_string(),
			"signatureValue": b"..".join([encoded_header, b64safe_encode(sigdata)])
		}
	})

	return new_doc


def validate(document: MutableMapping[str, Any], algo: HS2019) -> bool:
	new_doc = deepcopy(document)
	signature = new_doc.pop("signature")
	jws_signature = signature["signatureValue"].encode("utf-8")
	encoded_header, encoded_signature = jws_signature.split(b"..")

	return algo.verify_data(
		algo.hash_data(b".".join([encoded_header, normalize_jsonld(new_doc)])),
		b64safe_decode(encoded_signature)
	)
