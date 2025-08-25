# Blackjack Bot
Blackjack telegram bot on Python

## Continue developing
1. Create venv
```bash
python -m venv venv
```
2. Install dependencies
```bash
pip install -r "requirements.txt"
pip install -r "requirements-dev.txt"
```
3. Initialize pre-commit locally
```bash
pre-commit install
```
4. Run bot from project root
```bash
python3 -m bot.main
```
5. Run db in container
```bash
docker compose up -d
```
