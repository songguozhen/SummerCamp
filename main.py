# Run: uvicorn main:app --reload --host 127.0.0.1 --port 8000
import csv
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")
SILICONFLOW_BASE_URL = "https://api.siliconflow.cn/v1"
MODEL = "deepseek-ai/DeepSeek-V3"

DATA_DIR = Path("data")
CSV_FILE = DATA_DIR / "camps.csv"
JSON_FILE = DATA_DIR / "camps.json"

CSV_FIELDS = [
    "id", "created_at", "school", "institute", "program_name",
    "registration_start", "registration_end",
    "activity_start", "activity_end", "notes", "raw_text"
]

SYSTEM_PROMPT = """你是一个结构化信息提取助手。用户会粘贴关于大学生夏令营的中文通知。
只返回合法 JSON，不包含任何其他文字或 markdown 代码块。

字段：
- school: 大学/高校名称
- institute: 学院/研究所名称（没有则返回空字符串）
- program_name: 项目名称（去掉"通知""关于"等前缀，不含学校和研究所名）
- registration_start: 报名开始日期 YYYY-MM-DD（仅截止日期则返回 null）
- registration_end: 报名截止日期 YYYY-MM-DD（最重要字段）
- activity_start: 活动开始日期 YYYY-MM-DD（未知返回 null）
- activity_end: 活动结束日期 YYYY-MM-DD（未知返回 null）

规则：日期统一转 YYYY-MM-DD，年份默认 2026；字段不存在返回 null。
只返回 JSON 对象，不要任何其他内容。"""


def init_storage():
    DATA_DIR.mkdir(exist_ok=True)
    if not CSV_FILE.exists():
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()
    if not JSON_FILE.exists():
        JSON_FILE.write_text("[]", encoding="utf-8")


def read_csv() -> list[dict]:
    if not CSV_FILE.exists():
        return []
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def write_csv(entries: list[dict]):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(entries)


def sync_json(entries: list[dict]):
    JSON_FILE.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


init_storage()


class ExtractRequest(BaseModel):
    text: str


class EntryCreate(BaseModel):
    school: str
    institute: Optional[str] = ""
    program_name: str
    registration_start: Optional[str] = None
    registration_end: Optional[str] = None
    activity_start: Optional[str] = None
    activity_end: Optional[str] = None
    notes: Optional[str] = ""
    raw_text: Optional[str] = ""


@app.post("/api/extract")
def extract(body: ExtractRequest):
    if not SILICONFLOW_API_KEY:
        raise HTTPException(status_code=500, detail="SILICONFLOW_API_KEY not configured")
    client = OpenAI(api_key=SILICONFLOW_API_KEY, base_url=SILICONFLOW_BASE_URL)
    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=512,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": body.text},
            ],
        )
        raw = response.choices[0].message.content.strip()
        # Strip markdown code block if model still wraps it
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=422, detail=f"LLM returned non-JSON: {raw}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/entries")
def get_entries():
    entries = read_csv()
    sync_json(entries)
    return entries


@app.post("/api/entries")
def create_entry(body: EntryCreate):
    entries = read_csv()
    for e in entries:
        if (e.get("program_name", "").strip() == (body.program_name or "").strip()
                and e.get("registration_end", "").strip() == (body.registration_end or "").strip()):
            raise HTTPException(status_code=409, detail="duplicate")
    new_entry = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        **body.model_dump(),
    }
    # Normalize None to empty string for CSV compatibility
    for k, v in new_entry.items():
        if v is None:
            new_entry[k] = ""
    entries.append(new_entry)
    write_csv(entries)
    sync_json(entries)
    return new_entry


@app.delete("/api/entries/{entry_id}")
def delete_entry(entry_id: str):
    entries = read_csv()
    filtered = [e for e in entries if e["id"] != entry_id]
    if len(filtered) == len(entries):
        raise HTTPException(status_code=404, detail="Entry not found")
    write_csv(filtered)
    sync_json(filtered)
    return {"ok": True}


# Serve frontend — must be last to not shadow API routes
app.mount("/", StaticFiles(directory="static", html=True), name="static")
