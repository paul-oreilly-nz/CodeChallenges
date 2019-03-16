#!/bin/python3

#
# Our PM ask us to create a function for password validation
# Some of the validation rules are the following:
# - Password cannot be less than 8 characters
# - Password cannot be greater than 20 characters
# - Password must have, at least, one capital letter
# - Password must have, at least, one number
# - Password must have, at least, one special character from this list !@#$%^&*
# The following is our first solution
#

import unittest
import string

# A lazy altervative to using logging...
debug = False

# Validation classes
class Validator:
    next_in_chain = None
    name = "Generic Validator"

    def validate(self, data):
        """ Calling this function will check the data provided against this validator and 
            any validators chained to it. It will then return an overall pass or fail, and
            a list of results of what each validator found """
        overall_success = True
        results = []
        # debug
        if debug:
            print("Calling test {}".format(str(self)))
        # if data appears valid, then validate and get a result for that data
        if data is not None and len(data) > 0:
            success, outcome = self.get_result(data)
            # results may return multiple result records, or could be just the one
            if type(outcome) is list:
                for out in outcome:
                    results.append(out)
                    if not success:
                        overall_success = False
            else:
                results.append(outcome)
                if not success:
                    overall_success = False
        # if another validator has been added for a chained call, call that validator
        if self.next_in_chain is not None:
            chain_success, chain_results = self.next_in_chain.validate(data)
            # add the results to our own list
            if chain_results is not None and len(chain_results):
                for result in chain_results:
                    results.append(result)
            if chain_success is not True:
                overall_success = False
        # Return the overall result
        return overall_success, results

    def chain(self, validator):
        """ Adds the given validator to the end of the chain, and returns this object """
        # We want to return this object so a chained assignment gets the top of the chain,
        # not the bottom.
        last = self
        while last.next_in_chain is not None:
            last = last.next_in_chain
        if debug:
            print("{} is linking validator {} to {}".format(self, validator, last))
        last.next_in_chain = validator
        return self

    def __add__(self, validator):
        # Syntex sugar - allow "Validator + Validator + Validator..." to define the chain
        return self.chain(validator)

    def __str__(self):
        return self.name

    def chain_string(self):
        if self.next_in_chain is not None:
            return "{} -> {}".format(self, self.next_in_chain.chain_string())
        else:
            return str(self)

    def get_result(self, data):
        """ Reurns either a single result in the form {success:bool, name:string, text:string} or
            a list with one or more result enteries matching the above """
        return {"success": True, "name": "Undefined", "text": "Undefined test"}


class CheckLength(Validator):
    """ Checks that a data string is at least a min length, and no greater than a max length"""

    def __init__(self, min_length=0, max_length=0, name="Length Check"):
        """ A value of 0 for either min_length or max_length will disable that check """
        self.min_length = min_length
        self.max_length = max_length
        self.name = name

    def get_result(self, data):
        results = []
        success = True
        if self.min_length > 0 and len(data) < self.min_length:
            results.append(
                {
                    "success": False,
                    "name": self.name,
                    "text": "Password must be at least {} characters long".format(
                        self.min_length
                    ),
                }
            )
            success = False
        else:
            results.append(
                {
                    "success": True,
                    "name": self.name,
                    "text": "Password is at least {} characters long".format(
                        self.min_length
                    ),
                }
            )
        if self.max_length > 0 and len(data) > self.max_length:
            results.append(
                {
                    "success": False,
                    "name": self.name,
                    "text": "Password must not be longer than {} characters".format(
                        self.max_length
                    ),
                }
            )
            success = False
        else:
            results.append(
                {
                    "success": True,
                    "name": self.name,
                    "text": "Password is no longer than {} characters".format(
                        self.max_length
                    ),
                }
            )
            # Return the results
        return success, results


class CheckIncludesCharacters(Validator):
    """ Checks that a data string includes at least [count] characters from a given string """

    def __init__(self, must_include, name="Character Check", count=1):
        self.must_include = must_include
        self.name = name
        self.count = count

    def get_result(self, data):
        success = sum(data.count(char) for char in self.must_include) >= self.count
        if success:
            return (
                True,
                {
                    "success": True,
                    "name": self.name,
                    "text": "Password contains at least {} from the characters {}".format(
                        self.count, self.must_include
                    ),
                },
            )
        else:
            return (
                False,
                {
                    "success": False,
                    "name": self.name,
                    "text": "Password did not contain at least {} characters from the set {}".format(
                        self.count, self.must_include
                    ),
                },
            )

            # Replaced password validation check function


def is_password_valid(password):
    # build the chain
    validation_chain = (
        CheckLength(min_length=8, max_length=20, name="LENGTH")
        + CheckIncludesCharacters(must_include=string.ascii_uppercase, name="CAPTIAL")
        + CheckIncludesCharacters(must_include=string.digits, name="NUMBER")
        + CheckIncludesCharacters(must_include="!@#$%^&*", name="SPECIAL CHAR")
    )
    # validate and collect results
    success, result_items = validation_chain.validate(password)
    # debug / verbose output
    if debug:
        print(validation_chain.chain_string)
        print("Testing password {}".format(password))
        for item in result_items:
            item["success_string"] = "PASSED" if item["success"] else "FAILED"
            print("  {success_string} - {name}: {text}".format(**item))
    # return result
    return success


class IsPasswordValidTest(unittest.TestCase):
    # To run tests issue `python -m unittest myNestedValidator.IsPasswordValidTest` in MyShinyChain folder.
    # Or uncomment the last line.
    def test_proper(self):
        self.assertEqual(is_password_valid("Abcdefa4!"), True)

    def test_too_short(self):
        self.assertEqual(is_password_valid("Abcdefa4"), False)

    def test_too_long(self):
        self.assertEqual(is_password_valid("Abcdefa4abcdefghijklmnopqrstuvwxyz"), False)

    def test_no_capitals(self):
        self.assertEqual(is_password_valid("Abcdefaa!"), False)

    def test_no_numbers(self):
        self.assertEqual(is_password_valid("abcdefa4!"), False)

    def test_no_special_characters(self):
        self.assertEqual(is_password_valid("Abcdefa4a"), False)


if __name__ == "__main__":
    print(is_password_valid("Abcdefa4!"))
    print(is_password_valid("Abcdefa4"))
    print(is_password_valid("Abcdefa4abcdefghijklmnopqrstuvwxyz"))
    print(is_password_valid("Abcdefaa!"))
    print(is_password_valid("abcdefa4!"))
    print(is_password_valid("Abcdefa4a"))
    # unittest.main()


#
# The PM now is asking us to reuse the password validator function
# in other part of the solution, but without applying max length restriction
# additionally, we will need to include another rule that must apply only
# for this call, but that functionality will be provided later.
#
# HINT: There is a design pattern called "chain of responsibility" that could
# fit perfectly for this case. Try to apply it.
#
