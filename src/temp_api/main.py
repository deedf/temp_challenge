"""Main program for temperature API"""
import uvicorn


def _main():
    uvicorn.run("temp_api.api:app", port=5000, log_level="info", host="0.0.0.0")


if __name__ == "__main__":
    _main()
