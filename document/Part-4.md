# 4. Một số kỹ thuật và thư viện được sử dụng trong hệ thống
## 4.1. Server-Sent Events (SSE)
### 4.1.1. Giới thiệu

Server-Sent Events (SSE) là một công nghệ giao tiếp web một chiều cho phép server chủ động đẩy dữ liệu đến client mà không cần client phải liên tục gửi yêu cầu mới. SSE được xây dựng trên nền tảng HTTP và sử dụng một kết nối duy nhất, được duy trì trong thời gian dài để truyền dữ liệu theo thời gian thực.

SSE được giới thiệu như một phần của đặc tả HTML5, với mục tiêu cung cấp một phương thức đơn giản hơn WebSockets cho các tình huống chỉ cần giao tiếp một chiều từ server đến client. Công nghệ này được phát triển để thay thế các kỹ thuật polling truyền thống, vốn kém hiệu quả và tạo nhiều tải cho server.

SSE hoạt động theo nguyên tắc sau:

- **Thiết lập kết nối:** Client khởi tạo một kết nối HTTP đến server với header `Accept: text/event-stream`.

- **Duy trì kết nối:** Server giữ kết nối HTTP mở và không đóng sau khi gửi response.

- **Truyền dữ liệu:** Server gửi dữ liệu theo định dạng đặc biệt qua kết nối này, mỗi thông điệp bắt đầu bằng `data:` và kết thúc bằng hai ký tự xuống dòng (`\n\n`).

- **Xử lý dữ liệu:** Client nhận và xử lý các thông điệp này theo thời gian thực thông qua JavaScript API `EventSource`.

- **Kết nối lại tự động:** Nếu kết nối bị mất, trình duyệt tự động thử kết nối lại theo một thuật toán chờ tăng dần.

### 4.1.2. Hoạt động của SSE trong hệ thống
### Phía client

Quy trình hoàn chỉnh khi người dùng tải lên file PDF được mô tả như sau:

1. **Khởi tạo request upload:**

- User chọn file PDF và nhấn nút "Upload File"
- Client tạo FormData và gửi file lên endpoint `/api/upload` qua POST request

2. **Xử lý file trên server:**

- Server nhận file, lưu và trả về `session_id` để định danh phiên xử lý

3. **Thiết lập kết nối SSE:**

- Client tạo đối tượng `EventSource` kết nối tới endpoint `/api/stream/${sessionId}`
Server giữ kết nối này mở và bắt đầu xử lý PDF

4. **Stream dữ liệu theo thời gian thực:**

- Server xử lý PDF, tách thành các ảnh, phân tích từng vùng chứa ký hiệu âm nhạc
- Mỗi khi xử lý xong một vùng, server gửi dữ liệu qua kết nối SSE với định dạng:
    ```json
    {
        "filename": filename,
        "page": i + 1,
        "zone": j + 1,
        "image": image_base64,
        "boxes": extract_boxes,
        "staff_lines": staff_lines
    }
    ```

5. **Client nhận và xử lý dữ liệu:**

- Client nhận được sự kiện `onmessage` cho mỗi chunk dữ liệu gửi từ server
- Dữ liệu được parse từ JSON và thêm vào state `images`
- UI cập nhật để hiển thị hình ảnh và các box nhận diện được
- Dữ liệu được lưu vào localStorage để sử dụng sau này

6. **Kết thúc luồng SSE:**

- Khi xử lý tất cả vùng trên các trang PDF, server gửi message "done"
- Client nhận được thông báo này, đóng kết nối SSE và cập nhật trạng thái UI

7. **Xử lý lỗi:**

- Nếu có lỗi xảy ra, sự kiện onerror được kích hoạt
- Client đóng kết nối và hiển thị thông báo lỗi

### Phía server

Quy trình xử lý file PDF và gửi dữ liệu qua SSE được thực hiện như sau:

1. **Nhận file PDF:**

- Server nhận file PDF từ client qua endpoint `/api/upload`
- Lưu file vào thư mục và tạo một cặp `(key, value)` với `session_id` là key và value là một đối tượng chứa thông tin về file PDF, bao gồm đường tên file, đường dẫn lưu trữ và trạng thái xử lý
    ```json
    {
        "filename": saved_filename,
        "path": save_path,
        "status": "uploaded" 
    }
    ```

