import random
import streamlit as st
import pandas as pd
import math
import pickle
import io
from classes import Skeleton, SkeletonArmy


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


def update_skeleton_health(army):
    army.display_army_health()
    input_str = input("Enter skeleton IDs to apply damage (e.g., '10-14, 16' or '10, 11, 13'): ")
    damage = int(input("Enter the damage each skeleton takes (use a negative number to heal): "))

    skeleton_ids = parse_skeleton_ids(input_str)
    updates = {skeleton_id: damage for skeleton_id in skeleton_ids}
    
    army.update_health(updates)

def create_and_add_skeletons():
    skeleton_army = SkeletonArmy(health=47, attack_bonus=13, dex_bonus=2)
    num_skeletons = add_skeletons_cli(skeleton_army)
    return skeleton_army,num_skeletons

def add_skeletons_cli(army):
    number_to_add = st.text_input('How many skeletons would you like to add? ')
    if number_to_add != '':
        army.add_skeletons(int(number_to_add))

    return number_to_add
    
def raise_hoard(undead_hoard):
    undead_option = st.selectbox('Which undead would you like to raise?', ['None','Skeleton'])

    if undead_option == 'Skeleton':
        if undead_option not in undead_hoard:
            army,num_skeletons = create_and_add_skeletons()
            if num_skeletons != '':
                st.write("Raised " + num_skeletons + " " + undead_option + "s to the hoard")
                undead_hoard[undead_option] = army
        else: 
            st.write('Skeleton Hoard Already Exists')
        # else: 
        #     new_skeleton_hoard = st.selectbox("Skeleton hoard already exists, would you like to delete the old group and make a new one?",['Yes','No'])
        #     if new_skeleton_hoard == 'Yes':
        #         army,num_skeletons = create_and_add_skeletons()

def add_undead(undead_hoard):
    undead_option = st.selectbox('Which undead would you like to raise?', ['None','Skeleton'])
    if undead_option == 'Skeleton':
        army = undead_hoard['Skeleton']
        num_skeletons = add_skeletons_cli(army)
        if num_skeletons != '':
            st.write("Added " + num_skeletons + " " + undead_option + "s to the hoard")


def remove_skeletons_cli(army):
    army.display_army_health()
    input_str = input("Enter the IDs of skeletons to remove (e.g., '1-5', '1,6,9'): ")
    skeleton_ids = parse_skeleton_ids(input_str)
    army.remove_skeletons(skeleton_ids)

def display_skeleton_image(skeleton,images):
    current_health = skeleton.current_health
    max_health = skeleton.max_health

    if current_health < (max_health*0.25):
        image_path = images[-1]

    elif current_health < (max_health*0.75):
        image_path = images[-2]  
    
    else: 
        image_path = images[-3]

    skeleton_label = 'Skeleton: ' + str(skeleton.id)
    skeleton_health = f'{str(current_health)}/{str(max_health)}'

    st.markdown(f'<u class="skeleton">{skeleton_label}</u> &nbsp;&nbsp;&nbsp;&nbsp;<span class="normal">{skeleton_health}</span>', unsafe_allow_html=True)   
    st.image(image_path, width=None)

    total_attempts = skeleton.num_successes + skeleton.num_fails
    if(total_attempts==0):
        hit_rate = 'NA'
    else:
        hit_rate = skeleton.num_successes / total_attempts
        hit_rate = str(round(hit_rate * 100,2))+'%'
    

    # if(skeleton.last_roll < 10):
    #     first_row_spaces = "  "
        
    st.write(f'Last Roll: {str(skeleton.last_roll)} | Last Action: {str(skeleton.last_action)}')
    st.write(f'Damage Done: {str(skeleton.damage_done)} | Success Rate: {hit_rate}')


def display_skeleton_stats(skeleton):
    total_attempts = skeleton.num_successes + skeleton.num_fails
    if(total_attempts==0):
        hit_rate = 'NA'
    else:
        hit_rate = skeleton.num_successes / total_attempts
        hit_rate = str(round(hit_rate * 100,2))+'%'

    st.write('\n')
    st.write(f"Health = {str(skeleton.current_health)}/{str(skeleton.max_health)}")
    st.write("Last Roll: " + str(skeleton.last_roll))
    st.write("Last Action: " + str(skeleton.last_action))
    st.write("Damage Done: " + str(skeleton.damage_done))
    st.write("Success Rate: " + hit_rate)
    st.write('\n')
    st.write('\n')

###########################################################################
# Streamlit APP
###########################################################################
st.set_page_config(layout="wide")

