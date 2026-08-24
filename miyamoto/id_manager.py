# Sprite ID Manager for dynamic string<->integer ID mapping
# Handles the allocation of integer IDs for custom sprites identified by strings

from . import globals
import struct

SpritemapVersion = 2

class SpriteIDManager:
    def __init__(self):
        self.reset()

    def reset(self):
        self.string_to_int = {}
        self.int_to_string = {}
        self.next_free_id = 0b1111000000000000

    def load_from_binary(self, data: bytes):
        self.reset()
        if not data:
            return

        try:
            if len(data) < 8:
                raise ValueError("Data too short for header")
                
            version, count = struct.unpack('>II', data[:8])
            
            if version != SpritemapVersion:
                raise RuntimeError(f"Spritemap version mismatch: Got {version}, expected {SpritemapVersion}")

            if count == 0:
                return

            offset_table_start = 8
            offsets = []
            
            for i in range(count):
                ptr = offset_table_start + (i * 4)
                str_offset, = struct.unpack('>I', data[ptr:ptr+4])
                offsets.append(str_offset)

            for offset in offsets:
                if offset >= len(data):
                    raise IndexError(f"String offset 0x{offset:X} is out of bounds")

                null_terminator_index = data.find(b'\x00', offset)
                if null_terminator_index == -1:
                    raise ValueError("Malformed spritemap entry: missing null terminator")

                utf8_string_id = data[offset:null_terminator_index].decode('utf-8')

                if utf8_string_id:
                    self.get_id_for_string(utf8_string_id)

        except (struct.error, IndexError, ValueError, UnicodeDecodeError, RuntimeError) as e:
            print(f"Error parsing spritemap.bin: {e}")
            self.reset()

    def get_save_data_binary(self) -> bytes:
        if not self.string_to_int:
            return b""

        sorted_items = sorted(self.string_to_int.items(), key=lambda item: item[1])
        sorted_strings = [item[0] for item in sorted_items]
        count = len(sorted_strings)

        header_bytes = bytearray()
        offset_table_bytes = bytearray()
        string_pool_bytes = bytearray()

        current_offset = 8 + (count * 4)

        for name in sorted_strings:
            offset_table_bytes.extend(struct.pack('>I', current_offset))

            encoded_str = name.encode('utf-8') + b'\x00'
            string_pool_bytes.extend(encoded_str)

            current_offset += len(encoded_str)

        header_bytes.extend(struct.pack('>II', SpritemapVersion, count))

        return bytes(header_bytes + offset_table_bytes + string_pool_bytes)

    def get_id_for_string(self, str_id: str) -> int:
        if str_id in self.string_to_int:
            return self.string_to_int[str_id]

        new_id = self.next_free_id
        self.next_free_id += 1

        self.string_to_int[str_id] = new_id
        self.int_to_string[new_id] = str_id

        while len(globals.Sprites) <= new_id: # HOLY RAM WASTE
            globals.Sprites.append(None)
        
        if str_id in globals.CustomSpriteDefinitions:
            globals.Sprites[new_id] = globals.CustomSpriteDefinitions[str_id]

        return new_id
    
    def get_string_for_id(self, int_id: int) -> str:
        if int_id in self.int_to_string:
            str_id = self.int_to_string[int_id]
            if str_id not in globals.CustomSpriteDefinitions:
                return ""
            return str_id

        return ""

    def cull_unused(self, used_strings):
        """
        Removes mappings whose string isn't in used_strings.
        Survivors keep their existing integer IDs so in-memory sprite
        references stay valid; the next save writes a compacted table.
        """
        dead = [(s, i) for s, i in self.string_to_int.items() if s not in used_strings]
        for str_id, int_id in dead:
            del self.string_to_int[str_id]
            del self.int_to_string[int_id]
