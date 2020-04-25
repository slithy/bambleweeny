from enum import Enum
from cogscc.funcs.dice import roll


class Wound(Enum):
    NORMAL = 1
    GRIEVOUS = 2
    MORTAL = 3
    DEAD = 4


class Bleeding(Enum):
    GRACE = 1
    BLEEDING = 2
    NOT_BLEEDING = 3


class HP:
    def __init__(self, max: int, current: int = 999, wound: Wound = Wound.NORMAL, bleeding = Bleeding.NOT_BLEEDING, conscious: bool = True):
        self.max = max
        self.current = max
        if current < max:
            self.current = current
        self.wound = wound
        self.bleeding = bleeding
        self.conscious = conscious

    @classmethod
    def __from_dict__(cls, d):
        hp = cls(**d)
        hp.wound = getattr(Wound, hp.wound)
        hp.bleeding = getattr(Bleeding, hp.bleeding)
        return hp

    def __to_json__(self):
        return {
            'max': self.max, 'current': self.current, 'wound': self.wound.name, 'bleeding': self.bleeding.name, 'conscious': self.conscious
        }

    # ---------- main funcs ----------
    def recover(self, name: str, hp: int):
        if self.current == self.max:
            return ''
        hp_text = f"{hp} hit points"
        if hp == 1:
           hp_text = "1 hit point"
        if self.current + hp <= self.max:
            self.current += hp
            return f"\n{name} recovers {hp_text}. :medical_symbol:  **HP**: {self.current}/{self.max}"
        else:
            self.current = self.max
            return f"\n{name} recovers to full strength. :medical_symbol:  **HP**: {self.current}/{self.max}"

    def rest(self, name: str, conMod: int, duration: int):
        if self.wound == Wound.DEAD:
            return f"{name} gets rigor mortis."
        result = ''
        if not self.conscious:
            self.conscious = True
            hours = [roll("1d6", inline=True) for _ in range(1)]
            result = f"{name} recovers consciousness after {hours[0].total} hours."
        if self.wound == Wound.MORTAL:
            self.wound = Wound.GRIEVOUS
            result += f"\n{name} is no longer mortally wounded."
            duration -= 1
        if duration > 0 and self.wound == Wound.GRIEVOUS:
            self.wound = Wound.NORMAL
            result += f"\n{name} is no longer greviously wounded."
            duration -= 1

        if duration > 0 and duration < 7:
            result += self.recover(name, duration)
            duration = 0
        elif duration > 0:
            result += self.recover(name, 7)
            duration -= 7

        if duration > 0:
            heal_rate = 1
            if conMod > 0:
                heal_rate += conMod
            result += self.recover(name, duration * heal_rate)

        return result

    def first_aid(self, name: str, status: str, success: bool):
        if self.wound == Wound.DEAD:
            return f"Unfortunately that doesn't really help. {name} is dead."
        if self.bleeding != Bleeding.NOT_BLEEDING and success:
            self.bleeding = Bleeding.NOT_BLEEDING
            return f"{status}\n{name} has stopped bleeding."
        elif self.bleeding != Bleeding.NOT_BLEEDING:
            return f"{status}\nFirst aid was unsuccessful. {name} is still bleeding."
        elif not self.conscious and success:
            self.conscious = True
            return f"{status}\n{name} has regained consciousness."
        elif not self.conscious:
            return f"{status}\nFirst aid was unsuccessful. {name} is still unconscious."
        else:
            return f"{name} is in a stable condition. Nothing more can be achieved with first aid."

    def heal(self, name: str, hp_healed: int):
        consequence = ''
        if self.wound == Wound.DEAD:
            consequence = f"Unfortunately that doesn't really help. {name} is dead."
        elif self.wound == Wound.MORTAL:
            if self.current + hp_healed > -6:
                hp_healed = -6 - self.current
            self.current += hp_healed
            consequence = f"{name} regains {hp_healed} hit points. :medical_symbol:  **HP**: {self.current}/{self.max}"
            if self.bleeding != Bleeding.NOT_BLEEDING:
                self.bleeding = Bleeding.NOT_BLEEDING
                consequence += f"\n{name} has stopped bleeding."
            if not self.conscious:
                self.conscious = True
                consequence += f"\n{name} regains consciousness."
            if self.current == -6:
                self.wound = Wound.GRIEVOUS
                consequence += f"\n{name} is grievously wounded."
        elif self.wound == Wound.GRIEVOUS:
            if self.current + hp_healed > 0:
                hp_healed = 0 - self.current
            self.current += hp_healed
            consequence = f"{name} regains {hp_healed} hit points. :medical_symbol:  **HP**: {self.current}/{self.max}"
            if not self.conscious:
                self.conscious = True
                consequence += f"\n{name} regains consciousness."
            if self.current == 0:
                self.wound = Wound.NORMAL
                consequence += f"\n{name} is no longer grievously wounded."
        elif self.current == self.max:
            consequence = f"{name} is already at full hit points."
            self.wound = Wound.NORMAL
            self.conscious = True
        else:
            if self.current + hp_healed > self.max:
                hp_healed = self.max - self.current
            self.current += hp_healed
            consequence = f"{name} regains {hp_healed} hit points. :medical_symbol:  **HP**: {self.current}/{self.max}"
            if not self.conscious:
                self.conscious = True
                consequence += f"\n{name} regains consciousness."
        return consequence

    def lose(self, name: str, dmg: int):
        dmgtxt = f"{dmg} points"
        if dmg < 1:
            return f"{name} takes no damage!"
        elif dmg == 1:
            dmgtxt = "1 point"
        self.current -= dmg
        consequence = f"{name} takes {dmgtxt} of damage! :scream:  **HP**: {self.current}/{self.max}"
        if self.wound == Wound.DEAD:
            consequence += f"\n{name} does not care because they are already dead."
        elif self.current < -9:
            consequence += f"\n{name} dies! :skull:"
            self.wound = Wound.DEAD
        elif self.current < -6 and self.wound != Wound.MORTAL:
            consequence += f"\n{name} is mortally wounded! :grimacing:"
            self.wound = Wound.MORTAL
            self.bleeding = Bleeding.GRACE
        elif self.current < 0 and self.wound == Wound.NORMAL:
            consequence += f"\n{name} is grievously wounded! :grimacing:"
            self.wound = Wound.GRIEVOUS
        if self.conscious and self.current < 1 and self.wound != Wound.DEAD:
            consequence += f"\n{name} loses consciousness! :dizzy_face:"
            self.conscious = False
        return consequence

    def bleed(self, name):
        status = ''
        if self.wound == Wound.DEAD:
            status = f"{name} is dead."
        elif self.conscious:
            status = f"{name} is conscious but too badly wounded to act."
        elif self.wound == Wound.MORTAL:
            status = f"{name} is mortally wounded, unconscious and bleeding out."
            if self.bleeding == Bleeding.GRACE:
                self.bleeding = Bleeding.BLEEDING
            elif self.bleeding == Bleeding.BLEEDING:
                self.current -= 1
                status += f"\n{name} loses 1 hit point. :scream:  **HP**: {self.current}/{self.max}"
            elif self.bleeding == Bleeding.NOT_BLEEDING:
                status = f"{name} is mortally wounded and unconscious but the bleeding has stopped."
            if self.current < -9:
                status += f"\n{name} dies! :skull:"
                self.wound = Wound.DEAD
        else:
            status = f"{name} is unconscious."
        return status

    def brief(self):
        if self.wound == Wound.NORMAL and not self.conscious:
            wounded = ' :dizzy_face:'
        elif self.wound == Wound.GRIEVOUS or self.wound == Wound.MORTAL:
            if self.conscious:
                wounded = ' :grimacing:'
            else:
                wounded = ' :dizzy_face:'
        elif self.wound == Wound.DEAD:
            wounded = f": skull:"
        else:
            wounded = ''
        return f"{self.current}/{self.max}{wounded}"

    def __str__(self):
        if self.conscious:
            unconscious = ':grimacing:'
        else:
            unconscious = '(unconscious) :dizzy_face:'
        if self.wound == Wound.NORMAL and not self.conscious:
            wounded = f"{unconscious}"
        elif self.wound == Wound.GRIEVOUS:
            wounded = f"Grievously wounded {unconscious}"
        elif self.wound == Wound.MORTAL:
            wounded = f"Mortally wounded {unconscious}"
        elif self.wound == Wound.DEAD:
            wounded = f"DEAD :skull:"
        else:
            wounded = ''
        return f"**HP**: {self.current}/{self.max} {wounded}"

