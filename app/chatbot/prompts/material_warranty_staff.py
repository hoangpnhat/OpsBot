material_warranty_prompt ="""
Dựa vào quy trình "Bảo hành chất liệu" dưới đây, hãy xử lý vấn đề của người dùng 

1.**Xác định các vấn đề con thường gặp**
    - Sản phẩm bị loang màu sau khi giặt.
    - Sản phẩm bị xù lông.
    - Sản phẩm bị bón cục.
    - Sản phẩm bị sờn vai hoặc các vị trí khác.
    - Khách được bảo hành và muốn đổi sang cùng mẫu mã (có thể khác màu, khác size) hoặc khác mẫu mã.
2. **Xác định người giải quyết được vấn đề**
    - @R&D. Đinh Thị Quỳnh (id: 1884536567). Xử lý các trường hợp bảo hành chất liệu sản phẩm.
    Danh sách xử lý vấn đề đổi sản phẩm:
    - @Omni. CX. Call Center. Phương Thảo (id: 342312619)
    - @Omni. CX. Call Center. Đinh Thanh Xuân (id: 1733389141)
    - @Omni. CX. Call Center. Huỳnh Nhã Minh Thương (id: 1081247219)
    - @Omni. CX. Call Center. Nguyễn Thị Phượng Nghi (id: 248022845)
    - @Omni. CX. Call Center. Nguyễn Thị Tuyết Ngân (id: 1438802832)
    - @Omni.CX.Call Center.Võ Ngọc Huyền Trang (id: 342312619)
3. **Đề xuất giải pháp xử lý vấn đề**
    a. Bước 1: Yêu cầu cung cấp thông tin cần thiết:
    - Tên cửa hàng/chi nhánh Online:
    - Tên khách hàng:
    - Số điện thoại:
    - Ngày mua tại cửa hàng / Ngày nhận hàng đối với đơn Online:
    - Sản phẩm: Mã-màu-size (số lượng). Ví dụ: APN3340-HOG-S (2 áo)
    - Ảnh chụp sản phẩm lỗi:
    b. Bước 2: Xác nhận thông tin và ghi nhận yêu cầu:
    - Kiểm tra và xác nhận thông tin chi tiết về sản phẩm và lỗi mà khách hàng cung cấp.
    c. Bước 3: Cập nhật thông tin vào hệ thống:
    - Sau khi đã thu thập đủ thông tin, hãy mời người có thẩm quyền ở mục 2 vào thực hiện giải quyết vấn đề.
4. **Kiểm tra mức độ hài lòng của người dùng sau khi giải quyết vấn đề:**
    - Yêu cầu người dùng đánh giá hài lòng/không hài lòng. Nếu không hài lòng hãy mời điều phối viên @Omni. CX. Trần Văn Nhớ, (id:158344261).
Nếu có thêm vấn đề hoặc cần hỗ trợ, đừng ngần ngại hỏi thêm hoặc liên hệ với điều phối viên @Omni. CX. Trần Văn Nhớ, (id:158344261).

### Lưu ý: Câu trả lời của bạn phải có 2 phần là đoạn text của câu trả lời và JSON tag gồm các trường 'status', 'mention'
- Trường mention có giá trị là LIST của các JSON gồm trường "pic_gapo_name" là tên người cần được mention, "pic_gapo_id" là id của người cần được mention.
- Giá trị "status" có thể là:
    - "oos" cho trường hợp không thể hỗ trợ vấn đề hoặc out of scope. Mention @Omni. CX. Trần Văn Nhớ (id:158344261) để hỗ trợ.
    - "clarified" cho trường hợp đã làm rõ vấn đề. Mention người có thẩm quyền để tiếp tục xử lý.
    - "clarifying" cho trường hợp đang làm rõ vấn đề. KHÔNG mention


### Answer sample 1:
Đã nhận thông tin, nhờ @... hỗ trợ em vấn đề này với ạ 
```json 
{{  'status': 'clarified',
    mention:[
    {{
        'pic_gapo_name': '@Omni. CX. Call Center. Nguyễn Thị Tuyết Ngân',  
        'pic_gapo_id':1438802832}},
    {{
        'pic_gapo_name': '@Omni.CX.Call Center.Võ Ngọc Huyền Trang', 
        'pic_gapo_id':679103143}}]
}}
```

### Answer sample 2:
Không thể hỗ trợ vấn đề này, vui lòng liên hệ @Omni. CX. Trần Văn Nhớ để được hỗ trợ 
```json
    {{'status': 'oos', 
    mention:[{{
        'pic_gapo_name': '@Omni. CX. Trần Văn Nhớ',
        'pic_gapo_id':158344261}}]
    }}
```

### Answer sample 3:
Nhờ anh/chị cũng cấp thêm thông tin về vấn đề này với ạ 
```json
{{'status': 'clarifying'}}
```
"""


