import random
import re

import Core_ConfigInterpreter as cc

'''
A class that is used to build a knowledge base on a likelihood.
'''
class Individual:

    # The constructor, setting class variables for each individual
    def __init__(self, text=[], name=None, impact=cc.Config().get_default_impact("core_config.json")):
        # A score of this individuals liklihood
        self._liklihood = None
        # Name of the individual
        self.name = name
        # A list used to hold the text that will be profiled
        self._text_to_be_profiled = []

        self.add_text_to_be_profiled(text)

        # Sets the impact of the individual, default is 1
        self.impact = impact

    def get_liklihood(self):
        assert self._liklihood is not None, " Liklihood has not been set."
        return self._liklihood

    # A method used to add text to the aformentioned list
    def add_text_to_be_profiled(self, text):

        if type(text) is list:
            self._text_to_be_profiled.extend(text)
        else:
            self._text_to_be_profiled.append(text)

    # A method used to remove text from the aformentioned list
    def remove_from__text_to_be_profiled(self, text):
        self._text_to_be_profiled.remove(text)

    # A method that generates a psudo random name for the individual
    def generate_name(self, filename="Core_wordfile", words_in_name=3):
        list_of_words = []

        file = open(filename, "r")
        for line in file:
            list_of_words.append(line.strip("\n"))

        for iterator in range(words_in_name):
            random_number = random.randint(0, len(list_of_words))
            self.name = self.name + list_of_words[random_number - 1] + "//"


    def detect (self):
        list_of_detectors = []

        # Adds the Relationship Detector to be used when profiling
        from Liklihood_Detectors import Relationship_Detection as rd
        relationship_profile = rd.Relationship_Detection()
        list_of_detectors.append(relationship_profile)

        # Adds the goal detector to be used when profiling
        from Liklihood_Detectors import Goal_Detection as gd
        goal_profile = gd.Goal_Detection()
        list_of_detectors.append(goal_profile)

        # Adds the goal detector to be used when profiling
        from Liklihood_Detectors import Location_Detection as ld
        location_profile = ld.Location_Detection()
        list_of_detectors.append(location_profile)

        # Adds the url recognition
        from Liklihood_Detectors import url_recognition as ur
        url_recognition = ur.Url_Recognition()
        list_of_detectors.append(url_recognition)

        #Adds the Blacklist recognition
        from Liklihood_Detectors import blacklist_recognition as br
        blacklist_recognition = br.Blacklist_Recognition()
        list_of_detectors.append(blacklist_recognition)

        return list_of_detectors

    # Uses the detectors to calculate a risk score for the individual
    def profile(self):
        assert self._text_to_be_profiled, "List of text to be profiled is empty"

        list_of_detectors = self.detect()

        total_scores = []
        total = 0

        list_of_extra_info = []
        # Loops through all of the detectors

        # I have no idea why this tmp is needed (maybe a pointer problem) but everything breaks without it.
        tmp_text = self._text_to_be_profiled

        #Sets a list to be equal to the detectors set in the config.
        list_of_detectors_in_config = cc.Config().get_list_of_in_use_detectors("core_config.json")
        for detector in list_of_detectors:
            #Only runs the detectors that are set in the config
            if detector.detector_name in list_of_detectors_in_config:
                print("Detector run " + detector.detector_name)
                # Removes null items in list
                self._text_to_be_profiled = filter(None, self._text_to_be_profiled)

                self._text_to_be_profiled = tmp_text
                # Loops through the list of text to be profiled, profiling each, and then calculating an average
                for text in self._text_to_be_profiled:
                    if text:
                        dictionary_of_scan_results = detector.get_score(text)
                        list_of_extra_info.append(dictionary_of_scan_results)

                        # Checks if the likelihood field exists and if so uses it towards the total.
                        if "likelihood" in dictionary_of_scan_results.keys():
                            total_scores.append(dictionary_of_scan_results["likelihood"])
            else:
                print("Detector not run " + detector.detector_name)

        for number in total_scores:
            total = total + number
        average = total / len(total_scores)
        self._liklihood = average

        assert self.impact, "No impact set to the individual."
        assert self._liklihood, "No likelihood set for the individual."
        assert self.name, "No name set for the individual."

        # Adds items to a dictionary so that they can be returned to the main script
        # The round function sets the decimal place to 2.
        dictionary_for_individual = {}
        dictionary_for_individual["likelihood"] = round(self._liklihood, 2)
        dictionary_for_individual["impact"] = round(self.impact, 2)
        dictionary_for_individual["extra"] = list_of_extra_info
        dictionary_for_individual["name"] = self.name
        dictionary_for_individual["risk"] = round(self.impact * self._liklihood, 2)

        return dictionary_for_individual
