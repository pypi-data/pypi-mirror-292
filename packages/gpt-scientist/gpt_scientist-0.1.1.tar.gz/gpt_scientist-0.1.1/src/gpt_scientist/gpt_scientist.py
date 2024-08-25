"""Main module."""

import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import json
import tiktoken
import logging
from gpt_scientist.google_doc_parser import convert_to_markdown

# Check if we are in Google Colab, and if so authenticate and import libraries to work with Google Sheets
try:
    from google.colab import auth
    IN_COLAB = True
    import gspread
    from google.auth import default
    from googleapiclient.discovery import build
    auth.authenticate_user()
except ImportError:
    IN_COLAB = False


class Scientist:
    '''Configuration class for the GPT Scientist.'''
    def __init__(self, api_key: str = None):
        '''
            Initialize configuration parameters.
            If no API key is provided, the key is read from the .env file.
        '''
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            load_dotenv()
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = 'gpt-4o' # Default model
        self.system_prompt = 'You are a social scientist analyzing textual data.' # Default system prompt
        self.num_results = 1 # How many completions to generate at once? The first valid completion will be used.
        self.num_reties = 10 # How many times to retry the request if no valid completion is generated?
        self.max_tokens = 2048 # Maximum number of tokens to generate
        self.top_p = 0.3 # Top p parameter for nucleus sampling (this value is quite low, preferring more deterministic completions)
        self.checkpoint_file = None # File to save the dataframe after every row is processed
        self.output_sheet = 'gpt_output' # Name (prefix) of the worksheet to save the output in Google Sheets
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def set_model(self, model: str):
        '''Set the model to use for the GPT Scientist.'''
        self.model = model

    def set_num_results(self, num_completions: int):
        '''Set the number of results to generate at once.'''
        self.num_results = num_completions

    def set_num_retries(self, num_retries: int):
        '''Set the number of retries if no valid completion is generated.'''
        self.num_reties = num_retries

    def set_system_prompt(self, system_prompt: str):
        '''Set the system prompt to use for the GPT Scientist.'''
        self.system_prompt = system_prompt

    def load_system_prompt_from_file(self, path: str):
        '''Load the system prompt from a file.'''
        with open(path, 'r') as f:
            self.system_prompt = f.read()

    def load_system_prompt_from_google_doc(self, doc_id: str):
        '''Load the system prompt from a Google Doc.'''
        if not IN_COLAB:
            self.logger.error("This method is only available in Google Colab.")
            return

        creds, _ = default()
        service = build('docs', 'v1', credentials=creds)
        doc = service.documents().get(documentId=doc_id).execute()
        self.system_prompt = convert_to_markdown(doc['body']['content'])

    def set_max_tokens(self, max_tokens: int):
        '''Set the maximum number of tokens to generate.'''
        self.max_tokens = max_tokens

    def set_top_p(self, top_p: float):
        '''Set the top p parameter for nucleus sampling.'''
        self.top_p = top_p

    def set_checkpoint_file(self, checkpoint_file: str):
        '''Set the file to save the dataframe after every row is processed.'''
        self.checkpoint_file = checkpoint_file

    def set_output_sheet(self, output_sheet: str):
        '''Set the name (prefix) of the worksheet to save the output in Google Sheets.'''
        self.output_sheet = output_sheet

    def token_count(self, prompt: str) -> int:
        '''Return the number of tokens in the prompt.'''
        tokenizer = tiktoken.encoding_for_model(self.model)
        return len(tokenizer.encode(prompt))

    def _prompt_model(self, prompt: str):
        return self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                n=self.num_results,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"},
                top_p=self.top_p,
            )

    def _parse_response(self, completion: str) -> dict:
        '''Parse model completion into a dictionary.'''
        try:
            return json.loads(completion)
        except json.JSONDecodeError as _:
            return None

    def get_response(self, prompt: str) -> dict:
        '''
            Prompt the model until we get a valid json completion.
            Return None if no valid completion is generated after scientist.num_reties attempts.
        '''
        for attempt in range(self.num_reties):
            if attempt > 0:
                self.logger.error(f"Attempt {attempt + 1}")
            completions = self._prompt_model(prompt)

            for i in range(self.num_results):
                response = self._parse_response(completions.choices[i].message.content.strip())
                if response is None:
                    # Log the bad response
                    self.logger.error(f"Bad response: {completions.choices[i].message.content.strip()}")
                    continue
                return response

    def _input_fields_and_values(self, fields: list[str], row: pd.Series) -> str:
        '''Format the input fields and values for the prompt.'''
        return '\n\n'.join([f"{field}:\n```\n{row[field]}\n```" for field in fields])

    def _format_suffix(self, fields: list[str]) -> str:
        '''Suffix added to the prompt to explain the expected format of the response.'''
        return f"Your response must be a json object with the following fields: {', '.join(fields)}. The response must start with {{, not with ```json."

    def analyze_data(self,
                     data: pd.DataFrame,
                     prompt_prefix: str,
                     input_fields: list[str],
                     output_fields: list[str]) -> pd.DataFrame:
        '''
            Analyze a pandas dataframe:
            for every value in the input_field column,
            create a prompt by concatenating prompt_prefix, names and values of input fields,
            and a suffix explaining the expected format of the response;
            parse output_fields from the response and add them as new columns to the dataframe.
            If checkpoint_file is provided, progress is saved there and restored from there.
        '''
        # Copy the dataframe to avoid modifying the original data
        data = data.copy()

        start_from = 0
        if self.checkpoint_file and os.path.exists(self.checkpoint_file):
            # Check if the checkpoint file has the same columns as the dataframe + output_fields
            checkpoint_data = pd.read_csv(self.checkpoint_file)
            if not set(data.columns).issubset(checkpoint_data.columns) or not set(output_fields).issubset(checkpoint_data.columns):
                self.logger.warning(f"Checkpoint file {self.checkpoint_file} does not have the same columns as the dataframe and will be overwritten.")
                os.remove(self.checkpoint_file)
            else:
                # Merge the checkpoint data with the dataframe and start from the last row
                self.logger.info(f"Found {len(checkpoint_data)}/{len(data)} rows in the checkpoint file.")
                data = pd.merge(data, checkpoint_data, on=list(data.columns), how='left')
                start_from = len(checkpoint_data)

        # Process every row in the dataframe
        for i, row in data.iterrows():
            if i < start_from:
                continue
            self.logger.info(f"Processing row {i}")
            prompt = f"{prompt_prefix}\n{self._input_fields_and_values(input_fields, row)}\n{self._format_suffix(output_fields)}"
            response = self.get_response(prompt)
            if response is None:
                self.logger.error(f"No valid response for input: {input}")
                continue
            for field in output_fields:
                data.at[i, field] = response[field]
            if self.checkpoint_file:
                # Append the row to the checkpoint file
                data.loc[[i]].to_csv(self.checkpoint_file, mode='a', header=(i == 0), index=False)
        return data

    def analyze_csv(self,
                    path: str,
                    prompt_prefix: str,
                    input_fields: list[str],
                    output_fields: list[str],
                    output_path: str = None):
        '''
            Load a csv file, analyze it, and save the results back to the file.
            If output_path is provided, save the results to this file instead.
        '''
        data = pd.read_csv(path)
        data = self.analyze_data(data, prompt_prefix, input_fields, output_fields)
        if output_path:
            data.to_csv(output_path, index=False)
        else:
            data.to_csv(path, index=False)

    def _create_output_sheet(self, spreadsheet):
        '''Create a new worksheet in the spreadsheet to save the output, avoiding name conflicts.'''
        worksheet_list = spreadsheet.worksheets()
        worksheet_names = [worksheet.title for worksheet in worksheet_list]
        if self.output_sheet in worksheet_names:
            i = 1
            while f"{self.output_sheet}_{i}" in worksheet_names:
                i += 1
            return spreadsheet.add_worksheet(title=f"{self.output_sheet}_{i}", rows=1, cols=1)
        else:
            return spreadsheet.add_worksheet(title=self.output_sheet, rows=1, cols=1)

    def analyze_google_sheet(self,
                             sheet_key: str,
                             prompt_prefix: str,
                             input_fields: list[str],
                             output_fields: list[str],
                             in_place: bool = True,
                             worksheet_index: int = 0):
        '''
            When in Colab: analyze data in the Google Sheet with key `sheet_key`; the user must have write access to the sheet.
            Use `worksheet_index` to specify a sheet other than the first one.
            If `in_place` is True, the input sheet will be extended with the output data; otherwise a new sheet will be created.
        '''
        if not IN_COLAB:
            self.logger.error("This method is only available in Google Colab.")
            return
        creds, _ = default()
        gc = gspread.authorize(creds)

        spreadsheet = gc.open_by_key(sheet_key)
        worksheet = spreadsheet.get_worksheet(worksheet_index)
        data = worksheet.get_all_records()
        data = pd.DataFrame(data)
        num_input_columns = len(data.columns)

        data = self.analyze_data(data, prompt_prefix, input_fields, output_fields)

        if in_place:
            first_output_column = chr(ord('A') + num_input_columns)
            last_output_column = chr(ord('A') + num_input_columns + len(output_fields) - 1)
            output_range = f"{first_output_column}:{last_output_column}"
            worksheet.update([output_fields] + data[output_fields].values.tolist(), range_name=output_range)
        else:
            out_worksheet = self._create_output_sheet(spreadsheet)
            out_worksheet.update([data.columns.values.tolist()] + data.values.tolist())
