import random

class Skeleton:
    _id_counter = 1  # Start with 1 or set this in the set_starting_id method
    
    # Class attributes for attack details
    sword_to_hit = 15
    sword_damage = 14
    bow_to_hit = 13
    bow_damage = 8

    # Adding ability score bonuses
    ability_bonuses = {
        'strength': +2,
        'dexterity': +2,
        'constitution': +2,
        'intelligence': +2,
        'wisdom': -1,
        'charisma': -3
    }

    @classmethod
    def set_starting_id(cls, starting_id):
        cls._id_counter = starting_id

    def __init__(self, max_health, attack_bonus, dex_bonus):
        if Skeleton._id_counter is None:
            raise ValueError("Starting ID has not been set.")
        self.id = Skeleton._id_counter
        self.max_health = max_health
        self.current_health = max_health
        self.attack_bonus = attack_bonus
        self.dex_bonus = dex_bonus
        Skeleton._id_counter += 1

    def attack_roll(self, armor_class, attack_type='sword'):
        # Choose the appropriate bonus and damage based on the attack type
        if attack_type == 'sword':
            bonus = Skeleton.sword_to_hit
            damage = Skeleton.sword_damage
        elif attack_type == 'bow':
            bonus = Skeleton.bow_to_hit
            damage = Skeleton.bow_damage
        else:
            raise ValueError(f"Unknown attack type: {attack_type}")

        roll = random.randint(1, 20)
        critical_hit = roll == 20
        critical_miss = roll == 1

        if critical_hit:
            # If it's a critical hit, we double the damage
            damage *= 2
            hit = True  # A natural 20 is always a hit
        elif critical_miss:
            hit = False  # A natural 1 is always a miss
        else:
            hit = roll + bonus >= armor_class

        return hit, damage, critical_hit, critical_miss

    def saving_throw(self, dc, ability_type='dexterity'):
        # Fetch the correct bonus for the saving throw based on ability_type
        bonus = self.ability_bonuses.get(ability_type, 0)
        roll = random.randint(1, 20)
        critical_success = roll == 20
        critical_failure = roll == 1

        # Automatic success on a natural 20 and automatic failure on a natural 1
        success = critical_success or (roll + bonus >= dc) if not critical_failure else False
        return success, roll, critical_success, critical_failure
    
    def display_health(self):
        return f"Skeleton {self.id}: Health = {self.current_health}/{self.max_health}"
    
