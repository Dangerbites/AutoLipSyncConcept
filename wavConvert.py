import json
import pronouncing
from tqdm import tqdm

def replace_words_with_phonemes(json_file):
    # Load the JSON file
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Replace words with phonemes
    for item in tqdm(data, desc='Replacing'):
        word = item['word']
        phonemes = get_phonemes_for_word(word)
        item['word'] = phonemes

    return data

def get_phonemes_for_word(word):
    # Use pronouncing library to extract phonemes for the word
    phonemes_list = pronouncing.phones_for_word(word)

    # Return the first phoneme from the list if available, otherwise return the word itself
    return phonemes_list[0] if phonemes_list else word

# Specify the input JSON file path
json_file = r'C:\Users\Dange\Desktop\phomeneExtractor\output.json'

# Replace words with phonemes
updated_data = replace_words_with_phonemes(json_file)

# Print the updated data
print(updated_data)
