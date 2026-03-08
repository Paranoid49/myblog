from fastapi import FastAPI

app = FastAPI(title="myblog")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