2. **Xác thực và lấy dữ liệu từ phiên:**

- Khi client gửi yêu cầu đến endpoint `/api/stream/${sessionId}`, server xác thực `session_id`
- Nếu hợp lệ, server lấy thông tin của file PDF cần được xử lý

3. **Truyền dữ liệu theo thời gian thực:**

- **Xử lý tuần tự các trang PDF:**

    Chuyển đổi PDF thành danh sách các ảnh sử dụng thư viện `pdf2image` và `poppler`

    ```python
    images = convert_from_path(pdf_path, dpi=300, fmt='png')
    ```

    Với mỗi ảnh đại diện cho mỗi trang, hệ thống chuyển đổi ảnh thành định dạng `byte` và phân tách thành các vùng khuông nhạc

    ```python
    img_io = io.BytesIO()
    img.save(img_io, "PNG")
    staff_zones = separate_staff_zones(img_io)
    ```

- **Xử lý chi tiết từng vùng:**

    Trích xuất thông tin và loại bỏ các dòng kẻ khuông nhạc

    ```python
    staff_lines = extract_staff_lines(zone)
    zone_no_lines = remove_staff_lines(zone)
    ```

    Trích xuất các box chứa ký hiệu âm nhạc

    ```python
    zone_io = io.BytesIO()
    zone_image.save(zone_io, "PNG")
    extrac_boxes = extract_boxes(zone_io)
    ```

- **Gửi dữ liệu từng phần:**

    Mỗi khi xử lý xong một vùng, server đóng gói kết quả vào `json` và sử dụng `yeild` để gửi dữ liệu ngay lập tức qua kết nối SSE

    ```python
    yield f"data: {json.dumps(data)}\n\n"
    ```

- **Báo hiệu hoàn thành:**

    Khi xử lý xong tất cả trang và vùng, server gửi thông báo `"data:done\n\n"`
    
    Xoá file PDF gốc và các thông tin phiên xử lý trong bộ nhớ

    ```python
    os.remove(pdf_path)
    del sessions[session_id]
    ```

## 4.2. WebSocket
### 4.2.1. Giới thiệu

WebSocket là một giao thức truyền thông hai chiều, thời gian thực cho phép giao tiếp song song giữa client và server qua một kết nối TCP duy nhất. Khác với HTTP truyền thống, WebSocket cung cấp kênh giao tiếp liên tục và không cần thiết lập lại kết nối cho mỗi tương tác.

WebSocket được giới thiệu trong HTML5 nhằm giải quyết các hạn chế của các kỹ thuật trước đây như polling và long polling, vốn không hiệu quả và tốn tài nguyên. Giao thức này được thiết kế để hoạt động trên cơ sở hạ tầng web hiện có, tương thích với proxy và tường lửa.

WebSocket hoạt động theo nguyên tắc sau:

- **Thiết lập kết nối:** Client khởi tạo "handshake" HTTP đến server với header `Upgrade: websocket`, yêu cầu nâng cấp kết nối HTTP thành WebSocket.

- **Chuyển đổi giao thức:** Server chấp nhận yêu cầu và trả về status code 101 (Switching Protocols), chuyển đổi kết nối HTTP thành WebSocket.

- **Truyền dữ liệu hai chiều:** Sau khi thiết lập, cả client và server đều có thể chủ động gửi dữ liệu cho nhau bất kỳ lúc nào mà không cần chờ yêu cầu.

- **Gửi tin nhắn có cấu trúc:** Dữ liệu được truyền dưới dạng "tin nhắn" riêng biệt trong các khung (frames), không phải dòng dữ liệu liên tục.

- **Đóng kết nối:** Bất kỳ bên nào cũng có thể chủ động đóng kết nối bằng cách gửi khung đóng kết nối.

### 4.2.2. Hoạt động của WebSocket trong hệ thống
### Phía client