class SkeletonArmy:
    def __init__(self, health, attack_bonus, dex_bonus):
        self.skeletons = []
        self.max_health = health
        self.attack_bonus = attack_bonus
        self.dex_bonus = dex_bonus

    def add_skeletons(self, count):
        for _ in range(count):
            new_skeleton = Skeleton(self.max_health, self.attack_bonus, self.dex_bonus)
            self.skeletons.append(new_skeleton)
            print(new_skeleton.display_health())
        print(f"Total number of skeletons: {len(self.skeletons)}.")

    def display_army_for_removal(self):
        if not self.skeletons:
            print("No skeletons in the army.")
            return
        print("Skeletons available for removal:")
        for skeleton in self.skeletons:
            print(skeleton.display_health())

    def remove_skeletons(self, skeleton_ids):
        collapsed_skeletons_ids = []
        for skel_id in skeleton_ids:
            skeleton = next((s for s in self.skeletons if s.id == skel_id), None)
            if skeleton:
                self.skeletons.remove(skeleton)
                collapsed_skeletons_ids.append(skel_id)
                print(f"Skeleton {skel_id} has been removed.")
            else:
                print(f"No skeleton with ID {skel_id} found.")
        if collapsed_skeletons_ids:
            print(f"Removed skeletons with IDs: {collapsed_skeletons_ids}")
        else:
            print("No skeletons were removed.")

        # Display the health of the remaining skeletons
        self.display_army_health()

    def group_attack(self, attacking_skeleton_ids, armor_class, attack_type='sword'):
        total_damage = 0
        critical_hits = []
        critical_misses = []
        for skel_id in attacking_skeleton_ids:
            skeleton = next((s for s in self.skeletons if s.id == skel_id), None)
            if skeleton:
                hit, damage, critical_hit, critical_miss = skeleton.attack_roll(armor_class, attack_type)
                if critical_hit:
                    critical_hits.append(skeleton.id)
                    total_damage += damage
                    print(f"Skeleton {skeleton.id} critically hit for {damage} damage.")
                elif critical_miss:
                    critical_misses.append(skeleton.id)
                    print(f"Skeleton {skeleton.id} critically missed.")
                elif hit:
                    total_damage += damage
                    print(f"Skeleton {skeleton.id} hit for {damage} damage.")
                else:
                    print(f"Skeleton {skeleton.id} missed.")
            else:
                print(f"No skeleton with ID {skel_id} found.")

        # Summarize critical hits and misses
        if critical_hits:
            print(f"Skeletons {', '.join(map(str, critical_hits))} critically hit.")
        if critical_misses:
            print(f"Skeletons {', '.join(map(str, critical_misses))} critically missed.")

        print(f"Total damage dealt by all attacking skeletons: {total_damage}")
    
    def group_saving_throw(self, affected_skeleton_ids, dc, potential_damage, ability_type='dexterity'):
        critical_successes = []
        critical_failures = []
        for skel_id in affected_skeleton_ids:
            skeleton = next((s for s in self.skeletons if s.id == skel_id), None)
            if skeleton:
                success, roll, critical_success, critical_failure = skeleton.saving_throw(dc, ability_type)

                if critical_success:
                    critical_successes.append(skeleton.id)
                elif critical_failure:
                    critical_failures.append(skeleton.id)
                    
                if critical_success:
                    print(f"Skeleton {skeleton.id} rolled a 20. Critical success on the saving throw.")
                    damage = potential_damage // 2
                elif critical_failure:
                    print(f"Skeleton {skeleton.id} rolled a 1. Critical failure on the saving throw.")
                    damage = potential_damage
                elif success:
                    print(f"Skeleton {skeleton.id} succeeded the saving throw and takes {potential_damage // 2} damage.")
                    damage = potential_damage // 2
                else:
                    print(f"Skeleton {skeleton.id} failed the saving throw and takes {potential_damage} damage.")
                    damage = potential_damage

                skeleton.current_health -= damage
                skeleton.current_health = max(skeleton.current_health, 0)

                if skeleton.current_health == 0:
                    print(f"Skeleton {skeleton.id} has collapsed.")

            else:
                print(f"No skeleton with ID {skel_id} found.")

        # Summarize critical successes and failures
        if critical_successes:
            print(f"Skeletons {', '.join(map(str, critical_successes))} critically succeeded.")
        if critical_failures:
            print(f"Skeletons {', '.join(map(str, critical_failures))} critically failed.")
        
        self.skeletons = [skeleton for skeleton in self.skeletons if skeleton.current_health > 0]
        self.display_army_health()

    def update_health(self, updates):
        collapsed_skeletons = []
        for skeleton_id, damage in updates.items():
            # Find the skeleton with the matching ID
            skeleton = next((skel for skel in self.skeletons if skel.id == skeleton_id), None)
            if skeleton:
                skeleton.current_health -= damage
                if skeleton.current_health <= 0:
                    collapsed_skeletons.append(skeleton)
        
        # Remove collapsed skeletons and print a message for each
        for skeleton in collapsed_skeletons:
            self.skeletons.remove(skeleton)
            print(f"Skeleton {skeleton.id} has collapsed.")

        # Display the health of the remaining skeletons
        self.display_army_health()

    def add_skeleton(self):
        self.skeletons.append(Skeleton(self.health, self.attack_bonus, self.dex_bonus))
        print(f"One skeleton added. Total number of skeletons: {len(self.skeletons)}.")

    def remove_skeleton(self):
        if self.skeletons:
            self.skeletons.pop()
            print(f"One skeleton removed. Total number of skeletons: {len(self.skeletons)}.")
        else:
            print("No skeletons to remove.")
            
    def display_army_health(self):
        if not self.skeletons:
            print("No skeletons in the army.")
            return
        print("Current health of the Skeleton Army:")
        for skeleton in self.skeletons:
            print(skeleton.display_health())

