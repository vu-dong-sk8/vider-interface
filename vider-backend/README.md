VIDER Backend — Local LLM + PostgreSQL

Giới thiệu

Đây là backend cho dự án VIDER: một API FastAPI lưu trữ lịch sử chat vào PostgreSQL và sinh phản hồi bằng một mô hình LLM chạy local (PyTorch + HuggingFace Transformers).

Thành phần chính

- FastAPI (API server)
- SQLAlchemy (ORM) kết nối PostgreSQL
- Local LLM: trình bọc `LocalLLM` sử dụng `transformers` + `torch`

Yêu cầu (Prerequisites)

- Python 3.10+ (hoặc 3.11)
- PostgreSQL (ví dụ: cài local hoặc container)
- Disk: cần dung lượng để tải mô hình (~ vài trăm MB tới vài GB tuỳ model)
- (Tuỳ chọn) GPU + CUDA để tốc độ cao hơn

Cài đặt nhanh

1. Tạo và kích hoạt virtualenv

PowerShell (Windows):

$ python -m venv .venv; ; .\.venv\Scripts\Activate.ps1

2. Cài dependencies

$ pip install -r vider-interface\vider-backend\requirements.txt

3. Tạo database PostgreSQL

- Ví dụ tạo DB và user:
  - DB name: vider_db
  - user: postgres (hoặc tạo user riêng)

4. Tạo file `.env` trong `vider-interface/vider-backend/` với nội dung ví dụ:

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/vider_db
LLM_MODEL=microsoft/Phi-3-mini-4k-instruct

(Thay thông tin theo cấu hình của bạn)

Chạy server

Từ root workspace (nơi có thư mục `vider-interface`):

$ uvicorn vider-backend.main:app --reload --host 0.0.0.0 --port 8000

Ghi chú: Lần đầu chạy, mô hình sẽ được tải về và SQLAlchemy sẽ tạo bảng (sử dụng Base.metadata.create_all).

API mẫu

POST /chat
- Request JSON:
  {"username": "alice", "message": "Xin chào"}
- Response JSON:
  {"reply": "..."}

Test nhanh bằng curl (PowerShell):

$ curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d '{"username":"alice","message":"Xin chao"}'

Lưu ý vận hành

- Model: mặc định sử dụng `microsoft/Phi-3-mini-4k-instruct`. Thay biến môi trường `LLM_MODEL` để dùng model khác. Lưu ý một số model lớn cần nhiều VRAM.
- Nếu không có GPU, Transformers sẽ chạy trên CPU nhưng chậm. Có thể giảm `max_new_tokens` trong hàm generate để tiết kiệm thời gian.
- Khuyến nghị cài accelerate và cấu hình nếu dùng GPU.

Tiếp theo

Nếu bạn muốn, tôi sẽ hướng dẫn:
- Cấu hình frontend để gọi API (TypeScript fetch) và hiển thị chat.
- Tối ưu prompt, giới hạn token, streaming trả về (sse) hoặc chuyển sang batching.

