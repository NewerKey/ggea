from functools import lru_cache

from src.security.hashing.algorithms import Argon2Algorithm, BCryptAlgorithm, SHA256Algorithm, SHA512Algorithm
from src.utility.typing.algorithm import HashingAlgorithmSubClass


class HashingFunctionFactory:
    @staticmethod
    def initialize_hashing_function(algorithm: str) -> HashingAlgorithmSubClass:
        if algorithm == "bc":
            return BCryptAlgorithm()
        elif algorithm == "a2":
            return Argon2Algorithm()
        elif algorithm == "256":
            return SHA256Algorithm()
        elif algorithm == "512":
            return SHA512Algorithm()
        raise Exception("Algorithm is not registered!")


@lru_cache()
def get_hashing_function(algorithm: str) -> HashingAlgorithmSubClass:
    return HashingFunctionFactory.initialize_hashing_function(algorithm=algorithm)
