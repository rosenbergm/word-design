def word_distance(word1, word2):
    """Calculate distance difference between two words"""
    return sum(c1 != c2 for c1, c2 in zip(word1, word2))


def verify_cg_constraint(words, verbose=False):
    """Verify that each word has exactly 4 C/G letters"""
    valid = True
    for i, word in enumerate(words):
        cg_count = sum(1 for c in word if c in ["C", "G"])
        at_count = sum(1 for c in word if c in ["A", "T"])
        if verbose:
            print(f"Word {i+1}: {word}")
            print(f"  C/G count: {cg_count}")
            print(f"  A/T count: {at_count}")
        if cg_count != 4 or at_count != 4:
            if verbose:
                print("  CONSTRAINT VIOLATION: Must have exactly 4 C/G letters!")
            valid = False
    return valid


def verify_distance_differ(words, verbose=False):
    """Verify that each pair of words differs in at least 4 positions"""
    valid = True
    for i, word1 in enumerate(words):
        for j, word2 in enumerate(words[i + 1 :], i + 1):
            dist = word_distance(word1, word2)
            if verbose:
                print(f"Words {i+1} and {j+1}: {word1} vs {word2}")
                print(f"  Distance: {dist}")
            if dist < 4:
                if verbose:
                    print("  CONSTRAINT VIOLATION: Distance must be at least 4!")
                    print("  Positions that differ:", end=" ")
                    for pos, (c1, c2) in enumerate(zip(word1, word2)):
                        if c1 != c2:
                            print(pos + 1, end=" ")
                    print()
                valid = False
            else:
                if verbose:
                    print("  OK")
    return valid


def get_complement(word):
    """Get Watson-Crick complement of a word"""
    compl = {"A": "T", "T": "A", "C": "G", "G": "C"}
    return "".join(compl[c] for c in word)


def verify_reverse_complement_constraint(words, verbose=False):
    """Verify that each word's reverse differs from each word's complement in at least 4 positions"""
    valid = True
    for i, word1 in enumerate(words):
        word1_rev = word1[::-1]
        for j, word2 in enumerate(words):
            word2_compl = get_complement(word2)
            dist = word_distance(word1_rev, word2_compl)
            if verbose:
                print(f"Word {i+1} reverse vs Word {j+1} complement:")
                print(f"  {word1_rev} vs {word2_compl}")
                print(f"  Distance: {dist}")
            if dist < 4:
                if verbose:
                    print("  CONSTRAINT VIOLATION: Distance must be at least 4!")
                    print("  Positions that differ:", end=" ")
                    for pos, (c1, c2) in enumerate(zip(word1_rev, word2_compl)):
                        if c1 != c2:
                            print(pos + 1, end=" ")
                    print()
                valid = False
            else:
                if verbose:
                    print("  OK")
    return valid


def validate_all_constraints(words, verbose=False):
    """Validate all constraints"""
    print("\nVerifying constraints:")

    if verbose:
        print("\n=== Validating C/G letter constraint ===")
    cg_valid = verify_cg_constraint(words, verbose)

    if verbose:
        print("\n=== Validating distance constraint ===")
    distance_valid = verify_distance_differ(words, verbose)

    if verbose:
        print("\n=== Validating reverse-complement constraint ===")
    rev_compl_valid = verify_reverse_complement_constraint(words, verbose)

    print("\n=== Summary ===")
    if cg_valid and distance_valid and rev_compl_valid:
        print("All constraints satisfied!")
    else:
        print("Some constraints were violated!")
        if not cg_valid:
            print("- C/G letter constraint violated")
        if not distance_valid:
            print("- Distance constraint violated")
        if not rev_compl_valid:
            print("- Reverse-complement constraint violated")
