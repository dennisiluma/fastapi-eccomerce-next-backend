import uvicorn

def main():
    print("Hello from shopease!")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8084, reload=True)


if __name__ == "__main__":
    main()
