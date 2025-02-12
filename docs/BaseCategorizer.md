# BaseCategorizer

The `BaseCategorizer` class provides functionality for categorizing input data
utilizing a specified LLM provider. This class serves as a base for implementing
categorization tasks where inputs are classified into predefined categories.

## Features

-   **Custom Categories**: Define your own categories for data classification.
-   **Input Validation**: Ensures the integrity of categories, examples, and
    input data for reliable categorization.
-   **Batch Categorization**: Categorizes multiple inputs simultaneously for
    token savings

## Attributes

-   `categories` (Dict[str, str]): A dictionary mapping category names to their
    descriptions. This structure allows for a clear definition of possible
    categories for classification.
-   `llm_provider` (LLMProvider): An instance of an LLM provider to be used for
    categorization.
-   `examples` (Optional[List[Dict[str, str]]]): A list of example inputs and
    their corresponding categories to improve categorization accuracy.

## Computed Fields

-   `system_message` (str): A system message used for single input
    categorization based on the provided categories and examples.
-   `system_message_batch` (str): A system message used for batch input

## Methods

### `categorize`

Categorizes the input data using the specified LLM provider.

#### Arguments

-   `input_data` (str): The text data to be categorized.

#### Returns

-   `str`: The predicted category for the input data.

#### Raises

-   `ValueError`: If the predicted category is not one of the provided
    categories.

### `categorize_batch`

Categorizes a batch of input data using the specified LLM provider. For less
advanced LLMs, call this method on batches of 3-5 inputs (depending on the
length of the input data).

#### Arguments

-   `input_data` (List[str]): A list of text data to be categorized.

#### Returns

-   `List[str]`: A list of predicted categories for the input data.

#### Raises

-   `ValueError`: If the predicted categories are not a subset of the provided
    categories or if the number of predicted categories does not match the
    number of input data.

## Usage

Setup the LLM provider and categories (as a dictionary):

```python
from databonsai.categorize import BaseCategorizer
from databonsai.llm_providers import OpenAIProvider, AnthropicProvider

provider = OpenAIProvider()  # Or AnthropicProvider()
categories = {
   "Weather": "Insights and remarks about weather conditions.",
   "Sports": "Observations and comments on sports events.",
   "Celebrities": "Celebrity sightings and gossip",
   "Others": "Comments do not fit into any of the above categories",
   "Anomaly": "Data that does not look like comments or natural language",
}
```

Categorize your data:

```python
categorizer = BaseCategorizer(
    categories=categories,
    llm_provider=provider,
)
category = categorizer.categorize("It's been raining outside all day")
print(category)
```

Output:

```python
Weather
```

Categorize a few inputs:

```python
categories = categorizer.categorize([
    "Storm Delays Government Budget Meeting, Weather and Politics Clash",
    "Olympic Star's Controversial Tweets Ignite Political Debate, Sports Meets Politics",
    "Local Football Hero Opens New Gym, Sports and Business Combine"])
print(categories)
```

Output:

```python
['Weather', 'Sports', 'Celebrities']
```

Categorize a list of inputs (Use shorter lists for weaker LLMs):

```python
headlines = [
    "Massive Blizzard Hits the Northeast, Thousands Without Power",
    "Local High School Basketball Team Wins State Championship After Dramatic Final",
    "Celebrated Actor Launches New Environmental Awareness Campaign",
    "President Announces Comprehensive Plan to Combat Cybersecurity Threats",
    "Tech Giant Unveils Revolutionary Quantum Computer",
    "Tropical Storm Alina Strengthens to Hurricane as It Approaches the Coast",
    "Olympic Gold Medalist Announces Retirement, Plans Coaching Career",
    "Film Industry Legends Team Up for Blockbuster Biopic",
    "Government Proposes Sweeping Reforms in Public Health Sector",
    "Startup Develops App That Predicts Traffic Patterns Using AI",
]
categories = categorizer.categorize_batch(headlines)
print(categories)
```

Output:

```python
['Weather', 'Sports', 'Celebrities', 'Politics', 'Tech', 'Weather', 'Sports', 'Celebrities', 'Politics', 'Tech']
```

Categorize a long list of inputs, or a dataframe column:

```python
from databonsai.utils import apply_to_column_batch, apply_to_column

categories = []
success_idx = apply_to_column_batch(headlines, categories, categorizer.categorize, 3, 0)
```

Without batching:

```python
categories = []
success_idx = apply_to_column(headlines, categories, categorizer.categorize)
```
