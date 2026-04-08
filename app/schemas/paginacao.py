from fastapi import Query


class Paginacao:
    def __init__(
        self,
        pagina: int = Query(default=1, ge=1, description="Número da página"),
        tamanho: int = Query(default=20, ge=1, le=100, description="Itens por página"),
    ):
        self.skip = (pagina - 1) * tamanho
        self.limit = tamanho
