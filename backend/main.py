import json

import uvicorn
from fastapi import FastAPI

from logic import initialise, query_llm

app = FastAPI()

retriever = initialise()


@app.get("/")
def read_root():
    return {"content": "Hello World"}


def search_movie(query, session_id):
    movies = retriever.get_relevant_documents(query=query)

    if len(movies) == 0:
        return {
            "content": "Hey there! Unfortunately I did not find any Nolan movie relevant to your query.",
            "metadata": {"session_id": session_id, "type": "UNHANDLED"},
        }
    else:
        top_movie = movies[0]
        top_movie_file = top_movie.metadata["source"]
        top_movie_name = top_movie_file.split("\\")[-1].split(".")[0]

        return {
            "content": f"I found the movie *{top_movie_name}* most relevant to your search!\n\nDo you want to search for another movie theme,\nor do you want to know more about this movie?\nAsk away!",
            "metadata": {
                "name": top_movie_name,
                "resource_file": top_movie_file,
                "session_id": session_id,
                "type": "SEARCH QUERY",
            },
        }


def chitchat(query, session_id):
    messages = [
        {"role": "system", "content": "You are a chit chat bot"},
        {"role": "user", "content": query},
    ]

    gpt_response = query_llm(messages)
    return {
        "content": gpt_response,
        "metadata": {
            "type": "CHIT-CHAT",
            "session_id": session_id,
        },
    }


def talktomovie(query, session_id, movie_search):
    movie_description = open(
        movie_search["resource_file"], encoding="utf-8"
    ).read()

    messages = [
        {
            "role": "system",
            "content": "You are a bot that only answers queries related to a movie from the description provided.",
        },
        {
            "role": "user",
            "content": f"{query}\n\nDescription:\n{movie_description}",
        },
    ]

    gpt_response = query_llm(messages, temperature=0.4)
    movie_search.pop("type")
    return {
        "content": gpt_response,
        "metadata": {
            "type": "FOLLOW UP",
            "session_id": session_id,
            **movie_search,
        },
    }


@app.get("/query")
def general_query(query, session_id, message_history=""):
    if message_history == "":
        message_history = []
    else:
        message_history = json.loads(message_history)

    past_user_messages = [x for x in message_history if x["role"] == "user"]

    if len(past_user_messages) == 0:
        prev_query = ""
    else:
        prev_query = past_user_messages[-1]["message"]

    messages = [
        {
            "role": "system",
            "content": "You are part of a decision making flow in a program that helps users discover movies.",
        },
        {
            "role": "user",
            "content": f"Is the below new query a follow up to the existing query or a completely new query, or a chit-chat? See the examples \n\nExamples:\n\nExisting Query: I want to watch a movie on dolls.\nNew Query: Did he direct any superhero films?\nResult: NEW QUERY\n\nExisting Query: I want to watch a historical world war 2 drama.\nNew Query: Is this movie based on a true story?\nResult: FOLLOW UP\n\nExisting Query: \nNew Query: Hey there\nResult: CHIT-CHAT\n\nExisting Query: I want to watch a horror movie\nNew Query: Hey there\nResult: CHIT-CHAT\n\n---\n\nExisting Query: {prev_query}\nNew Query: {query}\nResult:\n\n",
        },
    ]

    gpt_response = query_llm(messages, model="gpt-4")

    if "NEW QUERY" in gpt_response:
        return search_movie(query=query, session_id=session_id)
    elif "CHIT-CHAT" in gpt_response:
        return chitchat(query=query, session_id=session_id)
    elif "FOLLOW UP" in gpt_response:
        past_assistant_messages = [
            x for x in message_history if x["role"] == "assistant"
        ]
        for msg in past_assistant_messages[::-1]:
            if msg["metadata"]["type"] in ["SEARCH QUERY", "FOLLOW UP"]:
                movie_searched = msg["metadata"]
                break

        return talktomovie(
            query=query, session_id=session_id, movie_search=movie_searched
        )
    else:
        return {
            "content": "Unfortunately I could not understand. Could you please rephrase?",
            "metadata": {"session_id": session_id, "type": "UNHANDLED"},
        }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=1)
