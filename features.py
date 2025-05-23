import pandas as pd
import sys
import os
# following code is sourced from reference code from Jill:
derivatives_path = 'output'

phoneme_to_feature = {
    # Vowels
    'AA': ['voiced', 'vowel', 'back', 'low', 'unrounded'],  # odd
    'AE': ['voiced', 'vowel', 'front', 'low', 'unrounded'],  # at
    'AH': ['voiced', 'vowel', 'central', 'mid', 'unrounded'],  # hut
    'AO': ['voiced', 'vowel', 'back', 'mid', 'rounded'],  # ought
    'AW': ['voiced', 'vowel', 'back', 'low-mid', 'rounded'],  # cow
    'AY': ['voiced', 'vowel', 'central-front', 'low-high', 'unrounded'],  # hide
    'EH': ['voiced', 'vowel', 'front', 'mid', 'unrounded'],  # ed
    'ER': ['voiced', 'vowel', 'central', 'mid', 'unrounded'],  # hurt
    'EY': ['voiced', 'vowel', 'front', 'mid-high', 'unrounded'],  # ate
    'IH': ['voiced', 'vowel', 'front', 'high', 'unrounded'],  # it
    'IY': ['voiced', 'vowel', 'front', 'high', 'unrounded'],  # eat
    'OW': ['voiced', 'vowel', 'back', 'mid-high', 'rounded'],  # oat
    'OY': ['voiced', 'vowel', 'back-front', 'mid-high', 'rounded'],  # toy
    'UH': ['voiced', 'vowel', 'back', 'high', 'rounded'],  # hood
    'UW': ['voiced', 'vowel', 'back', 'high', 'rounded'],  # two

    # Consonants - Stops
    'B': ['voiced', 'stop', 'bilabial', 'na_height', 'na_round'],  # be
    'D': ['voiced', 'stop', 'alveolar', 'na_height', 'na_round'],  # day
    'G': ['voiced', 'stop', 'velar', 'na_height', 'na_round'],  # go
    'K': ['unvoiced', 'stop', 'velar', 'na_height', 'na_round'],  # key
    'P': ['unvoiced', 'stop', 'bilabial', 'na_height', 'na_round'],  # pay
    'T': ['unvoiced', 'stop', 'alveolar', 'na_height', 'na_round'],  # take

    # Affricates
    'CH': ['unvoiced', 'affricate', 'palatal', 'na_height', 'na_round'],  # cheese
    'JH': ['voiced', 'affricate', 'palatal', 'na_height', 'na_round'],  # joy

    # Fricatives
    'DH': ['voiced', 'fricative', 'dental', 'na_height', 'na_round'],  # thee
    'F': ['unvoiced', 'fricative', 'labiodental', 'na_height', 'na_round'],  # fee
    'HH': ['unvoiced', 'fricative', 'glottal', 'na_height', 'na_round'],  # he
    'S': ['unvoiced', 'fricative', 'alveolar', 'na_height', 'na_round'],  # sea
    'SH': ['unvoiced', 'fricative', 'palatal', 'na_height', 'na_round'],  # she
    'TH': ['unvoiced', 'fricative', 'dental', 'na_height', 'na_round'],  # theta
    'V': ['voiced', 'fricative', 'labiodental', 'na_height', 'na_round'],  # vee
    'Z': ['voiced', 'fricative', 'alveolar', 'na_height', 'na_round'],  # zee
    'ZH': ['voiced', 'fricative', 'palatal', 'na_height', 'na_round'],  # seizure

    # Nasals
    'M': ['voiced', 'nasal', 'bilabial', 'na_height', 'na_round'],  # me
    'N': ['voiced', 'nasal', 'alveolar', 'na_height', 'na_round'],  # knee
    'NG': ['voiced', 'nasal', 'velar', 'na_height', 'na_round'],  # ping

    # Liquids
    'L': ['voiced', 'liquid', 'alveolar', 'na_height', 'na_round'],  # lay
    'R': ['voiced', 'liquid', 'palatal', 'na_height', 'na_round'],  # ray

    # Semivowels (Glides)
    'W': ['voiced', 'semivowel', 'bilabial', 'na_height', 'rounded'],  # way
    'Y': ['voiced', 'semivowel', 'palatal', 'na_height', 'unrounded'],  # yield

    # Special tokens
    '[SIL]': ['na_phonation', 'silence', 'na_place', 'na_height', 'na_round'],
    '[UNK]': ['na_phonation', 'unknown', 'na_place', 'na_height', 'na_round'],
    '[PAD]': ['na_phonation', 'padding', 'na_place', 'na_height', 'na_round'],
    'sp': ['na_phonation', 'silence', 'na_place', 'na_height', 'na_round'],  # short pause
    'spn': ['na_phonation', 'unknown', 'na_place', 'na_height', 'na_round'],  # spoken noise
}

