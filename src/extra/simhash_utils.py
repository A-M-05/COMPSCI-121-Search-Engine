import hashlib

def hash_token(token : str, num_bits : int) -> int:
    """
    Hash a token into a stable integer fingerprint truncated to num_bits.
    
    :param token: Token string to hash
    :type token: str
    :param num_bits: Number of bits to keep
    :type num_bits: int
    :return: Integer hash value truncated to num_bits
    :rtype: int
    """

    digest = hashlib.sha1(token.encode("utf-8")).digest()
    value = int.from_bytes(digest, "big")
    mask = (1 << num_bits) - 1
    return value & mask

def compute_simhash(local_counts : dict[str, int], num_bits : int) -> int:
    """
    Compute a SimHash fingerprint for a document using weighted terms.

    :param local_counts: Mapping of token -> weighted term frequency
    :type local_counts: dict[str, float]
    :param num_bits: Number of bits in the fingerprint
    :type num_bits: int
    :return: SimHash fingerprint as an integer
    :rtype: int
    """
    vector = [0.0] * num_bits

    for token, weight in local_counts.items():
        token_hash = hash_token(token, num_bits)

        for i in range(num_bits):
            bitmask = 1 << i
            if token_hash & bitmask:
                vector[i] += weight
            else:
                vector[i] -= weight

    fingerprint = 0
    for i in range(num_bits):
        if vector[i] > 0:
            fingerprint |= (1 << i)

    return fingerprint

def hamming_distance(fp1 : int, fp2 : int) -> int:
    """
    Compute the Hamming distance between two fingerprints.

    :param fp1: First fingerprint
    :type fp1: int
    :param fp2: Second fingerprint
    :type fp2: int
    :return: Number of differing bits
    :rtype: int
    """
    x = fp1 ^ fp2
    count = 0
    while x:
        count += x & 1
        x >>= 1
    return count

def bucket_key(fingerprint : int, bucket_bits : int, num_bits : int):
    """
    Get a bucket key from the high-order bits of a fingerprint.

    :param fingerprint: SimHash fingerprint
    :type fingerprint: int
    :param bucket_bits: Number of leading bits to use as bucket key
    :type bucket_bits: int
    :param num_bits: Total number of bits in the fingerprint
    :type num_bits: int
    :return: Bucket key
    :rtype: int
    """
    shift = num_bits - bucket_bits
    return fingerprint >> shift
