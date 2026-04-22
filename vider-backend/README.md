# VIDER Backend — Local LLM + PostgreSQL/SQLite

## Giới thiệu

Backend cho dự án VIDER: API FastAPI lưu trữ lịch sử chat vào PostgreSQL (hoặc SQLite fallback) và sinh phản hồi bằng mô hình LLM chạy local (PyTorch + HuggingFace Transformers).

## Thành phần chính

| Thành phần | Mô tả |
|-----------|-------|
| **FastAPI** | API server (CORS-enabled) |
| **SQLAlchemy** | ORM — kết nối PostgreSQL hoặc SQLite |
| **LocalLLM** | Wrapper cho `transformers` + `torch`, model `Qwen2.5-1.5B-Instruct` |

## Yêu cầu

- Python 3.10+
- (Tuỳ chọn) PostgreSQL — nếu không có, tự động dùng SQLite
- (Tuỳ chọn) GPU + CUDA để tốc độ cao hơn

## Cài đặt nhanh

### 1. Tạo virtualenv

```powershell
cd vider-backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Cài dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình (tuỳ chọn)

Tạo file `.env`:

```env
# PostgreSQL (nếu có) — bỏ qua để dùng SQLite
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/vider_db

# Model LLM (mặc định: Qwen/Qwen2.5-1.5B-Instruct)
LLM_MODEL=Qwen/Qwen2.5-1.5B-Instruct

# CORS origins (mặc định: * cho development)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Server port
PORT=8000
```

> **Không có `.env`?** Backend vẫn chạy với SQLite + default model.

### 4. Chạy server

```bash
cd vider-backend
python main.py
```

Hoặc:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

> Lần đầu chạy, model sẽ được tải về (~3GB). SQLAlchemy sẽ tự tạo bảng.

## API Endpoints

### `GET /health`

Health check.

```json
{ "status": "ok", "service": "vider-backend" }
```

### `POST /chat`

Gửi tin nhắn và nhận phản hồi AI.

**Request:**
```json
{ "username": "alice", "message": "Xin chào" }
```

**Response:**
```json
{ "reply": "Xin chào! Tôi là VIDER...", "message_id": 42 }
```

### `GET /chat/history?username=alice&limit=50`

Lấy lịch sử chat.

## Test nhanh

```powershell
# Health check
Invoke-RestMethod -Uri http://localhost:8000/health

# Chat
Invoke-RestMethod -Method POST -Uri http://localhost:8000/chat `
  -ContentType "application/json" `
  -Body '{"username":"test","message":"Xin chao"}'
```

## Deploy Production (GPU Server)

### Dùng Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables cho production

```env
DATABASE_URL=postgresql://user:pass@db-host:5432/vider_db
LLM_MODEL=Qwen/Qwen2.5-1.5B-Instruct
CORS_ORIGINS=https://your-frontend.vercel.app
PORT=8000
```

### Lưu ý khi deploy

- **GPU Server**: Cần NVIDIA GPU + CUDA drivers. Model tự detect GPU qua `device_map="auto"`.
- **CPU Only**: Chạy chậm hơn nhưng vẫn hoạt động. Giảm `max_new_tokens` nếu cần.
- **Memory**: `Qwen2.5-1.5B-Instruct` cần ~3GB VRAM (bfloat16) hoặc ~6GB RAM (float32).
- **CORS**: Set `CORS_ORIGINS` chính xác domain frontend khi production.

## Kết nối Frontend

Frontend tự động gọi API qua biến `VITE_API_URL`:

```env
# File .env trong thư mục frontend (vider-interface)
VITE_API_URL=http://localhost:8000        # development
VITE_API_URL=https://api.your-domain.com  # production
```
