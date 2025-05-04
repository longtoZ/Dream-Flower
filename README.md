# Hệ thống Nhận diện bản nhạc quang học và Xử lý âm thanh cho Piano - Optical Music Recognition and Audio Processing for Piano

## *Lưu ý: Vì lí do thiếu hụt nguồn dữ liệu và thời gian, hệ thống chỉ được phát triển với một số chức năng cơ bản và chạy trong môi trường thử nghiệm. Bài báo cáo này sẽ trình bày các chức năng đã được thực hiện một cách hoàn chỉnh nhất có thể.*

# 1. Lời nói đầu

Từ một người yêu âm nhạc và lập trình,

Dự án mà bạn đang đọc không phải là một sản phẩm thương mại, cũng không phải là kết quả của một đề tài nghiên cứu mang tính chuyên sâu hay được tài trợ bởi bất kỳ tổ chức nào. Đây đơn thuần là một đồ án cá nhân mà tôi đã dành thời gian thực hiện trong suốt bốn tháng, tranh thủ từng khoảng thời gian rảnh rỗi sau những giờ học. Nó là sự kết hợp giữa hai niềm đam mê lớn – âm nhạc và lập trình – cùng với mong muốn tạo ra một điều gì đó vừa mang tính sáng tạo, vừa có giá trị thực tiễn.

Mục tiêu ban đầu của tôi là xây dựng một hệ thống có thể "đọc" được bản nhạc dưới dạng hình ảnh (như một tờ sheet nhạc) và tái tạo lại âm thanh của bản nhạc đó bằng tiếng đàn piano. Việc tìm hiểu các kỹ thuật nhận diện ký hiệu nhạc, xử lý ảnh, cũng như tổng hợp âm thanh – những lĩnh vực tưởng chừng rất khác biệt nhưng lại có thể kết nối với nhau một cách đầy thú vị.

Tôi không đặt mục tiêu xây dựng một hệ thống hoàn hảo, cũng không kỳ vọng nó sẽ thay thế con người trong việc hiểu và cảm nhận âm nhạc. Ngược lại, tôi coi đây là một hành trình học tập – nơi tôi được thực hành những kiến thức về xử lý ảnh, học máy, xử lý tín hiệu âm thanh, và cả cách tổ chức một dự án phần mềm theo hướng bài bản. Dự án không mang tính chuyên sâu vào một lĩnh vực nhất định, mà là sự giao thoa giữa các công nghệ và ý tưởng mà tôi đã có cơ hội tiếp cận trong quá trình học hỏi.

Ban đầu, tôi từng ấp ủ ý định phát triển một ứng dụng web hoàn chỉnh, với hệ thống quản lý người dùng, khả năng lưu trữ và tìm kiếm bản nhạc, chia sẻ với cộng đồng, và cả khả năng tạo bản nhạc từ ảnh chụp. Tuy nhiên, do hạn chế về thời gian và đặc biệt là dữ liệu huấn luyện cho các mô hình học sâu, tôi quyết định tập trung vào phần cốt lõi của hệ thống – đó là thuật toán phân tích hình ảnh bản nhạc và xử lý âm thanh.

Nếu bạn là một người yêu thích âm nhạc, lập trình, hoặc đơn giản là tò mò về cách mà công nghệ có thể can thiệp vào những lĩnh vực nghệ thuật như âm nhạc, tôi hy vọng bạn sẽ tìm thấy điều gì đó thú vị trong dự án này. Cảm ơn bạn đã dành thời gian để đọc bản báo cáo. Sự quan tâm và thấu hiểu của bạn chính là nguồn động lực lớn để tôi tiếp tục theo đuổi những ý tưởng khác trong tương lai.

Trân trọng,

LongTo.

# 2. Giới thiệu về báo cáo

Vì nội dung của báo cáo khá dài và có nhiều phần khác nhau, tôi đã chia báo cáo thành các phần riêng biệt để bạn có thể dễ dàng theo dõi. Các phần trong báo cáo bao được đặt ở thư mục `document`, bao gồm:

- [Part-1.md](./document/Part-1.md): Hệ thống nhận diện bản nhạc quang học (OMR)

- [Part-2.md](./document/Part-2.md): Quá trình tiền xử lý dữ liệu cho bản nhạc

- [Part-3.md](./document/Part-3.md): Phân tích và xử lý âm thanh

- [Part-4.md](./document/Part-4.md): Một số kỹ thuật và thư viện được sử dụng trong hệ thống

- [Full.md](./document/Full.md): Tất cả các phần trong báo cáo được gộp lại thành một file duy nhất

Một vài file âm thanh mẫu của 2 bản nhạc `Rewrite the stars` và `Your-lie-in-April` được lưu trữ trong thư mục `audio` để bạn có thể nghe thử.

Bạn có thể xem video trình bày sơ lược về hệ thống tại đây: [https://youtu.be/_i_xELRyrVo](https://youtu.be/_i_xELRyrVo)