- **Thiết lập kết nối:**

    Client khởi tạo kết nối WebSocket đến server với URL `/audio` và sử dụng thư viện `socket.io-client` để quản lý kết nối.

    ```javascript
    const socket = io("/audio", {
        transports: ["websocket"],
    });
    ```

    Sau khi kết nối thành công, client sẽ lưu `socketId` nhận được từ server, được sử dụng để xác định phiên làm việc cụ thể.

    ```javascript
    socket.on("connect", () => {
        sessionStorage.setItem('socketId', socket.id);
    });
    ```

- **Gửi yêu cầu tạo audio:**

    Khi người dùng nhấn nút "Create Audio", client gửi yêu cầu POST đến endpoint `/api/audio` với `socketId` trong body. Server sẽ sử dụng `socketId` này để gửi dữ liệu về trạng thái tiến trình tạo audio.

    ```javascript
    const socketId = sessionStorage.getItem('socketId');

    const data = {
        "music_sheet": musicSheetData,
        "measure_playtime": measurePlaytime,
        "audio_theme": selectedAudioTheme,
        "socket_id": socketId,
    }

    const response = await fetch("/api/generate-audio", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    });
    ```

- **Nhận dữ liệu từ server:**

    Client sẽ nhận về phản hồi loại `multipart/mixed` có chứa các checkpoints (loại `application/json`) và audio (loại `audio/mp3`).

    ```python
    response_body = (
        f"--{boundary}\r\n"
        "Content-Type: application/json\r\n\r\n"
        f"{json.dumps(checkpoints)}\r\n"
        f"--{boundary}\r\n"
        "Content-Type: audio/mp3\r\n"
        f"Content-Disposition: attachment; filename={filename}\r\n\r\n"
    ).encode("utf-8") + audio_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

    response = Response(
        response_body,
        mimetype=f"multipart/mixed; boundary={boundary}",
        headers={"Content-Length": str(len(response_body))},
    )
    ```

    Client khởi tạo audio blob từ phản hồi và tạo URL cho nó, sau đó sử dụng `Audio` API để phát âm thanh.

    ```javascript
    const audioBlob = new Blob([audioResponse], { type: "audio/mp3" });
    const audioUrl = URL.createObjectURL(audioBlob);
    ```

### Phía server

- **Khởi tạo WebSocket server:**

    Hệ thống sử dụng `socketio` bằng `SocketIO()` từ một model riêng biệt, hỗ trợ đa luồng (`async_mode='threading'`) vì quá trình tạo ra âm thanh của các khuông nhạc cũng dùng **đa luống**. Ngoài ra, nó còn tránh **circular import** khi import và cho phép sử dụng đối tượng `socketio` trong nhiều file khác nhau.    

- **Truyền dữ liệu qua WebSocket:**

    Server lấy `socket_id` từ POST request để xác định chính xác client đang kết nối. Sau đó, server gửi dữ liệu bằng phương thức `emit` của `socketio` với tên sự kiện là `status_update` và dữ liệu là một dictionary chứa thông tin về quá trình tạo ra audio của bản nhạc.

    ```python
    socket_io.emit(
        "status_update", 
        {
            "message": f"Processing sheet {i+1}/{len(music_sheet)}",
            "progress": progress
        }, 
        namespace="/audio", 
        to=socket_id
    )
    ```

- **Đóng kết nối:**

    Khi quá trình tạo audio hoàn tất, server gửi thông báo `"done"` qua WebSocket và đóng kết nối. Client sẽ nhận được thông báo này và có thể thực hiện các hành động tiếp theo như tải xuống file audio hoặc cập nhật giao diện người dùng.

    ```python
    socket_io.emit(
        "status_update", 
        {"message": "done"}, 
        namespace="/audio", 
        to=socket_id
    )
    ```

## 4.3. Multi-threading
### 4.3.1. Giới thiệu

Multi-threading là một kỹ thuật lập trình cho phép thực hiện nhiều luồng (thread) song song trong cùng một tiến trình (process). Mỗi luồng có thể thực hiện một tác vụ riêng biệt, giúp tăng hiệu suất và khả năng phản hồi của ứng dụng. Kỹ thuật này rất hữu ích trong các ứng dụng yêu cầu xử lý đồng thời nhiều tác vụ, như tải lên file, xử lý dữ liệu, hoặc giao tiếp mạng.

