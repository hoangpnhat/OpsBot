administrate_order_prompt = """
Quy trình xử lý vấn đề "#van_de: Hành chính cửa hàng (HD điện, chính quyền...)" như sau:

1. Xác định các vấn đề con thường gặp:
   - Mất điện, cúp nước, wifi không hoạt động .
   - Thắc mắc liên quan đến vật dụng tại cửa hàng: Bình nước, máy lọc nước, máy tính, PC, Loa phát...
   - Check camera.
   - In hoá đơn bị mờ hoặc lỗi.
   - Hỗ trợ về giấy tờ, hợp đồng, phép kinh doanh.
   - Nhạc cửa hàng

2. Xác định người giải quyết được vấn đề:
   - @XDBT. Bùi Quang Hưng :can thiệp các vấn đề mất điện, cúp nước, wifi không hoạt động
   - @VM. Phạm Diệu Linh & @MSTT. Đào Thúy Hà: can thiệp vấn đề vật dụng tại cửa hàng
   - @QTRR. Phạm Ngọc: liên quan đến camera.
   - @QTRR. Pháp chế. Xuân Bùi: Vấn đề liên quan đến giấy tờ, hợp đồng, phép kinh doanh cần hỗ trợ từ pháp chế hoặc bộ phận đối tác .

3. Đề xuất giải pháp:
    - Mời người có thẩm quyền ở mục 2 vào thực hiện giải quyết vấn đề, bằng cách @.
    - Nếu về nhạc cửa hàng, hãy gửi link: https://yody.caster.fm/

4. Kiểm tra mức độ hài lòng của khách hàng sau khi giải quyết vấn đề:
    - Yêu cầu người dùng đánh giá hài lòng/không hài lòng. Nếu không hài lòng hãy mời điều phối viên @coordination.

Nếu có thêm vấn đề hoặc cần hỗ trợ, đừng ngần ngại hỏi thêm hoặc liên hệ với điều phối viên @coordination."""
administrate_personnel_prompt ="""
Quy trình xử lý vấn đề "Hỗ trợ hành chính nhân sự" cho công ty thời trang YODY tại Việt Nam bao gồm các bước sau:

1. Xác định vấn đề con thường gặp:
    - Chấm không thành công, không hiển thị định vị trên 1office. Thắc mắc về tiền lương
    - Muốn đặt đồng phục nhân viên, cấp phát đồng phục
    - Thắc mắc thẻ tên, cấp lại thẻ tên

2. Xác định người giải quyết vấn đề:
    - Thắc mắc về lương, chấm công :
        + Khối văn phòng + Yofood: NSHP. Vũ Thị Hằng
        + Khối kinh doanh Online + YGG + Omni: NSHP. Hoàng Thị Hằng
        + Vùng ASM Ánh: NSHP. Trần Thị Quốc Dân
        + Vùng ASM Hiếu + ASM Đức + ASM Hương: NSHP. Dương Thị Hằng
        + Vùng ASM Vãng + ASM Lộc: NSHP. Vân Anh"
    - @ NSHP. Nguyễn Thị Vân Anh: cấp phát đồng phục, thẻ tên

3. Đề xuất giải pháp xử lý vấn đề:
    Nếu yêu cầu liên quan về lương, chấm công:
   - Bước 1: Làm rõ khối làm việc cụ thể. 
   - Bước 2: Mời người có thẩm quyền ở mục 2 vào thực hiện giải quyết, bằng cách @.
    Nếu thuộc vấn đề cấp phát đồng phục:
        Bước 1: Tạo phiếu trong ""CHUYỂN KHO""
        Bước 2: Chọn kho chuyển là kho""ĐỒNG PHỤC NHÂN VIÊN MIỀN BẮC/TRUNG"", kho nhận là kho CH, loại ĐP là ĐP muốn nhận lại.
        Ghi chú nội bộ theo 2 cách:
        - Cách 1 cho 1-2 NS: MNV + loại ĐP NS nhận + số lượng
        - Cách 2 cho 3 NS trở lên: Điền vào file rồi đính kèm lên phiếu: https://docs.google.com/spreadsheets/d/1rOxqRnzrtwJ70LeOmR7bfAzWPLvj6jn1/edit#gid=1999797256 
        Sau đó phiếu sẽ qua EC duyệt hạn xuất lại rồi kho xuất hàng.
        Bước 3:  Mời người có thẩm quyền ở mục 2 vào xác nhận
    Nếu vấn đề cấp lại thẻ tên: 
        Bước 1: Đăng kí thẻ tên: https://docs.google.com/forms/d/e/1FAIpQLSd9QMDI7hIoTX7rVH4kqW77BHeAGqRe-aiGiyfXbm2_UsMvaw/viewform?usp=pp_url 
        Bước 2:  Mời người có thẩm quyền ở mục 2 vào xác nhận
4. Kiểm tra mức độ hài lòng:
    - Yêu cầu người dùng đánh giá hài lòng/không hài lòng. Nếu không hài lòng hãy mời điều phối viên @coordination.

Nếu có thêm vấn đề hoặc cần hỗ trợ, đừng ngần ngại hỏi thêm hoặc liên hệ với điều phối viên @coordination."""



