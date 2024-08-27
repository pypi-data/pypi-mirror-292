

import pytest 

from saft_model.Sentiment import Sentiment

def test_value_of_success():
    example_sentiment = "neUTRal"
    converted_sentiment = Sentiment.value_of(example_sentiment)
    assert Sentiment.NEUTRAL == converted_sentiment

def test_value_of_error():
    example_incorrect_sentiment = "TO THE MOON" 
    with pytest.raises(ValueError) as e_info:
        converted_sentiment = Sentiment.value_of(example_incorrect_sentiment)