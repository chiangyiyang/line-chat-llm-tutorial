# Batch script to process LINE chat data and extract event mentions
# Usage: Run each command in sequence with parameters as needed

# Set API keys as environment variables or place in a config file
export GOOGLE_API_KEY="YOUR_GOOGLE_AI_KEY"
export OPENAI_API_KEY="YOUR_OPENAI_KEY"
export MAPPING_API_KEY="YOUR_GOOGLE_MAP_API_KEY"

# Step 1: Clean chat data
python 01_clean_chat_data.py -I chat_history.txt -O output_summary.txt

# Step 2: Extract event mentions using Google API
python 02_extract_event_mentions.py -K $GOOGLE_API_KEY -L gemini-1.5-pro -S system_config_google.json -H history_google.json -I output_summary.txt -O event_log.txt -P google

# Step 2: Extract event mentions using OpenAI API
# python 02_extract_event_mentions.py -K $OPENAI_API_KEY -L gpt-4o -S system_config_openai.json -H history_openai.json -I output_summary.txt -O event_log.txt -P openai

# Step 3: Visualize event trends
python 03_visualize_event_trends.py -I event_log.txt -O chart.png

# Step 4: Identify event locations
python 04_identify_locations.py -I event_log.txt -O unique_places.csv

# Step 5: Map location coordinates using Mapping API key
python 05_map_location_coordinates.py -K $MAPPING_API_KEY -P 桃園市復興區華陵 -I unique_places.csv -O updated_places.csv -D place_db.csv

# Step 6: Export event log with mapped data
python 06_export_event_log.py -I event_log.txt -O output_matched_events.csv -D place_db.csv

# Step 7: Export event map
python 07_export_event_map.py -I output_matched_events.csv -O event_map.html