#Main Menu

def main_menu():
    print("\nNecromancer's Skeleton Army Manager")
    print("1. Add Skeletons to the Army")
    print("2. Remove Skeletons from the Army")
    print("3. Attack with Skeleton Army")
    print("4. Roll Saving Throws for Skeleton Army")
    print("5. Display Army Health")
    print("6. Update Skeleton Health")
    print("7. Quit")
    choice = input("Enter your choice: ")
    return choice

    choice = input("Enter your choice: ")
    return choice

#CLI

def set_starting_skeleton_id():
    starting_id = int(input("Enter the starting ID for skeletons: "))
    Skeleton.set_starting_id(starting_id)

def parse_skeleton_ids(input_str):
    """
    Parses a string input to extract skeleton IDs.
    Supports ranges indicated by a hyphen and lists separated by commas.
    """
    skeleton_ids = []
    parts = input_str.split(',')
    for part in parts:
        if '-' in part:
            start, end = map(int, part.split('-'))
            skeleton_ids.extend(range(start, end + 1))
        else:
            skeleton_ids.append(int(part))
    return skeleton_ids

def attack_with_army(army):
    input_str = input("Enter the IDs of attacking skeletons (e.g., '1-3, 5'): ")
    armor_class = int(input("Enter the target's Armor Class (AC): "))
    attack_type = input("Enter the attack type (sword/bow): ")

    attacking_skeleton_ids = parse_skeleton_ids(input_str)
    army.group_attack(attacking_skeleton_ids, armor_class, attack_type)

def roll_saving_throws(army):
    input_str = input("Enter the IDs of skeletons making a saving throw (e.g., '1-3, 5'): ")
    ability_type = input("Enter the ability for the saving throw (strength, dexterity, etc.): ").lower()
    dc = int(input("Enter the Difficulty Check (DC) for the saving throw: "))
    potential_damage = int(input("Enter the potential damage on a failed save: "))

    affected_skeleton_ids = parse_skeleton_ids(input_str)
    army.group_saving_throw(affected_skeleton_ids, dc, potential_damage, ability_type)

def update_skeleton_health(army):
    army.display_army_health()
    input_str = input("Enter skeleton IDs to apply damage (e.g., '10-14, 16' or '10, 11, 13'): ")
    damage = int(input("Enter the damage each skeleton takes (use a negative number to heal): "))

    skeleton_ids = parse_skeleton_ids(input_str)
    updates = {skeleton_id: damage for skeleton_id in skeleton_ids}
    
    army.update_health(updates)

def add_skeletons_cli(army):
    count = int(input("How many skeletons would you like to add? "))
    army.add_skeletons(count)

def remove_skeletons_cli(army):
    army.display_army_health()
    input_str = input("Enter the IDs of skeletons to remove (e.g., '1-5', '1,6,9'): ")
    skeleton_ids = parse_skeleton_ids(input_str)
    army.remove_skeletons(skeleton_ids)

def main():
    set_starting_skeleton_id()  # Set the starting ID at the beginning of the program
    army = SkeletonArmy(health=47, attack_bonus=13, dex_bonus=2)  # Default sta

    while True:
        choice = main_menu()
        if choice == '1':
            add_skeletons_cli(army)
        elif choice == '2':
            remove_skeletons_cli(army)
        elif choice == '3':
            attack_with_army(army)
        elif choice == '4':
            roll_saving_throws(army)
        elif choice == '5':
            army.display_army_health()
        elif choice == '6':
            update_skeleton_health(army)
        elif choice == '7':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice or no army created yet.")

if __name__ == "__main__":
    main()


