import jaconv
from django.db.models import Q

def build_fuzzy_query(query_text: str, field_name: str = 'name') -> Q:
    """
    検索文字列から、ひらがな/カタカナ揺らぎを考慮したAND/OR検索クエリを構築する。
    
    Args:
        query_text: ユーザーが入力した検索キーワード文字列
        field_name: 検索対象のモデルフィールド名 (デフォルト: 'name')
        
    Returns:
        Qオブジェクト (フィルタ条件)
    """
    if not query_text:
        return Q()
        
    keywords = query_text.split()
    q_obj = Q()
    
    for keyword in keywords:
        hira = jaconv.kata2hira(keyword)
        kata = jaconv.hira2kata(keyword)
        
        # 部分一致条件をORで結合
        keyword_q = (
            Q(**{f"{field_name}__icontains": keyword}) |
            Q(**{f"{field_name}__icontains": hira}) |
            Q(**{f"{field_name}__icontains": kata})
        )
        
        # 各キーワード条件をANDで結合
        q_obj &= keyword_q
        
    return q_obj
