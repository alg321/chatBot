import spacy
import random
from spacy.training import Example

# Training data with contextual weather examples and specific queries
train_data = [
    ("Cumbria is known for its rainy weather.", {"entities": [(0, 7, "LOC")]}),
    ("It's always sunny in Corfe Castle.", {"entities": [(16, 28, "LOC")]}),
    ("The Cotswolds are beautiful in the spring.", {"entities": [(4, 16, "LOC")]}),
    ("Cambridge can get chilly in the winter.", {"entities": [(0, 9, "LOC")]}),
    ("Bristol enjoys mild temperatures year-round.", {"entities": [(0, 7, "LOC")]}),
    ("Oxford experiences foggy mornings in autumn.", {"entities": [(0, 6, "LOC")]}),
    ("Norwich is often windy due to its coastal location.", {"entities": [(0, 7, "LOC")]}),
    ("Stonehenge is breathtaking during summer sunsets.", {"entities": [(0, 10, "LOC")]}),
    ("Watergate Bay is perfect for surfing in the summer.", {"entities": [(0, 13, "LOC")]}),
    ("Birmingham can be humid in the summer months.", {"entities": [(0, 10, "LOC")]}),
    ("What is the weather in Cumbria?", {"entities": [(21, 28, "LOC")]}),
    ("What will the weather be in Corfe Castle tomorrow?", {"entities": [(28, 40, "LOC")]}),
    ("Tell me about the weather in The Cotswolds.", {"entities": [(27, 39, "LOC")]}),
    ("What's the forecast for Cambridge?", {"entities": [(23, 32, "LOC")]}),
    ("What will the weather be in Bristol tomorrow?", {"entities": [(28, 35, "LOC")]}),
    ("Can you check the weather in Oxford?", {"entities": [(25, 31, "LOC")]}),
    ("Is it going to rain in Norwich?", {"entities": [(20, 27, "LOC")]}),
    ("I heard it's sunny in Stonehenge today.", {"entities": [(18, 28, "LOC")]}),
    ("What's the temperature like in Watergate Bay?", {"entities": [(32, 45, "LOC")]}),
    ("Humidity in Birmingham is high today.", {"entities": [(12, 22, "LOC")]}),
    ("What was the weather in Birmingham on June 20th, 2024?", {"entities": [(24, 34, "LOC"), (38, 50, "DATE")]}),
    ("Forecast for Bristol tomorrow?", {"entities": [(12, 19, "LOC"), (20, 28, "DATE")]}),
    ("What's the temperature in Oxford at 4 PM?", {"entities": [(26, 32, "LOC"), (36, 41, "TIME")]}),
    ("Show me the weather in Cambridge next Monday.", {"entities": [(22, 31, "LOC"), (32, 43, "DATE")]}),
    ("Tell me about the weather in Norwich at 9 AM tomorrow.", {"entities": [(27, 34, "LOC"), (38, 42, "TIME"), (46, 54, "DATE")]}),
    ("What's the weather like in Stonehenge on July 4th?", {"entities": [(28, 38, "LOC"), (42, 49, "DATE")]}),
    ("What will the temperature be in Watergate Bay at noon?", {"entities": [(35, 48, "LOC"), (52, 56, "TIME")]}),
    ("Humidity in Birmingham on Friday at 3 PM?", {"entities": [(12, 22, "LOC"), (26, 32, "DATE"), (36, 41, "TIME")]}),
    ("Will it rain in Cumbria next Wednesday?", {"entities": [(15, 22, "LOC"), (24, 37, "DATE")]}),
    ("What's the forecast for Corfe Castle on December 25th?", {"entities": [(24, 36, "LOC"), (40, 52, "DATE")]}),
    ("Show me the weather in The Cotswolds at 8:30 AM.", {"entities": [(22, 34, "LOC"), (38, 45, "TIME")]}),
    ("What will the temperature be in Cambridge at 1:45 PM?", {"entities": [(31, 40, "LOC"), (44, 51, "TIME")]}),
    ("Humidity in Bristol on Thursday morning?", {"entities": [(12, 19, "LOC"), (23, 31, "DATE")]}),
    # General non-weather and non-location-specific queries
    ("Hello, how are you?", {"entities": []}),
    ("What time is it?", {"entities": []}),
    ("Tell me a joke.", {"entities": []}),
    ("Can you help me with something?", {"entities": []}),
    ("What is your name?", {"entities": []}),
    ("Who won the game last night?", {"entities": []}),
    ("How's the stock market today?", {"entities": []}),
    ("What's the capital of France?", {"entities": [(21, 27, "LOC")]}),
    ("Where can I find the best pizza?", {"entities": []}),
    ("Is it going to rain tomorrow?", {"entities": [(24, 32, "DATE")]}),
    ("What should I wear today?", {"entities": [(23, 28, "DATE")]}),
]

# Load base SpaCy model with pre-trained word vectors
nlp = spacy.load("en_core_web_md")

# Check if NER component exists
if "ner" not in nlp.pipe_names:
    ner = nlp.create_pipe("ner")
    nlp.add_pipe(ner)
else:
    ner = nlp.get_pipe("ner")

# Add custom labels to the NER
ner.add_label("LOC")
ner.add_label("DATE")
ner.add_label("TIME")

# Disable other pipeline components and only train NER
other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
with nlp.disable_pipes(*other_pipes):
    optimizer = nlp.begin_training()

    # Iterate over training data
    for itn in range(30):  # Number of iterations
        random.shuffle(train_data)
        losses = {}
        for text, annotations in train_data:
            doc = nlp.make_doc(text)  # Create a Doc object from text
            example = Example.from_dict(doc, annotations)  # Create Example object
            nlp.update([example], drop=0.3, sgd=optimizer, losses=losses)
        print(f"Iteration {itn + 1}: Losses - {losses}")

# Save the trained model
output_dir = "models/custom_ner_model"
nlp.to_disk(output_dir)

print(f"Trained model saved to {output_dir}")
