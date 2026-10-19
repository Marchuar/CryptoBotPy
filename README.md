# CryptoBotPy

Lernprojekt: Ein Telegram-Bot in Python, der Kryptomärkte der Börse Bybit mit technischen Indikatoren analysiert und Abonnenten benachrichtigt, wenn eine Strategie ein Signal erzeugt. Das Projekt dient nur dem Programmieren und der Datenanalyse und ist **keine Anlageberatung**.

## Funktionen
- Marktdaten über `ccxt` (Bybit)
- Indikatoren: EMA, MACD, RSI, ADX, CCI, ATR, Bollinger-Bänder, Parabolic SAR, CVD
- Strategien mit Bewertung der Signale, auswählbare Zeitrahmen von 15 Minuten bis 1 Tag
- Backtesting mit CSV-Daten und mit historischen Daten der Börse
- Telegram-Bot (aiogram) zum Abonnieren, Abbestellen und Einstellen des Zeitrahmens
- Speicherung der Abonnenten in PostgreSQL
- Docker-Image

## Technik
Python 3.11, aiogram, ccxt, TA-Lib, pandas, NumPy, PostgreSQL (psycopg2), Docker

## Einrichten
Datei `deapp/.env` anlegen (nicht committen):
