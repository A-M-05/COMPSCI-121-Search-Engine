from ..config.settings import SIMHASH_HAMMING_THRESHOLD, SIMHASH_BUCKET_BITS, SIMHASH_BITS
from .simhash_utils import compute_simhash, hamming_distance, bucket_key
import re
import hashlib


class DuplicateDetector:
    def __init__(self):
        self.seen_hashes = {}
        self.fingerprint_buckets = {}
        self.threshold = SIMHASH_HAMMING_THRESHOLD
        self.bucket_bits = SIMHASH_BUCKET_BITS
        self.num_bits = SIMHASH_BITS

    def build_exact_text(self, fields: dict[str, str]) -> str:
        """
        Build normalized text used for exact duplicate detection.

        :param fields: Extracted fields from a document
        :type fields: dict[str, str]
        :return: Normalized combined text
        :rtype: str
        """
        combined_text = " ".join([
            fields["title"],
            fields["headings"],
            fields["bold"],
            fields["body"]
        ])
        normalized_combined_text = re.sub(r"\s+", " ", combined_text.lower()).strip()
        return normalized_combined_text

    def check_exact(self, url: str, fields: dict[str, str], current_doc_id: int) -> tuple[bool, int | None, str | None]:
        """
        Check whether a page is an exact duplicate of previously seen content.

        :param url: Current page URL
        :type url: str
        :param fields: Extracted text fields
        :type fields: dict[str, str]
        :param current_doc_id: Current docID candidate
        :type current_doc_id: int
        :return: (is_duplicate, kept_doc_id, kept_url)
        :rtype: tuple[bool, int | None, str | None]
        """
        normalized_text = self.build_exact_text(fields)
        exact_hash = hashlib.sha1(normalized_text.encode("utf-8")).hexdigest()

        if exact_hash in self.seen_hashes:
            kept_doc_id, kept_url = self.seen_hashes[exact_hash]
            return (True, kept_doc_id, kept_url)

        self.seen_hashes[exact_hash] = (current_doc_id, url)
        return (False, None, None)

    def check_near(self, url: str, current_doc_id: int, local_counts: dict[str, float]) -> list[tuple[int, str, int]]:
        """
        Check whether a page is near-duplicate to previously seen pages in the same bucket.

        :param url: Current page URL
        :type url: str
        :param current_doc_id: Current docID candidate
        :type current_doc_id: int
        :param local_counts: Weighted term counts for the current document
        :type local_counts: dict[str, float]
        :return: List of matches as (prior_doc_id, prior_url, distance)
        :rtype: list[tuple[int, str, int]]
        """
        fingerprint = compute_simhash(local_counts, self.num_bits)
        key = bucket_key(fingerprint, self.bucket_bits, self.num_bits)

        bucket = self.fingerprint_buckets.get(key, [])
        near_matches = []

        for prior_doc_id, prior_url, prior_fingerprint in bucket:
            distance = hamming_distance(fingerprint, prior_fingerprint)
            if distance <= self.threshold:
                near_matches.append((prior_doc_id, prior_url, distance))

        bucket.append((current_doc_id, url, fingerprint))
        self.fingerprint_buckets[key] = bucket

        return near_matches