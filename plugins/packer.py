from typing import Union

class Packer:
    def __init__(self, img_info) -> None:
        self.duplicate_of = img_info["duplicate_of"]
        if img_info["duplicate_of"]:
            return
        self.urls = img_info["representations"]
        self.score = img_info["score"]
        self.id = img_info["id"]

    def get_url(self) -> str:
        raise NotImplementedError

    def get_packet(self) -> dict[str, Union[str, int]]:
        return {
            "url": self.get_url(),
            "score": self.score,
            "id": self.id
        }


class ImagePacker(Packer):
    def __init__(self, img_info) -> None:
        super().__init__(img_info)

    def get_url(self) -> str:
        return self.urls["large"]


class ImageListPacker(ImagePacker):
    def __init__(self, img_info_list) -> None:
        self.packet = []
        for img_info in img_info_list:
            packer = ImagePacker(img_info)
            if packer.duplicate_of:
                continue
            self.packet.append(packer.get_packet())

    def get_packet(self) -> list[dict[str, str | int]]:
        return self.packet


class WebMPacker(Packer):
    def __init__(self, img_info) -> None:
        super().__init__(img_info)
    
    def get_url(self) -> str:
        return self.urls["medium"]