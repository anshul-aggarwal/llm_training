# Training for LLMs, August 2023

## Getting started

### Setting up OpenAI access

Create a file with the name `.env` and set your enviornment variables. You can copy the `.env.sample` file, rename it to `.env` and then add the requisite values there.

### Dependencies

Install (in a virtual environment) dependencies in `requirements.txt` by running `pip install -r requirements.txt`.

### Learning through notebooks

You can start working through the notebooks in the `notebooks` directory in order by running `jupyter notebook` in the root directory, or using VS code

### Running an end-to-end demo

You can also run an end-to-end demo by:
1. Go to the `backend` directory in a terminal, and run `python main.py`
2. In a separate terminal, go to the `frontend` directory, and run `streamlit run main.py`

Make sure in both cases the virtual environment is active.