import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llama_cpp import Llama
from app.ast_checker import validate_python_syntax

app = FastAPI(
    title="Fine-Tuned Qwen 2.5 Code Review Agent API (GGUF)",
    version="1.0.0"
)

MODEL_PATH = "./model_weights/qwen2.5-coder-7b-q4_k_m.gguf"
llm = None

@app.on_event("startup")
def load_agent():
    global llm
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"GGUF model binary missing at {MODEL_PATH}")
    
    print("🚀 Loading GGUF model into CPU RAM...")
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,
        n_threads=4,
        n_batch=512,
        verbose=False
    )
    print("✅ GGUF Model successfully loaded!")

class CodeReviewRequest(BaseModel):
    code: str

class CodeReviewResponse(BaseModel):
    syntax_valid: bool
    syntax_error: str | None
    review: str | None

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_ready": llm is not None}

@app.post("/api/v1/review", response_model=CodeReviewResponse)
def review_code(payload: CodeReviewRequest):
    if not payload.code.strip():
        raise HTTPException(status_code=400, detail="Code snippet cannot be empty.")

    # 1. AST Syntax Check Guardrail
    syntax_check = validate_python_syntax(payload.code)
    if not syntax_check["valid"]:
        return CodeReviewResponse(
            syntax_valid=False,
            syntax_error=syntax_check["error"],
            review="Automated Review Blocked: Please resolve syntax errors prior to LLM inspection."
        )

    # 2. Fast CPU Inference
    prompt = f"<|im_start|>user\nReview this Python code for bugs and optimization:\n{payload.code}<|im_end|>\n<|im_start|>assistant\n"
    
    output = llm(
        prompt,
        max_tokens=256,
        temperature=0.2,
        top_p=0.9,
        stop=["<|im_end|>", "</s>"]
    )

    review_text = output["choices"][0]["text"].strip()
    return CodeReviewResponse(
        syntax_valid=True,
        syntax_error=None,
        review=review_text
    )