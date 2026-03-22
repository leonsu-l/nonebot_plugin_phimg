from typing import Union, TypedDict

class ImageInfo(TypedDict, total=False):
    duplicate_of: int | None
    hidden_from_users: bool | None
    representations: dict[str, str]
    score: int
    id: int

class Packer:
    def __init__(self, img_info: ImageInfo) -> None:
        self.hidden = img_info["duplicate_of"] or img_info["hidden_from_users"]# type: ignore
        if self.hidden:
            self.urls = {}
            self.score = 0
            self.id = 0
            return
        self.urls = img_info["representations"] # type: ignore
        self.score = img_info["score"] # type: ignore
        self.id = img_info["id"] # type: ignore

    def get_url(self) -> str:
        raise NotImplementedError

    def get_packet(self) -> dict[str, Union[str, int]]:
        return {
            "url": self.get_url(),
            "score": self.score,
            "id": self.id
        }


class ImagePacker(Packer):
    def get_url(self) -> str:
        return self.urls["large"]


class WebMPacker(Packer):
    def get_url(self) -> str:
        return self.urls["medium"]


class ImageListPacker:
    def __init__(self, img_info_list: list[ImageInfo]) -> None:
        self.packet = [
            ImagePacker(img_info).get_packet()
            for img_info in img_info_list
            if not img_info["duplicate_of"] and not img_info["hidden_from_users"] # type: ignore
        ]

    def get_packet(self) -> list[dict[str, str | int]]:
        return self.packet