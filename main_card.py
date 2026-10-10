#VERSION 1.2
import json
import textwrap
import unicodedata
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from globals import Elements, Rarity
from support_card import SupportCard
from templates import SkillTemplate

@dataclass
class MainCard:
    name: str
    desc: str
    main_element: Elements
    second_element: Elements
    rarity: Rarity

    support: SupportCard | None

    # Stats base
    base_health: float
    base_attack: int
    base_defense: int
    
    stat_variation: float
    ultimate_skill: SkillTemplate

    # Stats con variacion
    mod_health: float
    mod_attack: int
    mod_defense: int

    # Stats temporales para el combate (init=False evita que dataclass los sobreescriba)
    temp_health: float = field(init=False)
    temp_attack: int = field(init=False)
    temp_defense: int = field(init=False)

    id: UUID = field(default_factory=uuid4)

    def to_json(self):
        name: str = self.name
        description: str = self.desc
        main: str = self.main_element.name
        second: str = self.second_element.name
        rarity: float = self.rarity.value

        if self.support == None: support = None
        else: support = self.support.id.hex

        base_health: float = self.base_health
        base_attack: int = self.base_attack
        base_defense: int = self.base_defense
        
        stat_variation: float = self.stat_variation
        ultimate_skill = self.ultimate_skill.to_json()
        
        mod_health: float = self.mod_health
        mod_attack: int = self.mod_attack
        mod_defense: int = self.mod_defense

        id: str = self.id.hex
        data = {
            "id": id,
            "name": f"{name}",
            "description": f"{description}",
            "main_element": f"{main}",
            "second_element": f"{second}",

            "rarity": rarity,
            "support": support,

            "stat_variation": stat_variation,

            "base_health": base_health,
            "base_attack": base_attack,
            "base_defense": base_defense,

            "mod_health": mod_health,
            "mod_attack": mod_attack,
            "mod_defense": mod_defense,

            "ultimate_skill": ultimate_skill
        }

        return data

    def debug_json_skill(self):
        return json.dumps(self.ultimate_skill.to_json())

    def debug_json_main(self):
        return json.dumps(self.to_json())

    def __post_init__(self):
        self.apply_support()

    def take_damage(self, damage, multiplier):
        self.temp_health -= max(0, (damage * multiplier) - self.temp_defense)

    def is_alive(self):
        return self.temp_health > 0

    def apply_support(self):
        self.reset_temp_stats()
        if self.support is not None:
            if self.main_element == self.support.element or self.second_element == self.support.element:
                modifier = 1.75
            else:
                modifier = 1
                
            self.temp_health += round((self.support.mod_health * modifier) * 0.15)
            self.temp_attack += round((self.support.mod_attack * modifier) * 0.15)
            self.temp_defense += round((self.support.mod_defense * modifier) * 0.15)

    def reset_temp_stats(self):
        self.temp_health = float(self.mod_health)
        self.temp_attack = int(self.mod_attack)
        self.temp_defense = int(self.mod_defense)

    def __str__(self) -> str:
        width = 58
        content_width = width - 4

        def visual_len(text: str) -> int:
            return sum(2 if unicodedata.east_asian_width(c) in ('F', 'W') else 1 for c in text)

        def fmt_line(text: str, align: str = "left") -> str:
            v_len = visual_len(text)
            padding = max(0, content_width - v_len)
            if align == "center":
                left_pad = padding // 2
                right_pad = padding - left_pad
                return f"║ {' ' * left_pad}{text}{' ' * right_pad} ║"
            return f"║ {text}{' ' * padding} ║"

        rarity_str = getattr(self.rarity, 'name', str(self.rarity))
        m_elem = getattr(self.main_element, 'name', str(self.main_element))
        s_elem = getattr(self.second_element, 'name', str(self.second_element))
        elem_info = m_elem if self.second_element == Elements.NONE else f"{m_elem} / {s_elem}"
        ult_name = getattr(self.ultimate_skill, 'name', str(self.ultimate_skill))

        top_border    = f"╔{'═' * (width - 2)}╗"
        mid_border    = f"╠{'═' * (width - 2)}╣"
        div_border    = f"╟{'─' * (width - 2)}╢"
        bottom_border = f"╚{'═' * (width - 2)}╝"

        lines = [
            top_border,
            fmt_line(f"⚔️  {self.name.upper()}", align="center"),
            fmt_line(f"⭐ Rareza: {rarity_str}  │  🆔 {str(self.id)[:8]}...", align="center"),
            mid_border,
            fmt_line(f"🌀 Elemento : {elem_info}"),
            fmt_line(f"💥 Ultimate : {ult_name}"),
            fmt_line(f"📈 Variación: {self.stat_variation:+.2f}"),
            div_border,
            fmt_line(f"❤️  HP: {self.mod_health:.0f} ({self.base_health:.0f}) │ ⚔️  ATK: {self.mod_attack} ({self.base_attack}) │ 🛡️  DEF: {self.mod_defense} ({self.base_defense})")
        ]

        # Comprobar si los stats temporales son diferentes a los modificados
        has_temp_changes = (
            self.temp_health != self.mod_health or
            self.temp_attack != self.mod_attack or
            self.temp_defense != self.mod_defense
        )

        if has_temp_changes:
            status_symbol = "💀" if not self.is_alive() else "🔄"
            lines.append(
                fmt_line(f"{status_symbol} ACTUAL: {self.temp_health:.0f} HP │ {self.temp_attack} ATK │ {self.temp_defense} DEF", align="center")
            )

        if self.desc:
            lines.append(div_border)
            wrapped_desc = textwrap.wrap(self.desc, width=content_width)
            for d_line in wrapped_desc:
                lines.append(fmt_line(f"📖 {d_line}" if d_line == wrapped_desc[0] else f"   {d_line}"))

        if self.support is not None:
            lines.append(mid_border)
            lines.append(fmt_line("EQUIPAMIENTO Y SOPORTE", align="center"))
            lines.append(mid_border)
            
            support_lines = str(self.support).split("\n")
            for s_line in support_lines:
                lines.append(fmt_line(s_line, align="center"))

        lines.append(bottom_border)
        return "\n".join(lines)