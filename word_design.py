#!/usr/bin/env python3

# Solution to CSPlib problem 033 (https://www.csplib.org/Problems/prob033/)

import argparse
import subprocess
from itertools import combinations, product

from validator import validate_all_constraints

WORD_LENGTH = 8
LETTERS = ["A", "C", "G", "T"]
COMPLEMENTS = {"A": "T", "T": "A", "C": "G", "G": "C"}


class WorldProblemEncoder:
    def __init__(self, num_words):
        self.num_words = num_words
        self.clauses = []
        self.var_map = {}
        self.next_var = 1

    def get_var(self, word_idx, pos, letter):
        """Get variable number for word[word_idx][pos] = letter"""
        key = (word_idx, pos, letter)

        if key not in self.var_map:
            self.var_map[key] = self.next_var
            self.next_var += 1

        return self.var_map[key]

    def exactly_one_letter_per_position(self):
        """Each position in each word must have exactly one letter"""
        for word in range(self.num_words):
            for pos in range(WORD_LENGTH):
                self.clauses.append(
                    [self.get_var(word, pos, letter) for letter in LETTERS]
                )

                for l1, l2 in combinations(LETTERS, 2):
                    self.clauses.append(
                        [-self.get_var(word, pos, l1), -self.get_var(word, pos, l2)]
                    )

    def exactly_four_cg_letters(self):
        """Each word must have exactly four C/G letters"""
        for word in range(self.num_words):
            cg_vars = []

            for pos in range(WORD_LENGTH):
                c_var = self.get_var(word, pos, "C")
                g_var = self.get_var(word, pos, "G")
                a_var = self.get_var(word, pos, "A")
                t_var = self.get_var(word, pos, "T")

                is_cg = self.next_var
                self.next_var += 1
                cg_vars.append(is_cg)

                # is_cg ↔ (c_var ∨ g_var)
                self.clauses.append([-is_cg, c_var, g_var])
                self.clauses.append([-c_var, is_cg])
                self.clauses.append([-g_var, is_cg])

                # position must be either C,G or A,T
                self.clauses.append([c_var, g_var, a_var, t_var])

                # C,G and A,T are exclusive
                self.clauses.append([-c_var, -a_var])
                self.clauses.append([-c_var, -t_var])
                self.clauses.append([-g_var, -a_var])
                self.clauses.append([-g_var, -t_var])

            for five_positions in combinations(cg_vars, 5):
                self.clauses.append([-var for var in five_positions])

            not_cg_vars = []

            for pos in range(WORD_LENGTH):
                not_cg = self.next_var
                self.next_var += 1
                not_cg_vars.append(not_cg)

                # not_cg ↔ (a_var ∨ t_var)
                a_var = self.get_var(word, pos, "A")
                t_var = self.get_var(word, pos, "T")
                self.clauses.append([-not_cg, a_var, t_var])
                self.clauses.append([-a_var, not_cg])
                self.clauses.append([-t_var, not_cg])

                # position must be either C,G or not C,G
                self.clauses.append([cg_vars[pos], not_cg])
                self.clauses.append([-cg_vars[pos], -not_cg])

            for five_positions in combinations(not_cg_vars, 5):
                self.clauses.append([-var for var in five_positions])

            for pos in range(WORD_LENGTH):
                c_var = self.get_var(word, pos, "C")
                g_var = self.get_var(word, pos, "G")
                a_var = self.get_var(word, pos, "A")
                t_var = self.get_var(word, pos, "T")

                self.clauses.append([c_var, g_var, a_var, t_var])

                self.clauses.append([-c_var, -a_var])
                self.clauses.append([-c_var, -t_var])
                self.clauses.append([-g_var, -a_var])
                self.clauses.append([-g_var, -t_var])

    def distance_difference_constraint(self):
        """Each pair of words must differ in at least 4 positions"""
        for w1, w2 in combinations(range(self.num_words), 2):
            same_pos_vars = []

            for pos in range(WORD_LENGTH):
                # same_var ↔ (w1[pos] = w2[pos])
                same_var = self.next_var
                self.next_var += 1
                same_pos_vars.append(same_var)

                for l1, l2 in product(LETTERS, repeat=2):
                    if l1 == l2:
                        self.clauses.append(
                            [
                                -self.get_var(w1, pos, l1),
                                -self.get_var(w2, pos, l2),
                                same_var,
                            ]
                        )
                    else:
                        self.clauses.append(
                            [
                                -self.get_var(w1, pos, l1),
                                -self.get_var(w2, pos, l2),
                                -same_var,
                            ]
                        )

            for same_pos in combinations(same_pos_vars, 5):
                self.clauses.append([-var for var in same_pos])

    def reverse_complement_constraint(self):
        """Each word's reverse must differ from each word's complement in at least 4 positions"""

        for w1 in range(self.num_words):  # word to be reversed
            for w2 in range(self.num_words):  # word to be complemented
                same_pos_vars = []

                for pos in range(WORD_LENGTH):
                    same_var = self.next_var
                    self.next_var += 1
                    same_pos_vars.append(same_var)

                    rev_pos = WORD_LENGTH - 1 - pos

                    for letter in LETTERS:
                        compl = COMPLEMENTS[letter]

                        self.clauses.append(
                            [
                                -self.get_var(w1, rev_pos, letter),
                                -self.get_var(w2, pos, compl),
                                same_var,
                            ]
                        )

                        for wrong_compl in LETTERS:
                            if wrong_compl != compl:
                                self.clauses.append(
                                    [
                                        -self.get_var(w1, rev_pos, letter),
                                        -self.get_var(w2, pos, wrong_compl),
                                        -same_var,
                                    ]
                                )

                for same_pos in combinations(same_pos_vars, 5):
                    self.clauses.append([-var for var in same_pos])

    def encode(self):
        """Generate CNF encoding"""
        self.exactly_one_letter_per_position()
        self.exactly_four_cg_letters()
        self.distance_difference_constraint()
        self.reverse_complement_constraint()

        lines = []
        lines.append(f"p cnf {self.next_var-1} {len(self.clauses)}")

        for clause in self.clauses:
            lines.append(" ".join(map(str, clause + [0])))

        return "\n".join(lines)

    def decode_solution(self, solution):
        """Decode SAT solution into words"""
        decoded = ""

        for line in solution.splitlines():
            if line.startswith("c"):
                continue
            if line.startswith("s"):
                print("SATISFIABLE")
            if line.startswith("v"):
                decoded += line[2:]
            else:
                continue

        values = list(map(int, decoded.split()))

        words = []
        for word in range(self.num_words):
            current_word = ""
            for pos in range(WORD_LENGTH):
                for letter in LETTERS:
                    var = self.get_var(word, pos, letter)
                    if values[var - 1] > 0:
                        current_word += letter
                        break
            words.append(current_word)

        return words


