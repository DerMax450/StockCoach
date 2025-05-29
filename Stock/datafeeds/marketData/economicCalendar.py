import csv
from datetime import datetime
from typing import List
from services.setupLogger import setup_logger
from bs4 import BeautifulSoup
import requests
import datetime
import logging
import csv

logger = setup_logger(__name__, f"logs/stockAnalyzer.log")

from jb_news.news import CJBNews

class JBNewsHelper:
    def __init__(self, api_key: str, offset: int = 7):
        self.api_key = api_key
        self.jb = CJBNews()
        self.jb.offset = offset
    
    def connect(self) -> bool:
        """Verbindet sich mit der API und gibt True bei Erfolg zurück."""
        return self.jb.get(self.api_key)
    
    def get_event_info(self, event_id: int) -> dict:
        """
        Lädt die Event-Infos und gibt sie als Dictionary zurück.
        """
        if not self.connect():
            raise Exception("API-Verbindung fehlgeschlagen")
        if self.jb.load(event_id):
            info = self.jb.info
            return {
                "name": info.name,
                "currency": info.currency,
                "event_id": info.event_id,
                "history": info.history,
                "category": info.category,
                "machine_learning": info.machine_learning,
                "smart_analysis": info.smart_analysis,
            }
        else:
            logger.error(f"Fehler: {e}")
    
    def get_calendar(self, today: bool = True) -> list:
        """
        Loads the calendar for today (or overall) and returns a list of events as dictionaries.
        """
        try:
            if self.jb.calendar(self.api_key, today=today):
                events = []
                for event in self.jb.calendar_info:
                    events.append({
                        "name": event.name,
                        "currency": event.currency,
                        "event_id": event.event_id,
                        "category": event.category,
                        "date": event.date,
                        "actual": event.actual,
                        "forecast": event.forecast,
                        "previous": event.previous,
                        "outcome": event.outcome,
                        "strength": event.strength,
                        "quality": event.quality,
                        "projection": event.projection,
                    })
                return events
            else:
                raise Exception("Calendar could not be loaded")
        except Exception as e:
            logger.error(f"Fehler: {e}")
            
    def ask_gpt(self, prompt: str) -> str:
        """
        Asks the NewsGPT model and returns the response as a string.
        """
        return self.jb.GPT(self.api_key, prompt)
