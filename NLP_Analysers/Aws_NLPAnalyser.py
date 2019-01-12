import subprocess as sp
import json

'''
A class used to interact with the AWS Comprehend api and 
to perform NLP on text.
'''
class AWSComprehend:

    # A list of the current NLP detect commands.
    list_of_detect_commands = [
    "detect-sentiment",
    "detect-entities",
    "detect-dominant-language",
    "detect-key-phrases",
    "detect-syntax"]

    #A function that takes a 'command' list, executes it and converts the output to json
    def _run_aws_comprehend(self, command):
        assert "aws" in command, "AWS Comprehend command not run."
        raw_output = sp.Popen(command, stdout=sp.PIPE, shell=True)
        raw_output = raw_output.communicate()[0]
        utf8_output = str(raw_output, 'utf-8')
        json_output = json.loads(utf8_output)

        return json_output

    #A function used to construct a list for a command out of the type of command, the text and the language.
    def construct_detect_command(self, task, text, language = "en"):
        #Check if used task is in list of known aws comprehend detect commands
        assert task in self.list_of_detect_commands, task + " not in list of known detect commands: " + str(self.list_of_detect_commands)
        command_list = ['aws', 'comprehend', task, '--text', text, "--language-code", language]
        return self._run_aws_comprehend(command_list)