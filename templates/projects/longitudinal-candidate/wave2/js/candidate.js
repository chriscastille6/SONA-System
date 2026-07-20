/**
 * CANDIDATE linking protocol (adapted from Sandnes, 2021, PLOS ONE)
 * for client-side longitudinal surveys.
 *
 * Adaptation notes
 * ----------------
 * Sandnes (2021) hashes participant names with djb2 / CRC-32 families and
 * truncates into a small coding space. For IRB-approved SONA studies where
 * names must never enter the research instrument, this module instead hashes
 * three static security-question answers that only the participant can
 * recreate. The digest is truncated to a 16-character hex linking ID.
 *
 * Properties enforced here
 * - Pure client-side; no network calls
 * - Raw answers are never persisted — only the 16-char hash enters the dataset
 * - Deterministic: identical normalized answers → identical Candidate ID
 * - No master re-identification table is created or required
 *
 * Citation: Sandnes, F. E. (2021). CANDIDATE: A tool for generating anonymous
 * participant-linking IDs in multi-session studies. PLOS ONE, 16(12), e0260569.
 */
(function (global) {
  "use strict";

  var DELIMITER = "|";
  var ID_LENGTH = 16;

  /**
   * Normalize a security-question answer for stable hashing.
   * - trim, collapse whitespace
   * - lowercase
   * - strip non-alphanumeric (except keeping digits for birth day)
   */
  function normalizeAnswer(raw) {
    if (raw == null) return "";
    return String(raw)
      .trim()
      .toLowerCase()
      .replace(/\s+/g, "")
      .replace(/[^a-z0-9]/g, "");
  }

  /** Compose the three answers into the pre-image string. */
  function composePreimage(answers) {
    var a = normalizeAnswer(answers.motherMaidenInitials);
    var b = normalizeAnswer(answers.birthDayOfMonth);
    var c = normalizeAnswer(answers.childhoodStreetInitials);
    if (!a || !b || !c) {
      throw new Error("All three CANDIDATE security answers are required.");
    }
    // Birth day must be 1–31 after normalization (digits only).
    var day = parseInt(b, 10);
    if (Number.isNaN(day) || day < 1 || day > 31) {
      throw new Error("Birth day of month must be an integer from 1 to 31.");
    }
    // Zero-pad day so "7" and "07" collide intentionally (same person).
    var dayNorm = String(day).padStart(2, "0");
    return [a, dayNorm, c].join(DELIMITER);
  }

  /* ---- Minimal SHA-256 (public domain style; no external CDN) ---- */
  function sha256Hex(ascii) {
    function rightRotate(value, amount) {
      return (value >>> amount) | (value << (32 - amount));
    }

    var mathPow = Math.pow;
    var maxWord = mathPow(2, 32);
    var lengthProperty = "length";
    var i, j;
    var result = "";

    var words = [];
    var asciiBitLength = ascii[lengthProperty] * 8;

    var hash = (sha256Hex.h = sha256Hex.h || []);
    var k = (sha256Hex.k = sha256Hex.k || []);
    var primeCounter = k[lengthProperty];

    var isComposite = {};
    for (var candidate = 2; primeCounter < 64; candidate++) {
      if (!isComposite[candidate]) {
        for (i = 0; i < 313; i += candidate) {
          isComposite[i] = candidate;
        }
        hash[primeCounter] = (mathPow(candidate, 0.5) * maxWord) | 0;
        k[primeCounter++] = (mathPow(candidate, 1 / 3) * maxWord) | 0;
      }
    }

    ascii += "\x80";
    while ((ascii[lengthProperty] % 64) - 56) ascii += "\x00";
    for (i = 0; i < ascii[lengthProperty]; i++) {
      j = ascii.charCodeAt(i);
      if (j >> 8) return ""; // UTF-8 only for this minimal impl; we normalize to ASCII
      words[i >> 2] |= j << (((3 - i) % 4) * 8);
    }
    words[words[lengthProperty]] = (asciiBitLength / maxWord) | 0;
    words[words[lengthProperty]] = asciiBitLength;

    for (j = 0; j < words[lengthProperty]; ) {
      var w = words.slice(j, (j += 16));
      var oldHash = hash;
      hash = hash.slice(0, 8);

      for (i = 0; i < 64; i++) {
        var w15 = w[i - 15],
          w2 = w[i - 2];
        var a = hash[0],
          e = hash[4];
        var temp1 =
          hash[7] +
          (rightRotate(e, 6) ^ rightRotate(e, 11) ^ rightRotate(e, 25)) +
          ((e & hash[5]) ^ (~e & hash[6])) +
          k[i] +
          (w[i] =
            i < 16
              ? w[i]
              : (w[i - 16] +
                  (rightRotate(w15, 7) ^ rightRotate(w15, 18) ^ (w15 >>> 3)) +
                  w[i - 7] +
                  (rightRotate(w2, 17) ^ rightRotate(w2, 19) ^ (w2 >>> 10))) |
                0);
        var temp2 =
          (rightRotate(a, 2) ^ rightRotate(a, 13) ^ rightRotate(a, 22)) +
          ((a & hash[1]) ^ (a & hash[2]) ^ (hash[1] & hash[2]));
        hash = [(temp1 + temp2) | 0].concat(hash);
        hash[4] = (hash[4] + temp1) | 0;
        hash.pop();
      }

      for (i = 0; i < 8; i++) {
        hash[i] = (hash[i] + oldHash[i]) | 0;
      }
    }

    for (i = 0; i < 8; i++) {
      for (j = 3; j + 1; j--) {
        var b = (hash[i] >> (j * 8)) & 255;
        result += (b < 16 ? "0" : "") + b.toString(16);
      }
    }
    return result;
  }

  /**
   * Sandnes-inspired auxiliary hashes (djb2 + CRC-32 of reverse) mixed into
   * the SHA-256 pre-image so the linking token inherits multi-function
   * collision resistance ideas from the original CANDIDATE procedure, while
   * remaining fully deterministic and offline.
   */
  function djb2(str) {
    var hash = 5381;
    for (var i = 0; i < str.length; i++) {
      hash = ((hash << 5) + hash) ^ str.charCodeAt(i);
      hash = hash >>> 0;
    }
    return hash >>> 0;
  }

  function crc32(str) {
    var table = sha256Hex._crcTable;
    if (!table) {
      table = [];
      for (var n = 0; n < 256; n++) {
        var c = n;
        for (var k = 0; k < 8; k++) {
          c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
        }
        table[n] = c >>> 0;
      }
      sha256Hex._crcTable = table;
    }
    var crc = 0xffffffff;
    for (var i = 0; i < str.length; i++) {
      crc = table[(crc ^ str.charCodeAt(i)) & 0xff] ^ (crc >>> 8);
    }
    return (crc ^ 0xffffffff) >>> 0;
  }

  /**
   * Generate the 16-character CANDIDATE Hash ID from three security answers.
   * @param {{motherMaidenInitials:string, birthDayOfMonth:string|number, childhoodStreetInitials:string}} answers
   * @returns {string} 16-char lowercase hex linking ID
   */
  function generateCandidateId(answers) {
    var base = composePreimage(answers);
    var reverse = base.split("").reverse().join("");
    var enriched =
      base +
      DELIMITER +
      djb2(base).toString(16) +
      DELIMITER +
      crc32(reverse).toString(16);
    var digest = sha256Hex(enriched);
    if (!digest || digest.length < ID_LENGTH) {
      throw new Error("CANDIDATE hash generation failed.");
    }
    return digest.slice(0, ID_LENGTH);
  }

  /** Validate a previously generated ID format. */
  function isValidCandidateId(id) {
    return typeof id === "string" && /^[a-f0-9]{16}$/.test(id);
  }

  global.CandidateProtocol = {
    normalizeAnswer: normalizeAnswer,
    composePreimage: composePreimage,
    generateCandidateId: generateCandidateId,
    isValidCandidateId: isValidCandidateId,
    ID_LENGTH: ID_LENGTH,
    VERSION: "1.0.0-sandnes-adapted",
  };
})(typeof window !== "undefined" ? window : globalThis);