def main():
    parser = argparse.ArgumentParser(
        description="Encode and solve CSPlib problem 033",
        epilog="Made by Martin Rosenberg during winter semester at MFF CUNI 2024/25",
    )

    parser.add_argument(
        "number_of_words",
        type=int,
        help="Maximum number of words to encode (and possibly solve for)",
    )

    parser.add_argument(
        "-s",
        "--solver",
        type=str,
        help="SAT solver to use",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbosity output for solver and validation",
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate solution after solving and decoding",
    )

    args = parser.parse_args()

    encoder = WorldProblemEncoder(num_words=args.number_of_words)
    cnf = encoder.encode()

    with open("word_problem.cnf", "w", encoding="ASCII") as f:
        f.write(cnf)

    if args.solver is None:
        print("No solver specified. Exiting.")
        return

    solution = subprocess.run(
        [
            args.solver,
            "-model",
            "word_problem.cnf",
            "-verb=" + "1" if args.verbose else "0",
        ],
        stdout=subprocess.PIPE,
    )

    if args.verbose:
        print(solution.stdout.decode())

    words = encoder.decode_solution(solution.stdout.decode())
    for word in words:
        print(word)

    if args.validate and words:
        validate_all_constraints(words, verbose=args.verbose)


if __name__ == "__main__":
    main()
