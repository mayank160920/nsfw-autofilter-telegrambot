# NSFW Auto Filter Telegram Bot
I've used the a pretraiend model for detecting nsfw contents that is avaiable in  repository.

## How to run project
1. Install Python v3.6
2. Install virtualenv
```bash
pip insatll virtualenv
```
3. Create a virtual environment:
```bash
virtualenv venv
```
4. Active the virtual environment (On Linux):
```bash
source venv/bin/activate
```
5. Install all the requirements by using this command:
```bash
pip install -r requirements.txt
```
6. Download the model from [here](https://github.com/bedapudi6788/NudeNet/releases/download/v0/classifier_model) and put it in a folder like `models`.
7. Move and rename `config.py.sample` to `ndproject/config.py` and do proper changes.
8. Do migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```
6. Run project:
```bash
python manage.py runserver
```