# Create font color markdown variables 
st.markdown(
    """
    <style>
    .miss_fail {
        font-size:20px !important;
        color:#FF0000 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .hit_succeed {
        font-size:20px !important;
        color:#f0f5f4 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <style>
    .crit_succeed {
        font-size:20px !important;
        color:#008000 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .crit_fail{
        font-size:20px !important;
        color:#000000 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .skeleton{
        font-size:20px !important;
        color:#B200ED !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .normal{
        font-size:20px !important;
        color:#FFFFFF !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
if 'undead_hoard' not in st.session_state:
    st.session_state['undead_hoard'] = {}

# Create a space column on the left, then the title, and then the image on the right
col_image, col_title,space, download,upload = st.columns([1,0.5,3,1,2])
title_image_path = '/Users/scottsmacbook/dnd_necromancer_helper/photos/necromancy_symbol.png'  # Replace with the actual path

with col_image:
    st.image(title_image_path)
with col_title:
    st.title("Necromancers Army")

# Use Streamlit's 'columns' layout to display buttons side by side
# col1,col2,vertical_line,outputs = st.columns([2.5,2.5,0.1,1.5])
col1,vertical_line,outputs1,space1,outputs2,space2,outputs3,space3 = st.columns([1.5,0.1,0.8,0.2,0.8,0.2,0.8,0.2])

if 'undead_hoard' in st.session_state:
    undead_hoard = st.session_state['undead_hoard']

if 'Skeleton' in undead_hoard:
    skeleton_army = undead_hoard['Skeleton']

with col1: 
    # Dropdown menu
    option = st.selectbox('What would you like to do?', ['Raise Hoard','Add Undead to Existing Hoard','Attack', 'Roll Saving Throws', 'Buff Army'])

    # Check if the user selects 'Other'
    if option == 'Raise Hoard':
        raise_hoard(st.session_state['undead_hoard'])
    
    if option == 'Add Undead to Existing Hoard':
        add_undead(st.session_state['undead_hoard'])

    if option == 'Roll Saving Throws':
        input_str = st.text_input("Enter the IDs of attacking skeletons (e.g., '1-3, 5'): ")

        if input_str.lower() == 'all':
            input_str = '1-50'

        dc = st.text_input("Enter the Difficulty Check (DC) for the saving throw: ")
        potential_damage = st.text_input("Enter the potential damage on a failed save: ")
        ability_type = st.selectbox("Enter the ability for the saving throw: ",['Strength','Dexterity','Constitution','Intelligence','Wisdom','Charisma'])

        if ((dc != '') and (input_str != '') and (potential_damage != '')):   
            affected_skeleton_ids = parse_skeleton_ids(input_str)
            if st.button("Roll"):
                skeleton_army.group_saving_throw(affected_skeleton_ids, int(dc), int(potential_damage), ability_type)

    if option == 'Attack':
        input_str = st.text_input("Enter the IDs of attacking skeletons (e.g., '1-3, 5, all'): ")
        if input_str.lower() == 'all':
            input_str = '1-50'
        armor_class = st.text_input("Enter the target's Armor Class (AC): ")
        attack_type = st.selectbox("Enter the attack type:", ['None','sword','bow'])

        if (attack_type!='None' and (input_str != '') and (armor_class != '')):
            attacking_skeleton_ids = parse_skeleton_ids(input_str)
            armor_class = int(armor_class)
            if st.button("Roll"):
                skeleton_army.group_attack(attacking_skeleton_ids, armor_class, attack_type)

    if option == 'Buff Army':
        damage_buff = st.text_input("Enter the damage buff: ")
        duration = st.text_input("Enter the duration of the buff: ")
        if st.button("Apply Buff"):
            skeleton_army.add_damage_buff(damage_buff,duration)
            st.write(f'Added a damage buff of {damage_buff} to the army')

        if st.button("Reset Buff"):
            skeleton_army.reset_buff()

    
healthy_skelly_image_path = '/Users/scottsmacbook/dnd_necromancer_helper/photos/Health Skeleton.png'
damaged_skelly_image_path = '/Users/scottsmacbook/dnd_necromancer_helper/photos/Damaged Skeleton.png'
almost_dead_skelly_image_path = '/Users/scottsmacbook/dnd_necromancer_helper/photos/Nearly Defeated Skeleton.png'

images = []
images.append(healthy_skelly_image_path)
images.append(damaged_skelly_image_path)
images.append(almost_dead_skelly_image_path)



with download:
    if 'undead_hoard' in st.session_state:
        if st.button("Convert Data to pkl"):
        # Serialize the object
            buffer = io.BytesIO()
            pickle.dump(undead_hoard, buffer)
            buffer.seek(0)
            st.download_button(
                label="Download Army Data",
                data=buffer,
                file_name="unead_army.pkl",
                mime="application/octet-stream"
            )
        
with upload:
    uploaded_file = st.file_uploader("Upload Undead Army pkl File", type=["pkl"])
    if ((uploaded_file is not None) and ('file_uploaded' not in st.session_state)) :
        st.session_state['undead_hoard'] = pickle.load(uploaded_file)
        undead_hoard = st.session_state['undead_hoard']
        st.session_state['file_uploaded'] = True


if 'Skeleton' in undead_hoard:
    skeleton_army = undead_hoard['Skeleton']
    skeletons = skeleton_army.get_skeletons()
    num_skeletons = len(skeletons)
    num_rows = int(math.ceil(num_skeletons/3))

    with vertical_line:
        num_line_pixels = 450*num_rows
        line_len = str(num_line_pixels)+'px'
        st.markdown(f'<div style="border-left: 2px solid #808080; height: {line_len}"></div>', unsafe_allow_html=True)

    with outputs1:
        group_1 = skeletons[0::3]
        for skeleton in group_1:
            display_skeleton_image(skeleton,images)
    
    with outputs2: 
        group_2 = skeletons[1::3]
        for skeleton in group_2:
            display_skeleton_image(skeleton,images)


    with outputs3:
        group_3 = skeletons[2::3]
        for skeleton in group_3:
            display_skeleton_image(skeleton,images)
