import uvicorn



if __name__ == "__main__":
    uvicorn.run("server.api:api", host="0.0.0.0", port=80, reload=True)