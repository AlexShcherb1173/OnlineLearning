from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    Стандартный пагинатор для списков курсов и уроков.
    Параметры:
      - page_size              — количество объектов на странице по умолчанию
      - page_size_query_param  — имя GET-параметра для управления размером страницы
      - max_page_size          — максимальное количество объектов на странице
    """

    page_size = 10                 # по умолчанию 10 объектов на страницу
    page_size_query_param = "page_size"
    max_page_size = 100            # не больше 100 за раз