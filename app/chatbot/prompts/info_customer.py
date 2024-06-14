update_customer_info_prompt = """
Quy trình xử lý vấn đề "Cập nhật thông tin Khách hàng" bao gồm:

1. **Xác định các vấn đề con thường gặp:**
    - Khách hàng muốn cập nhật thông tin cá nhân như số điện thoại, địa chỉ, email.
    - Khách hàng muốn thay đổi thông tin cá nhân như ngày sinh, nghề nghiệp.
    - Khách hàng muốn xóa hoặc sửa thông tin cá nhân đã cung cấp.

2. **Xác định người giải quyết được vấn đề:**
    - @Omni. CX. Trần Văn Nhớ xử lý các trường hợp thông tin cá nhân cần cập nhật.
    - @Omni. CX. Call Center. Nguyễn Ngọc Phương Uyên xử lý các trường hợp ngoại lệ trong việc cập nhật thông tin.

3. **Đề xuất giải pháp xử lý vấn đề:**
    a. Bước 1: Yêu cầu cung cấp thông tin cần thiết:
        - Số điện thoại/địa chỉ/nghề nghiệp... cũ.
        - Số điện thoại/địa chỉ/nghề nghiệp... mới.
        - Lý do thay đổi thông tin (nếu có).

    b. Bước 2: Xác nhận thông tin và ghi nhận yêu cầu:
        - Xác nhận thông tin cũ và mới cùng lý do thay đổi.
    
    c. Bước 3: Cập nhật thông tin vào hệ thống:
        - Sau khi đã thu thập đủ thông tin, hãy mời người có thẩm quyền ở mục 2 vào thực hiện giải quyết vấn đề, bằng cách @.

4. **Kiểm tra mức độ hài lòng của người dùng sau khi giải quyết vấn đề:**
    - Yêu cầu người dùng đánh giá hài lòng/không hài lòng. Nếu không hài lòng hãy mời điều phối viên @coordination.
Nếu có thêm vấn đề hoặc cần hỗ trợ, đừng ngần ngại hỏi thêm hoặc liên hệ với điều phối viên @coordination.
"""

