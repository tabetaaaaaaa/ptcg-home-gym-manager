from django_filters.widgets import RangeWidget

class RangeSliderWidget(RangeWidget):
    template_name = 'cards/widgets/range_slider.html'

    def __init__(self, attrs=None, min_val=0, max_val=100, step=1):
        # 個別のウィジェットに渡す属性を設定
        default_attrs = {'class': 'range-input'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
        self.min_val = min_val
        self.max_val = max_val
        self.step = step

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['min_val'] = self.min_val
        context['max_val'] = self.max_val
        context['step'] = self.step
        # サブウィジェットのデータを使いやすく整理
        # value は [min, max] のリスト形式
        context['current_min'] = value[0] if value and value[0] is not None else self.min_val
        context['current_max'] = value[1] if value and value[1] is not None else self.max_val
        return context
