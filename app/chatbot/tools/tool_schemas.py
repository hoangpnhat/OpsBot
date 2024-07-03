from pydantic import BaseModel, Field

class search_product(BaseModel):
    """
    Hàm `search_product` dùng để tìm kiếm thông tin sản phẩm dựa vào mã sản phẩm
    """
    product_code: str = Field(..., title="product_code", description="Mã sản phẩm cần tìm kiếm")


class query_promotion(BaseModel):
    """
    Hàm `promotion` được chọn đối khi user cần truy vấn, tìm kiếm thông tin về chương trình khuyến mãi
    """
    query: str = Field(..., title="user_query", description="Câu truy vấn/câu hỏi của user về chương trình khuyến mãi")