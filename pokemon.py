class Pokemon:
    def __init__(self, id: int, slug: str) -> None:
        self.id = id
        self.slug = slug

    def __repr__(self) -> str:
        return f"<Pokemon id={self.id} slug={self.slug}>"
