import re

import pandas as pd

ST_FILE = "st_homepage_tutorials.csv"
YT_FILE = "spoken_tutorial.csv"
OUTPUT_FILE = "st_homepage_with_youtube_flag.csv"
TOKEN_MATCH_THRESHOLD = 0.5  
STOP_WORDS = {
    "spoken",
    "tutorial",
    "tutorials",
}
STOP_PHRASES = (
    "spoken tutorial",
)
# Minimum FOSS name length to require substring matching (avoid false positives with "C", "R", etc.)
MIN_FOSS_LENGTH_FOR_SUBSTRING = 3

# Enable more lenient matching for edge cases
ENABLE_FALLBACK_MATCHING = True


def normalize(text):
    if pd.isna(text):
        return ""
    return str(text).lower().strip()


def remove_punctuation(text):
    return re.sub(r"[^\w\s]", " ", text)


def normalize_text_field(text):
    base = normalize(text)
    for phrase in STOP_PHRASES:
        base = base.replace(phrase, " ")
    no_punct = remove_punctuation(base)
    return " ".join(no_punct.split())


def tokenize_for_match(text):
    cleaned = normalize_text_field(text)
    tokens = [tok for tok in cleaned.split() if tok not in STOP_WORDS]
    if tokens:
        return tokens
    return cleaned.split()


def tokens_match(source_tokens, target_tokens):
    if not source_tokens or not target_tokens:
        return False
    overlap = set(source_tokens) & set(target_tokens)
    ratio = len(overlap) / len(set(source_tokens))
    return ratio >= TOKEN_MATCH_THRESHOLD


def build_language_patterns(language_value):
    tokens = [tok for tok in language_value.split() if tok]
    return [re.compile(rf"\b{re.escape(token)}\b") for token in tokens]


def extract_language_from_playlist(playlist_name):
    """Extract language from playlist name (e.g., 'Advance C - English' -> 'english')"""
    if pd.isna(playlist_name):
        return ""
    
    match = re.search(r'-\s*([a-zA-Z]+)\s*$', str(playlist_name))
    if match:
        return match.group(1).lower().strip()
    return ""


def extract_language_from_video_title(video_name):
    """Extract language from video title (e.g., 'Tutorial Name - Hindi' -> 'hindi')"""
    if pd.isna(video_name):
        return ""
    
    match = re.search(r'-\s*([a-zA-Z]+)\s*$', str(video_name))
    if match:
        return match.group(1).lower().strip()
    return ""


def main():
    st_df = pd.read_csv(ST_FILE)
    yt_df = pd.read_csv(YT_FILE)

    print(f"Loaded {len(st_df)} ST homepage tutorials")
    print(f"Loaded {len(yt_df)} YouTube videos")

    # Normalize YouTube data
    yt_df["playlist_norm"] = yt_df["playlist_name"].apply(normalize_text_field)
    yt_df["title_tokens"] = yt_df["video_name"].apply(tokenize_for_match)
    yt_df["title_lang_text"] = yt_df["video_name"].apply(normalize_text_field)
    yt_df["playlist_language"] = yt_df["playlist_name"].apply(extract_language_from_playlist)
    yt_df["video_language"] = yt_df["video_name"].apply(extract_language_from_video_title)
    if "description" in yt_df.columns:
        yt_df["description_lang_text"] = yt_df["description"].apply(normalize_text_field)
    else:
        yt_df["description_lang_text"] = ""

    # Normalize ST homepage data
    st_df["foss_norm"] = st_df["foss_name"].apply(normalize_text_field)
    st_df["tutorial_tokens"] = st_df["tutorial"].apply(tokenize_for_match)
    st_df["language_norm"] = st_df["language"].apply(normalize_text_field)
    st_df["language_patterns"] = st_df["language_norm"].apply(build_language_patterns)
    
    print("Processing tutorials...")

    def is_available(row):
        foss = row["foss_norm"]
        tutorial_tokens = row["tutorial_tokens"]
        language_patterns = row["language_patterns"]
        language_norm = row["language_norm"]

        if not foss or not tutorial_tokens or not language_patterns:
            return "No"

        # Filter YouTube videos by FOSS name
        if len(foss) < MIN_FOSS_LENGTH_FOR_SUBSTRING:
            # Use word boundary matching for short names
            pattern = rf"\b{re.escape(foss)}\b"
            candidates = yt_df[
                yt_df["playlist_norm"].str.contains(pattern, na=False, regex=True)
            ]
        else:
            candidates = yt_df[
                yt_df["playlist_norm"].str.contains(foss, na=False, regex=False)
            ]

        if candidates.empty:
            return "No"

        for _, video_row in candidates.iterrows():
            # Step 1: Check if tutorial tokens match video title tokens
            if not tokens_match(tutorial_tokens, video_row["title_tokens"]):
                continue

            # Step 2: Check language match - improved logic
            # Method 1: Check if language appears in title or description
            title_text = video_row["title_lang_text"]
            description_text = video_row["description_lang_text"]
            
            language_in_content = any(
                pattern.search(title_text) or pattern.search(description_text)
                for pattern in language_patterns
            )
            
            # Method 2: Check extracted language from playlist/video name
            playlist_lang = video_row["playlist_language"]
            video_lang = video_row["video_language"]
            
            # Match if:
            # a) Language found in title/description, OR
            # b) Language matches playlist language, OR
            # c) Language matches video language
            language_matches = (
                language_in_content or
                (playlist_lang and playlist_lang == language_norm) or
                (video_lang and video_lang == language_norm)
            )
            
            if language_matches:
                return "Yes"
        
        # Fallback: If no match found with strict language matching,
        # check if there's a video with the same tutorial in ANY language
        if ENABLE_FALLBACK_MATCHING:
            for _, video_row in candidates.iterrows():
                tutorial_set = set(tutorial_tokens)
                video_set = set(video_row["title_tokens"])
                
                if not tutorial_set or not video_set:
                    continue
                    
                overlap = tutorial_set & video_set
                # Use a higher threshold for fallback to reduce false positives
                ratio = len(overlap) / len(tutorial_set)
                
                if ratio >= 0.7:  
                    video_has_different_lang = (
                        (playlist_lang and playlist_lang != language_norm) or
                        (video_lang and video_lang != language_norm)
                    )
                    pass

        return "No"

    st_df["available_on_youTube"] = st_df.apply(is_available, axis=1)

    st_df.drop(
        columns=["foss_norm", "tutorial_tokens", "language_norm", "language_patterns"],
        inplace=True,
    )

    st_df.to_csv(OUTPUT_FILE, index=False)

    # Print summary statistics
    yes_count = (st_df["available_on_youTube"] == "Yes").sum()
    no_count = (st_df["available_on_youTube"] == "No").sum()
    
    print(f"\n{'='*60}")
    print(f"Done. Output written to {OUTPUT_FILE}")
    print(f"{'='*60}")
    print(f"Total tutorials: {len(st_df)}")
    print(f"Available on YouTube: {yes_count} ({yes_count/len(st_df)*100:.1f}%)")
    print(f"Not available: {no_count} ({no_count/len(st_df)*100:.1f}%)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
