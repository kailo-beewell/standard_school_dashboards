# 🐝 Standard school dashboards

Dashboards for schools who completed the standard #BeeWell survey in 2023/24. 🏫

These are created using completely random synthetic data, so this repository is public, as it contains no project data. The prototypes will be used to create official dashboards using actual school data after data collection.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://beewell-kailo-standard-school-dashboard-prototype.streamlit.app/)

Streamlit Community Cloud only appears to work with virtual environment (states compatability with environment.yml but failed), so we use a virtual environment with the requirements.txt file provided and python version 3.9.12 (with community cloud set up on python 3.9). To set up environment, need pip + python + virtualenv installed, then run:
* Create environment - `virtualenv kailo_dashboards`
* Enter environment -  `source kailo_dashboards/bin/activate`
* Install requirements into environment - `pip install -r requirements.txt`

Manage streamlit apps here: https://share.streamlit.io/