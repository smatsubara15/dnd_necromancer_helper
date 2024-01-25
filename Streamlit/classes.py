import random
import pandas as pd
import streamlit as st

class Skeleton:
    _id_counter = 1  # Start with 1 or set this in the set_starting_id method
    
    # Class attributes for attack details
    sword_to_hit = 15
    sword_damage = 11
    bow_to_hit = 13
    bow_damage = 5

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
        self.damage_buff = 0
        self.buff_duration = 0
        self.last_roll = None
        self.num_successes = 0
        self.num_fails= 0
        self.last_action = None
        self.damage_done = 0
        Skeleton._id_counter += 1

    def attack_roll(self, armor_class, attack_type='sword'):
        # Choose the appropriate bonus and damage based on the attack type
        if attack_type == 'sword':
            bonus = Skeleton.sword_to_hit
            damage = Skeleton.sword_damage + random.randint(1,6) + int(self.damage_buff)

        elif attack_type == 'bow':
            bonus = Skeleton.bow_to_hit
            damage = Skeleton.bow_damage + random.randint(1,6) + int(self.damage_buff)
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

        self.buff_duration = max(0, self.buff_duration-1)
        if(self.buff_duration==0):
            self.damage_buff = 0

        return hit, damage, critical_hit, critical_miss,roll

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
        hits = []
        num_hits = 0
        num_crit_hits = 0
        num_crit_fails = 0

        for skel_id in attacking_skeleton_ids:
            skeleton = next((s for s in self.skeletons if s.id == skel_id), None)
            if skeleton:
                hit, damage, critical_hit, critical_miss,roll = skeleton.attack_roll(armor_class, attack_type)
                skeleton.last_roll = roll

                if critical_hit:
                    total_damage += damage
                    st.write(f"Skeleton {skeleton.id} critically hit for {damage} damage.")
                    hits.append(skel_id)
                    num_hits+=1
                    num_crit_hits+=1
                    skeleton.last_action = "Critical Hit!"
                    skeleton.num_successes += 1
                    skeleton.damage_done += damage



                elif critical_miss:
                    st.write(f"Skeleton {skeleton.id} critically missed.")
                    skeleton.last_action = "Critical Miss"
                    skeleton.num_fails += 1


                elif hit:
                    hits.append(skel_id)
                    total_damage += damage
                    num_hits += 1
                    num_crit_fails += 1
                    skeleton.num_successes += 1
                    skeleton.last_action = "Hit!"
                    skeleton.damage_done += damage

                else: 
                    skeleton.num_fails += 1
                    skeleton.last_action = "Miss"



            # else:
            #     st.write(f"No skeleton with ID {skel_id} found.")

        # Summarize which skeletons hit
        if hits:
            st.write(f"Skeletons {', '.join(map(str, hits))} hit.")
        st.write(f"{num_hits} skeletons hit for {total_damage} total damage")
    
    def group_saving_throw(self, affected_skeleton_ids, dc, potential_damage, ability_type='dexterity'):
        successes = []

        num_successes = 0
        num_crit_success = 0
        num_crit_fails = 0
        
        for skel_id in affected_skeleton_ids:
            skeleton = next((s for s in self.skeletons if s.id == skel_id), None)
            if skeleton:
                success, roll, critical_success, critical_failure = skeleton.saving_throw(dc, ability_type)
                skeleton.last_roll = roll

                if critical_success:
                    st.write(f"Skeleton {skeleton.id} rolled a 20. Critical success on the saving throw.")
                    damage = 0

                    successes.append(skel_id)
                    num_crit_success +=1
                    num_successes+=1

                    skeleton.last_action = "Critical Success!"
                    skeleton.num_successes += 1

                elif critical_failure:
                    st.write(f"Skeleton {skeleton.id} rolled a 1. Critical failure on the saving throw.")
                    damage = potential_damage
                    
                    num_crit_fails += 1
                    skeleton.num_fails += 1

                    skeleton.last_action = "Critical Failure"


                elif success:
                    successes.append(skel_id)

                    damage = potential_damage // 2
                    num_successes+=1

                    skeleton.last_action = "Successful Saving Throw"

                    skeleton.num_successes += 1


                else:
                    damage = potential_damage
                    skeleton.num_fails += 1
                    skeleton.last_action = "Failed Saving Throw"


                skeleton.current_health -= damage
                skeleton.current_health = max(skeleton.current_health, 0)

                if skeleton.current_health == 0:
                    st.write(f"Skeleton {skeleton.id} has collapsed.")

            else:
                print(f"No skeleton with ID {skel_id} found.")
        
        # Summarize which skeletons succeeded
        if successes:
            st.write(f"Skeletons {', '.join(map(str, successes))} succeeded.")

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

    def add_damage_buff(self,buff,duration):
        if ((buff!='') and (duration != '')):
            for skeleton in self.skeletons:
                skeleton.damage_buff += int(buff)
                skeleton.buff_duration = int(duration)

    def reset_buff(self):
        for skeleton in self.skeletons:
            skeleton.damage_buff = 0

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
            st.write("No skeletons in the army.")
            return
        print("Current health of the Skeleton Army:")
        for skeleton in self.skeletons:
            st.write(skeleton.display_health())
    
    def get_skeletons(self):
        return self.skeletons
