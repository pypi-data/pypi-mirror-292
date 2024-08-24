import openai
import spacy
from transformers import pipeline


class ContextualGenerator:
    """
    Class for generating dataset from a given context. Uses NLP models for tasks
    like text generation and analysis.
    """

    def __init__(self, api_key=None):
        self.nlp = spacy.load('en_core_web_sm')
        self.generator = pipeline('text-generation', model='llama-3b')
        self.api_key = api_key
        if self.api_key:
            openai.api_key = self.api_key


    def generate_detailed_context(self, context):
        """
        Generates detailed context from a given context using LLaMA 3.

        Parameters
        ----------
        context: str
            Basic context

        Returns
        -------
        str
            Detailed context generated

        Raises
        ------
        RuntimeError
            If an error occurs during text generation
        """
        try:
            prompt = f"{context}: Generate a detailed context with columns, their types, and potential constraints."
            result = self.generator(prompt, max_length=200, num_return_sequences=1)
            return result[0]['generated_text']
        except Exception as e:
            raise RuntimeError(f"Error while generating the text : {e}")


    def premium_analyze_context(self, context):
        """
        Parses a context using OpenAI GPT-3 to generate a list of columns with their types and constraints.

        Parameters
        ----------
        context: str
            Context to analyze

        Returns
        -------
        list
            List of dictionaries representing columns

        Raises
        ------
        RuntimeError
            If an error occurs while scanning with GPT-3
        """
        try:
            pre_prompt = (
                "Given the context, generate a list of columns for this dataset, each represented as a dictionary with "
                "the keys: 'name', 'type', and 'constraints' and 'fair' set by default to false unless the context precises it for the column."
                f"\nContext: {context}\n"
                "The output should be a Python list of dictionaries."
            )
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=pre_prompt,
                max_tokens=150,
                n=1,
                stop=None,
                temperature=0.5
            )
            return eval(response.choices[0].text.strip())
        except Exception as e:
            raise RuntimeError(f"Error during analysis with GPT-3  : {e}")
   
   
    def standard_analyze_description(self, description):
        """
        Analyzes a description to identify columns, their types, and their constraints using Spacy.

        Parameters
        ----------
        description: str
            Description to analyze

        Returns
        -------
        list
            List of dictionaries representing columns

        Raises
        ------
        RuntimeError
            If an error occurs while parsing the description
        """
        try:
            doc = self.nlp(description)
            columns = []

            for ent in doc.ents:
                if ent.label_ == 'COLUMN':  # Cette partie reste à parfaire
                    column_info = {
                        'name': ent.text,
                        'type': None,
                        'constraints': [],
                        'fair': False
                    }

                    for token in ent.root.head.subtree:
                        if token.dep_ == 'amod' and token.head == ent.root:
                            column_info['type'] = token.text
                        if token.dep_ in ['acl', 'relcl'] and token.head == ent.root:
                            column_info['constraints'].append(token.text)

                    columns.append(column_info)

            return columns
        except Exception as e:
            raise RuntimeError(f"Error when analyzing description : {e}")


    def generate_column_info(self, context):
        """
        Generates column information from a given context, depending on whether an API key is provided.

        Parameters
        ----------
        context: str
            Basic context

        Returns
        -------
        list
            List of dictionaries representing columns

        Raises
        ------
        ValueError
            If detailed context generation fails
        """
        if self.api_key:
            column_info = self.premium_analyze_context(context)
        else:
            detailed_context = self.generate_detailed_context(context)
            if not detailed_context:
                raise ValueError("Detailed context generation failed.")
            column_info = self.standard_analyze_description(detailed_context)

        return column_info


    def generate(self, column_info):
        """
        Placeholder for a method of generating data from information
        on the columns. This method should be implemented.

        Parameters
        ----------
        column_info: list
            Information about columns to use for data generation

        Returns
        -------
        list
            The dataset generated
        """
        return []


def generate_contextual_data(context, api_key=None):
    """
        External method to generate column information from context.

        Parameters
        ----------
        context: str
            Context to analyze
        api_key: str, optional
            API key for OpenAI GPT-3 if premium generation is required

        Returns
        -------
        list
            List of column information generated
    """
    generator = ContextualGenerator(api_key=api_key)
    column_info = generator.generate_column_info(context)
    data = generator.generate(column_info)
    
    return data