# Feature categories
feature_categories = {
    'phonation': ['voiced', 'unvoiced', 'na_phonation'],
    'manner': ['vowel', 'stop', 'fricative', 'affricate', 'liquid', 'nasal', 'semivowel', 'silence', 'unknown',
               'padding'],
    'place': ['bilabial', 'labiodental', 'dental', 'alveolar', 'palatal', 'velar', 'glottal',
              'front', 'central', 'back', 'central-front', 'back-front', 'na_place'],
    'height': ['high', 'mid', 'low', 'mid-high', 'low-high', 'na_height'],
    'roundness': ['rounded', 'unrounded', 'na_round']
}


def normalize_phoneme(phoneme_str):
    """
    Normalize phoneme by removing any position numbers and mapping to base phoneme
    """

    base_phoneme = ''.join([c for c in phoneme_str if not c.isdigit() and c != ' '])
    return base_phoneme


def process_features(input_file, output_file):
    """
    Process phonemes from input CSV and generate feature vectors
    """
    print(f"Reading input file: {input_file}")

    # Read the input CSV
    try:
        phonemes = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    # Get unique phonemes from input for debugging
    unique_phonemes = phonemes['Phoneme'].unique()
    print(f"Unique phonemes in input: {unique_phonemes}")

    # Initialize feature columns
    for category in feature_categories:
        for feature in feature_categories[category]:
            phonemes[feature] = 0

    # Process each phoneme
    for idx, row in phonemes.iterrows():
        current_phoneme = normalize_phoneme(row['Phoneme'])
        print(f"Processing phoneme: {current_phoneme}")  # Debug print

        if current_phoneme in phoneme_to_feature:
            features = phoneme_to_feature[current_phoneme]
            # Set the features for this phoneme
            phonemes.at[idx, features[0]] = 1  # phonation
            phonemes.at[idx, features[1]] = 1  # manner
            phonemes.at[idx, features[2]] = 1  # place
            phonemes.at[idx, features[3]] = 1  # height
            phonemes.at[idx, features[4]] = 1  # roundness
        else:
            print(f"Warning: Unknown phoneme {current_phoneme}")
            # Set unknown features
            phonemes.at[idx, 'na_phonation'] = 1
            phonemes.at[idx, 'unknown'] = 1
            phonemes.at[idx, 'na_place'] = 1
            phonemes.at[idx, 'na_height'] = 1
            phonemes.at[idx, 'na_round'] = 1

    # Save the annotated file
    try:
        phonemes.to_csv(output_file, index=False)
        print(f"Saved annotated file to: {output_file}")
    except Exception as e:
        print(f"Error saving output file: {e}")


def main():
    # Create output directory if it doesn't exist
    os.makedirs(derivatives_path, exist_ok=True)

    # Default file paths for testing
    default_input = os.path.join(derivatives_path, 'test.csv')
    default_output = os.path.join(derivatives_path, 'test_with_features.csv')

    # Use command line arguments if provided, otherwise use defaults
    input_file = sys.argv[1] if len(sys.argv) > 1 else default_input
    output_file = sys.argv[2] if len(sys.argv) > 2 else default_output

    process_features(input_file, output_file)


if __name__ == "__main__":
    main()

    #test