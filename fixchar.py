import pandas as pd
import unicodedata

# ✅ Character mapping for Turkish characters
CHARACTER_MAP = {
    '√º': 'ü', '√ß': 'ç',
    '√ú': 'Ü',
    '≈û': 'Ş', '≈ü': 'ş',
    'Ã‡': 'Ç', 'Ã§': 'ç',
    'Ä°': 'İ', 'Ä±': 'ı',
    'ÅŸ': 'ş', 'Åž': 'Ş',
    'ÄŸ': 'ğ', 'Äž': 'Ğ',
    'Ã¼': 'ü', 'Ãœ': 'Ü',
    'Ã¶': 'ö', 'Ã–': 'Ö',
    'Ã¢': 'â', 'Ã‚': 'Â',
    'Ãª': 'ê', 'ÃŠ': 'Ê',
    'Ã¡': 'á', 'ÃÁ': 'Á',
    'Ã©': 'é', 'Ã‰': 'É',
    'Ã¨': 'è', 'Ãˆ': 'È',
    'Ã«': 'ë', 'Ã‹': 'Ë',
    'Ã´': 'ô', 'Ã”': 'Ô',
    'Ã¸': 'ø', 'Ã˜': 'Ø',
    'Ã£': 'ã', 'Ãƒ': 'Ã',
    'Ãµ': 'õ', 'Ã•': 'Õ',
    'â€™': "'", 'â€˜': "'",
    'ÃŸ': 'ß', 'â€“': '-',
    'â€”': '—', 'â€œ': '"',
    'â€': '"', 'â€¦': '…',
    'Ã': 'ı', 'Ä': 'İ',
    'Å': 'Ş', 'Ã¿': 'ÿ',
    'ก': 'ı', 'ษ': 'Ş', '™': '',  # Fix weird Thai-like characters
    '¶': '', '§': '',  # Remove unwanted symbols
}

# ✅ Fix function with double-decoding
def fix_turkish_characters(text):
    if isinstance(text, str):
        try:
            # 🌟 Step 1: Double decoding (ISO-8859-9 → UTF-8)
            text = text.encode('ISO-8859-9').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
        
        # 🌟 Step 2: Apply character map
        for wrong_char, correct_char in CHARACTER_MAP.items():
            text = text.replace(wrong_char, correct_char)

        # 🌟 Step 3: Clean up combining characters
        text = unicodedata.normalize("NFC", text)

    return text

# ✅ Load the corrupted file
input_file = "book_sales_files/g1_20250315.csv"
output_file = "fixed.csv"

# ✅ Read the file using ISO-8859-9 encoding
df = pd.read_csv(input_file, encoding="ISO-8859-9", on_bad_lines="skip")

# ✅ Fix Turkish characters in all columns
df = df.applymap(fix_turkish_characters)

# ✅ Save the fixed data to a new CSV file (UTF-8 encoding)
df.to_csv(output_file, index=False, encoding="utf-8")

print(f"✅ Fixed data saved to '{output_file}'")
