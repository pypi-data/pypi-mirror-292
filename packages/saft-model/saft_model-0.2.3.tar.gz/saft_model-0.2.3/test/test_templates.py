
import pytest

# def test_single_word():
#     assert format_proper_name_to_pascal_case('hello') == 'Hello'

# def test_multiple_words():
#     assert format_proper_name_to_pascal_case('this_is_a_test') == 'ThisIsATest'

# def test_leading_and_trailing_underscores():
#     assert format_proper_name_to_pascal_case('-leading-and-trailing-') == 'LeadingAndTrailing'


# def test_multiple_words():
#     assert format_proper_name_to_pascal_case('this_is_a_test') == 'ThisIsATest'

# def test_leading_and_trailing_underscores():
#     assert format_proper_name_to_pascal_case('_leading_and_trailing_') == 'LeadingAndTrailing'


# def test_empty_string():
#     assert format_proper_name_to_pascal_case('') == ''

# def test_string_with_only_underscores():
#     assert format_proper_name_to_pascal_case('___') == ''

# def test_mixed_case_input():
#     assert format_proper_name_to_pascal_case('hElLo_WoRLd') == 'HelloWorld'

# def test_already_pascal_case():
#     assert format_proper_name_to_pascal_case('AlreadyPascalCase') == 'AlreadyPascalCase'  # Depending on desired behavior

# def test_special_characters():
#     assert format_proper_name_to_pascal_case('hello$world') == 'Hello$world'
#     assert format_proper_name_to_pascal_case('hello_world!') == 'HelloWorld!'

# def test_numerics_in_string():
#     assert format_proper_name_to_pascal_case('hello2world') == 'Hello2world'
#     assert format_proper_name_to_pascal_case('hello_world_123') == 'HelloWorld123'