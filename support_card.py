#VERSION 1.2
import json
import textwrap
import unicodedata
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from globals import Elements, Rarity
from templates import SkillTemplate

@dataclass
class SupportCard:
    name: str
    desc: str
    element: Elements
    rarity: Rarity

    stat_variation: float

    #Stats base
    base_health: float
    base_attack: int
    base_defense: int

    #Stats modificados
    mod_health: float
    mod_attack: int
    mod_defense: int

    skill_list: tuple[SkillTemplate, ...]

    id: UUID = field(default_factory=uuid4)

    def to_json(self):
        name: str = self.name
        description: str = self.desc
        element: str = self.element.name
        rarity: float = self.rarity.value
        
        stat_variation: float = self.stat_variation
        
        #Stats base
        base_health: float = self.base_health
        base_attack: int = self.base_attack
        base_defense: int = self.base_defense
        
        #Stats modificados
        mod_health: float = self.mod_health
        mod_attack: int = self.mod_attack
        mod_defense: int = self.mod_defense
        
        skill_list: list[dict] = []
        for skill in self.skill_list:
            skill_list.append(skill.to_json())
        skill_tuple = tuple(skill_list)

        id: str = self.id.hex

        data = {
            "id": id,
            "name": name,
            "description": description,
            "element": element,
            "rarity": rarity,
            "stat_variation": stat_variation,

            "base_health": base_health,
            "base_attack": base_attack,
            "base_defense": base_defense,

            "mod_health": mod_health,
            "mod_attack": mod_attack,
            "mod_defense": mod_defense,

            "skill_list": skill_tuple
        }
        return data

    def debug_json_support(self):
        return json.dumps(self.to_json())
    

    def __str__(self) -> str:
        width = 50  # Un poco más estrecha para encajar bien si se anida dentro de MainCard
        content_width = width - 4

        def visual_len(text: str) -> int:
            return sum(2 if unicodedata.east_asian_width(c) in ('F', 'W') else 1 for c in text)

        def fmt_line(text: str, align: str = "left") -> str:
            v_len = visual_len(text)
            padding = max(0, content_width - v_len)
            if align == "center":
                left_pad = padding // 2
                right_pad = padding - left_pad
                return f"│ {' ' * left_pad}{text}{' ' * right_pad} │"
            return f"│ {text}{' ' * padding} │"

        rarity_str = getattr(self.rarity, 'name', str(self.rarity))
        elem_str = getattr(self.element, 'name', str(self.element))
        
        skills_formatted = [getattr(s, 'name', str(s)) for s in self.skill_list]
        skills_str = ", ".join(skills_formatted) if skills_formatted else "Ninguna"

        top_border    = f"┌{'─' * (width - 2)}┐"
        mid_border    = f"├{'─' * (width - 2)}┤"
        bottom_border = f"└{'─' * (width - 2)}┘"

        lines = [
            top_border,
            fmt_line(f"🎴 SOPORTE: {self.name.upper()}", align="center"),
            fmt_line(f"⭐ Rareza: {rarity_str} │ 🌀 Elemento: {elem_str}", align="center"),
            mid_border,
            fmt_line(f"❤️  HP: {self.mod_health:.0f} ({self.base_health:.0f}) ⚔️  ATK: {self.mod_attack} 🛡️  DEF: {self.mod_defense}"),
            fmt_line(f"📈 Variación de Stats: {self.stat_variation:+.2f}"),
            mid_border,
            fmt_line(f"✨ Skills: {skills_str}")
        ]

        if self.desc:
            lines.append(mid_border)
            wrapped_desc = textwrap.wrap(self.desc, width=content_width)
            for d_line in wrapped_desc:
                lines.append(fmt_line(f"📖 {d_line}" if d_line == wrapped_desc[0] else f"   {d_line}"))

        lines.append(bottom_border)
        return "\n".join(lines)