import openai
import json
import os
from configLoader import load_config
from setupLogger import setup_logger

logger = setup_logger(__name__, f"logs/stockAnalyzer.log")

openai.api_key = load_config("openAIKey")

def generate_report(ticker, name, df, prompt_template):
    """
    Generates a report on base of the prompt.

    Args:
        ticker (str): Der Ticker der Aktie oder des ETF.
        name (str): Der Name des Titels.
        df (pd.DataFrame): Der zu analysierende DataFrame.
        prompt_template (str): Ein Prompt mit Platzhaltern für {ticker}, {name}, {data_json}.

    Returns:
        str: Die von GPT erzeugte Antwort.
    """
    try:
        summary_data = df.tail(5).to_dict()
        data_json = json.dumps(summary_data, indent=2)

        # Platzhalter im Prompt ersetzen
        prompt = prompt_template.format(ticker=ticker, name=name, data_json=data_json)

        logger.debug(f"Sending prompt to OpenAI:\n{prompt[:10]}...")  # Nur die ersten 500 Zeichen loggen

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        return response['choices'][0]['message']['content']

    except Exception as e:
        logger.error(f"Fehler beim Generieren des Berichts: {e}")
        return f"Fehler beim Generieren des Berichts: {e}"