Trong quá trình tạo ra âm thành cho bản nhạc, `ThreadPoolExecutor` được sử dụng để tạo ra một nhóm các luồng (thread) để xử lý các khuông nhạc một cách song song. Điều này giúp giảm thời gian xử lý tổng thể và cải thiện hiệu suất của hệ thống, đặc biệt là khi các nốt nhạc có thể được sử dụng lại thông qua `USED_NOTES` dùng chung cho tất cả các `thread` đang chạy.

### 4.3.2. Sự phù hợp của multi-threading trong hệ thống

Một điểm nổi bật trong việc triển khai `ThreadPoolExecutor` là cách thu thập và kết hợp kết quả:

- **Thu thập theo thứ tự:** Mặc dù các tác vụ được thực hiện song song, kết quả được thu thập và sắp xếp theo thứ tự ban đầu của khuông nhạc để đảm bảo tính nhất quán của bản nhạc.

- **Cập nhật tiến trình hai giai đoạn:** Quá trình được chia thành hai giai đoạn: xử lý song song (0-50%) và kết hợp kết quả (50-100%), cho phép hiển thị tiến trình chính xác hơn.

- **Quản lý checkpoints:** Các checkpoint được điều chỉnh để phản ánh vị trí chính xác trong file âm thanh cuối cùng, cho phép người dùng nhảy đến các phần cụ thể của bản nhạc khi phát lại.

## 4.4. Các thư viện khác
### 4.4.1. React JSON View

React JSON View là một thư viện React cho phép hiển thị và tương tác với dữ liệu JSON một cách dễ dàng và trực quan. Thư viện này cung cấp một giao diện người dùng đẹp mắt để xem cấu trúc của dữ liệu JSON, cho phép người dùng mở rộng/thu gọn các phần tử, sao chép dữ liệu và thậm chí chỉnh sửa trực tiếp trong giao diện.

Trong hệ thống, React JSON View được sử dụng để hiển thị dữ liệu JSON của bản nhạc đã được xử lý. Người dùng có thể di chuyển qua các ô nhịp, khuông nhạc, trang khác nhau và xem các thông tin chi tiết về từng ký hiệu âm nhạc. Điều này giúp người dùng dễ dàng theo dõi và kiểm tra dữ liệu mà hệ thống đã nhận diện được.

### 4.4.2. React Toastify

React Toastify là một thư viện React cho phép hiển thị thông báo (toast notifications) một cách dễ dàng và tùy chỉnh. Thư viện này cung cấp nhiều tùy chọn để hiển thị thông báo với các kiểu dáng khác nhau, thời gian tự động đóng, vị trí hiển thị và nhiều tính năng khác.

Trong hệ thống, React Toastify được sử dụng để hiển thị các thông báo cho người dùng trong quá trình tải lên file PDF, xử lý âm thanh và các thông báo lỗi. Điều này giúp người dùng nhận biết được trạng thái của hệ thống và có thể thực hiện các hành động tiếp theo một cách dễ dàng hơn.

### 4.4.3. WaveSurfer.js

WaveSurfer.js là một thư viện JavaScript cho phép hiển thị và tương tác với sóng âm thanh trong trình duyệt. Thư viện này cung cấp nhiều tính năng như phóng to/thu nhỏ, kéo thả, tạo điểm đánh dấu và nhiều tính năng khác để làm việc với âm thanh.

Trong hệ thống, WaveSurfer.js được sử dụng để hiển thị sóng âm thanh của bản nhạc đã được xử lý. Người dùng có thể tương tác với sóng âm thanh, chọn các đoạn âm thanh cụ thể và phát lại chúng. Điều này giúp người dùng dễ dàng kiểm tra và chỉnh sửa âm thanh của bản nhạc theo ý muốn.

### 4.4.4. pdf2image

pdf2image là một thư viện Python cho phép chuyển đổi file PDF thành các hình ảnh (image) với độ phân giải cao. Thư viện này sử dụng `poppler` để thực hiện việc chuyển đổi và hỗ trợ nhiều định dạng hình ảnh khác nhau như PNG, JPEG, BMP, v.v.
Thư viện này rất hữu ích trong việc xử lý các file PDF, đặc biệt là trong các ứng dụng cần phân tích nội dung của file PDF như OMR.