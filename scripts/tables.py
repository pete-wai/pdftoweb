"""Curated semantic tables, visually transcribed from NIST IR 8547 (2026).

Run with uv run --locked python scripts/tables.py. Physical PDF page numbers
are one-based. Regions bound table cells, not captions or footnotes. None
represents a row covered by an earlier rowspan; it is not a missing value.
"""
import json
from pathlib import Path


def group(text, n):
    return {"text": text, "rowspan": n}


def region(page, y0, y1):
    return {"page": page, "y0": y0, "y1": y1}


def table(number, caption, headers, rows, regions):
    return dict(number=number, caption=f"Table {number}. {caption}", headers=headers, rows=rows, regions=regions)


transition = "<em><strong>Deprecated</strong></em> after 2030<br><em><strong>Disallowed</strong></em> after 2035"
security = "≥ 112 bits of classical security strength"
strength_headers = ["Parameter Sets", "Classical Security Strength", "Security Category"]
large = "<br>(assuming large enough output size)"

tables = [
    table(1, "Post-quantum security categories", ["Security Category", "Attack Type", "Example"], [
        ["1", "Key search on a block cipher with a 128-bit key", "AES-128"],
        ["2", "Collision search on a 256-bit hash function", "SHA-256"],
        ["3", "Key search on a block cipher with a 192-bit key", "AES-192"],
        ["4", "Collision search on a 384-bit hash function", "SHA3-384"],
        ["5", "Key search on a block cipher with a 256-bit key", "AES-256"],
    ], [region(22, 92, 197)]),
    table(2, "Quantum-vulnerable digital signature algorithms", ["Digital Signature Algorithm Family", "Parameters", "Transition"], [
        ["<strong>ECDSA</strong><br>[FIPS186]", security, transition],
        ["<strong>EdDSA</strong><br>[FIPS186]", "≥ 128 bits of classical security strength", transition],
        ["<strong>RSA</strong><br>[FIPS186]", security, transition],
    ], [region(22, 299, 418)]),
    table(3, "Post-quantum digital signature algorithms", ["Digital Signature Algorithm Family", *strength_headers], [
        [group("<strong>ML-DSA</strong><br>[FIPS204]", 3), "ML-DSA-44", "128 bits", '2 (see note <sup><a href="#fn-2" id="fnref-2">2</a></sup>)'],
        [None, "ML-DSA-65", "192 bits", "3"],
        [None, "ML-DSA-87", "256 bits", "5"],
        [group("<strong>SLH-DSA</strong><br>[FIPS205]", 3), "SLH-DSA-SHA2-128[s/f]<br>SLH-DSA-SHAKE-128[s/f]", "128 bits", "1"],
        [None, "SLH-DSA-SHA2-192[s/f]<br>SLH-DSA-SHAKE-192[s/f]", "192 bits", "3"],
        [None, "SLH-DSA-SHA2-256[s/f]<br>SLH-DSA-SHAKE-256[s/f]", "256 bits", "5"],
        [group("<strong>LMS, HSS</strong><br>[SP800208]", 2), "With SHA-256/192<br>With SHAKE256/192", "192 bits", "3"],
        [None, "With SHA-256<br>With SHAKE256", "256 bits", "5"],
        [group("<strong>XMSS, XMSS<sup><em>MT</em></sup></strong><br>[SP800208]", 2), "With SHA-256/192<br>With SHAKE256/192", "192 bits", "3"],
        [None, "With SHA-256<br>With SHAKE256", "256 bits", "5"],
    ], [region(23, 93, 392)]),
    table(4, "Quantum-vulnerable key-establishment schemes", ["Key-Establishment Scheme", "Parameters", "Transition"], [
        ["<strong>Finite Field<br>DH and MQV</strong><br>[SP80056A]", security, transition],
        ["<strong>Elliptic Curve<br>DH and MQV</strong><br>[SP80056A]", security, transition],
        ["<strong>RSA</strong><br>[SP80056B]", security, transition],
    ], [region(23, 579, 661), region(24, 71, 230)]),
    table(5, "Post-quantum key-establishment schemes", ["Key-Establishment Scheme", *strength_headers], [
        [group("<strong>ML-KEM</strong><br>[FIPS203]", 3), "ML-KEM-512", "128 bits", "1"],
        [None, "ML-KEM-768", "192 bits", "3"],
        [None, "ML-KEM-1024", "256 bits", "5"],
    ], [region(24, 467, 572)]),
    table(6, "Block ciphers", ["Block Cipher", *strength_headers], [
        [group("<strong>AES</strong><br>[FIPS197]", 3), "AES-128", "128 bits", "1"],
        [None, "AES-192", "192 bits", "3"],
        [None, "AES-256", "256 bits", "5"],
    ], [region(25, 350, 446)]),
    table(7, "Authenticated Encryption with Associated Data (AEAD)", ["Authenticated Encryption with Associated Data (AEAD)", *strength_headers], [
        ["<strong>Ascon</strong><br>[SP800232]", "AES-AEAD128", "128 bits", "1"],
    ], [region(25, 474, 532)]),
    table(8, "Hash functions and XOFs", ["Hash/XOF Algorithm Family", "Variants", "Collision Security Strength (classical)", "Collision Security Category", 'Preimage Security Strength<sup><a href="#fn-3" id="fnref-3">3</a></sup> (classical)', "Preimage Security Category"], [
        ['<strong>SHA-1</strong><br>[FIPS180]<sup><a href="#fn-4" id="fnref-4">4</a></sup>', "SHA-1", "&lt;80 bits", "&lt; 1", "160 bits", "1"],
        [group("<strong>SHA-2</strong><br>[FIPS180]", 4), "SHA-224<br>SHA-512/224", "112 bits", "&lt; 1", "224 bits", "3"],
        [None, "SHA-256<br>SHA-512/256", "128 bits", "2", "256 bits", "5"],
        [None, "SHA-384", "192 bits", "4", "384 bits", "5"],
        [None, "SHA-512", "256 bits", "5", "512 bits", "5"],
        [group("<strong>SHA-3</strong><br>[FIPS202]", 6), "SHA3-224", "112 bits", "&lt; 1", "224 bits", "3"],
        [None, "SHA3-256", "128 bits", "2", "256 bits", "5"],
        [None, "SHAKE128" + large, "128 bits", "2", "128 bits", "2"],
        [None, "SHA3-384", "192 bits", "4", "384 bits", "5"],
        [None, "SHA3-512", "256 bits", "5", "512 bits", "5"],
        [None, "SHAKE256" + large, "256 bits", "5", "256 bits", "5"],
        [group("<strong>Ascon</strong><br>[SP800232]", 3), "Ascon-Hash256", "128 bits", "2", "128 bits", "2"],
        [None, "Ascon-XOF128" + large, "128 bits", "2", "128 bits", "2"],
        [None, "Ascon-CXOF128" + large, "128 bits", "2", "128 bits", "2"],
    ], [region(25, 561, 659), region(26, 71, 528)]),
]

if __name__ == "__main__":
    target = Path(__file__).resolve().parents[1] / "evidence/tables.json"
    target.write_text(json.dumps(tables, ensure_ascii=False, indent=2) + "\n")
    print(f"Wrote {len(tables)} tables to {target}")
