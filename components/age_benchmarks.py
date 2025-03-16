import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def get_benchmark_data():
    """
    Get comprehensive benchmark data for different age groups and skills
    Returns a structured dictionary of skill benchmarks by age
    """
    benchmarks = {
        # Skating Skills
        'skating_speed': {
            (6, 8): {'min': 2, 'target': 3, 'advanced': 4, 'description': "Basic forward skating"},
            (9, 11): {'min': 2.5, 'target': 3.5, 'advanced': 4.5, 'description': "Developing speed"},
            (12, 14): {'min': 3, 'target': 4, 'advanced': 4.5, 'description': "Advanced speed"},
            (15, 18): {'min': 3.5, 'target': 4.5, 'advanced': 5, 'description': "Elite speed"}
        },
        'edge_control': {
            (6, 8): {'min': 1.5, 'target': 2.5, 'advanced': 3.5, 'description': "Basic balance on edges"},
            (9, 11): {'min': 2, 'target': 3, 'advanced': 4, 'description': "Improved edge work"},
            (12, 14): {'min': 3, 'target': 3.5, 'advanced': 4.5, 'description': "Refined edge control"},
            (15, 18): {'min': 3.5, 'target': 4, 'advanced': 5, 'description': "Elite edge work"}
        },
        'agility': {
            (6, 8): {'min': 1.5, 'target': 2.5, 'advanced': 3.5, 'description': "Basic turns and stops"},
            (9, 11): {'min': 2, 'target': 3, 'advanced': 4, 'description': "Quick direction changes"},
            (12, 14): {'min': 2.5, 'target': 3.5, 'advanced': 4.5, 'description': "Advanced agility"},
            (15, 18): {'min': 3, 'target': 4, 'advanced': 5, 'description': "Elite agility"}
        },
        'backward_skating': {
            (6, 8): {'min': 1, 'target': 2, 'advanced': 3, 'description': "Basic backward movement"},
            (9, 11): {'min': 2, 'target': 3, 'advanced': 4, 'description': "Comfortable backward skating"},
            (12, 14): {'min': 2.5, 'target': 3.5, 'advanced': 4.5, 'description': "Proficient backwards"},
            (15, 18): {'min': 3.5, 'target': 4, 'advanced': 5, 'description': "Elite backward skating"}
        },
        
        # Puck Skills
        'puck_control': {
            (6, 8): {'min': 1.5, 'target': 2.5, 'advanced': 3.5, 'description': "Basic puck handling"},
            (9, 11): {'min': 2, 'target': 3, 'advanced': 4, 'description': "Controlled movements"},
            (12, 14): {'min': 2.5, 'target': 3.5, 'advanced': 4.5, 'description': "Advanced control"},
            (15, 18): {'min': 3, 'target': 4, 'advanced': 5, 'description': "Elite puck handling"}
        },
        'passing_accuracy': {
            (6, 8): {'min': 1, 'target': 2, 'advanced': 3, 'description': "Basic passing"},
            (9, 11): {'min': 2, 'target': 3, 'advanced': 4, 'description': "Accurate short passes"},
            (12, 14): {'min': 2.5, 'target': 3.5, 'advanced': 4.5, 'description': "Consistent passing"},
            (15, 18): {'min': 3, 'target': 4, 'advanced': 5, 'description': "Elite passing"}
        },
        'receiving': {
            (6, 8): {'min': 1, 'target': 2, 'advanced': 3, 'description': "Basic receiving"},
            (9, 11): {'min': 2, 'target': 3, 'advanced': 4, 'description': "Clean reception"},
            (12, 14): {'min': 2.5, 'target': 3.5, 'advanced': 4.5, 'description': "Advanced receiving"},
            (15, 18): {'min': 3, 'target': 4, 'advanced': 5, 'description': "Elite reception skills"}
        },
        
        # Shooting Skills
        'wrist_shot': {
            (6, 8): {'min': 1, 'target': 2, 'advanced': 3, 'description': "Basic shot form"},
            (9, 11): {'min': 2, 'target': 3, 'advanced': 4, 'description': "Developing shot"},
            (12, 14): {'min': 2.5, 'target': 3.5, 'advanced': 4.5, 'description': "Strong wrist shot"},
            (15, 18): {'min': 3, 'target': 4, 'advanced': 5, 'description': "Elite wrist shot"}
        },
        'slap_shot': {
            (6, 8): {'min': 1, 'target': 1.5, 'advanced': 2.5, 'description': "Introduction to slap shot"},
            (9, 11): {'min': 1.5, 'target': 2.5, 'advanced': 3.5, 'description': "Developing slap shot"},
            (12, 14): {'min': 2.5, 'target': 3.5, 'advanced': 4.5, 'description': "Powerful slap shot"},
            (15, 18): {'min': 3, 'target': 4, 'advanced': 5, 'description': "Elite slap shot"}
        },
        'shot_accuracy': {
            (6, 8): {'min': 1, 'target': 2, 'advanced': 3, 'description': "Basic aim"},
            (9, 11): {'min': 2, 'target': 3, 'advanced': 4, 'description': "Improved accuracy"},
            (12, 14): {'min': 2.5, 'target': 3.5, 'advanced': 4.5, 'description': "Consistent accuracy"},
            (15, 18): {'min': 3, 'target': 4, 'advanced': 5, 'description': "Elite accuracy"}
        },
        
        # Game IQ
        'decision_making': {
            (6, 8): {'min': 1, 'target': 2, 'advanced': 3, 'description': "Basic game decisions"},
            (9, 11): {'min': 2, 'target': 3, 'advanced': 4, 'description': "Improved decisions"},
            (12, 14): {'min': 2.5, 'target': 3.5, 'advanced': 4.5, 'description': "Advanced decisions"},
            (15, 18): {'min': 3, 'target': 4, 'advanced': 5, 'description': "Elite decision-making"}
        },
        'game_awareness': {
            (6, 8): {'min': 1, 'target': 2, 'advanced': 3, 'description': "Basic awareness"},
            (9, 11): {'min': 2, 'target': 3, 'advanced': 4, 'description': "Developing awareness"},
            (12, 14): {'min': 2.5, 'target': 3.5, 'advanced': 4.5, 'description': "Strong game awareness"},
            (15, 18): {'min': 3, 'target': 4, 'advanced': 5, 'description': "Elite game awareness"}
        },
        'hockey_sense': {
            (6, 8): {'min': 1, 'target': 2, 'advanced': 3, 'description': "Basic understanding"},
            (9, 11): {'min': 2, 'target': 3, 'advanced': 4, 'description': "Developing hockey sense"},
            (12, 14): {'min': 2.5, 'target': 3.5, 'advanced': 4.5, 'description': "Advanced hockey sense"},
            (15, 18): {'min': 3, 'target': 4, 'advanced': 5, 'description': "Elite hockey sense"}
        },
        
        # Goalie Skills
        'positioning': {
            (6, 8): {'min': 1.5, 'target': 2.5, 'advanced': 3.5, 'description': "Basic positioning"},
            (9, 11): {'min': 2, 'target': 3, 'advanced': 4, 'description': "Improved positioning"},
            (12, 14): {'min': 2.5, 'target': 3.5, 'advanced': 4.5, 'description': "Advanced positioning"},
            (15, 18): {'min': 3, 'target': 4, 'advanced': 5, 'description': "Elite positioning"}
        },
        'save_technique': {
            (6, 8): {'min': 1.5, 'target': 2.5, 'advanced': 3.5, 'description': "Basic saves"},
            (9, 11): {'min': 2, 'target': 3, 'advanced': 4, 'description': "Standard techniques"},
            (12, 14): {'min': 2.5, 'target': 3.5, 'advanced': 4.5, 'description': "Advanced technique"},
            (15, 18): {'min': 3, 'target': 4, 'advanced': 5, 'description': "Elite technique"}
        },
        'rebound_control': {
            (6, 8): {'min': 1, 'target': 2, 'advanced': 3, 'description': "Basic control"},
            (9, 11): {'min': 2, 'target': 2.5, 'advanced': 3.5, 'description': "Improved control"},
            (12, 14): {'min': 2.5, 'target': 3.5, 'advanced': 4.5, 'description': "Good rebound control"},
            (15, 18): {'min': 3, 'target': 4, 'advanced': 5, 'description': "Elite rebound control"}
        }
    }
    
    return benchmarks

def get_age_appropriate_benchmark(age, metric):
    """
    Get age-appropriate benchmark values for a specific metric
    
    Args:
        age (int): Player's age
        metric (str): The skill metric to look up
        
    Returns:
        dict: Benchmark data including min, target, and description
    """
    benchmarks = get_benchmark_data()
    
    # Find appropriate age group
    for (min_age, max_age), values in benchmarks.get(metric, {}).items():
        if min_age <= age <= max_age:
            return values
            
    # Default fallback if no match found
    return {'min': 1, 'target': 3, 'advanced': 4, 'description': "Standard performance"}

def display_benchmark_comparison(player_data, metric):
    """
    Display a visual comparison of player performance against age benchmarks
    
    Args:
        player_data (dict): Player data including age and metric values
        metric (str): The skill metric to compare
    """
    age = player_data.get('age')
    current_value = player_data.get(metric, 0) or 0
    benchmark = get_age_appropriate_benchmark(age, metric)
    
    # Create a gauge chart to compare player value to benchmarks
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = current_value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"{metric.replace('_', ' ').title()} - Age {age}"},
        gauge = {
            'axis': {'range': [0, 5], 'tickwidth': 1},
            'bar': {'color': "royalblue"},
            'steps': [
                {'range': [0, benchmark['min']], 'color': "lightgray"},
                {'range': [benchmark['min'], benchmark['target']], 'color': "lightgreen"},
                {'range': [benchmark['target'], benchmark['advanced']], 'color': "green"},
                {'range': [benchmark['advanced'], 5], 'color': "darkgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': benchmark['target']
            }
        }
    ))
    
    # Add benchmark description
    st.markdown(f"**Benchmark:** {benchmark['description']}")
    st.markdown(f"**Target for age {age}:** {benchmark['target']}")
    
    # Display chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Show performance assessment
    if current_value < benchmark['min']:
        st.info("📊 **Assessment:** Below age-appropriate minimum expectations")
    elif current_value < benchmark['target']:
        st.info("📊 **Assessment:** Meeting minimum expectations for age group")
    elif current_value < benchmark['advanced']:
        st.info("📊 **Assessment:** Meeting target expectations for age group")
    else:
        st.success("📊 **Assessment:** Exceeding expectations for age group")

def display_age_benchmarks(player_data, selected_metrics=None):
    """
    Display comprehensive age benchmarks for a player
    
    Args:
        player_data (dict): Player data including age and metrics
        selected_metrics (list): Optional list of metrics to display
    """
    st.subheader("Age-Appropriate Skill Benchmarks")
    st.write("Compare player skills against age-appropriate benchmarks")
    
    # If no specific metrics provided, determine based on position
    if not selected_metrics:
        position = player_data.get('position', 'Forward')
        if position == 'Goalie':
            selected_metrics = ['positioning', 'save_technique', 'rebound_control']
        elif position == 'Defense':
            selected_metrics = ['skating_speed', 'backward_skating', 'shot_blocking']
        else:  # Forward
            selected_metrics = ['skating_speed', 'shot_accuracy', 'puck_control']
            
    # Create columns for benchmark displays
    cols = st.columns(len(selected_metrics))
    
    for i, metric in enumerate(selected_metrics):
        with cols[i]:
            if metric in player_data:
                display_benchmark_comparison(player_data, metric)
            else:
                st.warning(f"No data available for {metric.replace('_', ' ').title()}")
                
def display_all_benchmarks_by_age():
    """Display a reference table of all benchmarks by age group"""
    st.subheader("Skill Benchmarks by Age Group")
    
    # Get all benchmark data
    benchmarks = get_benchmark_data()
    
    # Create tab for each age group
    age_tabs = st.tabs(["Ages 6-8", "Ages 9-11", "Ages 12-14", "Ages 15-18"])
    
    age_ranges = [(6, 8), (9, 11), (12, 14), (15, 18)]
    
    for i, age_range in enumerate(age_ranges):
        with age_tabs[i]:
            # Group skills by category
            categories = {
                "Skating": ["skating_speed", "edge_control", "agility", "backward_skating"],
                "Puck Control": ["puck_control", "passing_accuracy", "receiving", "stick_protection"],
                "Shooting": ["wrist_shot", "slap_shot", "shot_accuracy", "one_timer"],
                "Game IQ": ["decision_making", "game_awareness", "hockey_sense"],
                "Goalie Skills": ["positioning", "save_technique", "rebound_control", "recovery"]
            }
            
            # Create tab for each skill category
            category_tabs = st.tabs(list(categories.keys()))
            
            for j, (category, skills) in enumerate(categories.items()):
                with category_tabs[j]:
                    # Create a table of benchmark values
                    benchmark_data = []
                    
                    for skill in skills:
                        if skill in benchmarks and age_range in benchmarks[skill]:
                            bm = benchmarks[skill][age_range]
                            benchmark_data.append({
                                "Skill": skill.replace("_", " ").title(),
                                "Minimum": bm.get('min', '-'),
                                "Target": bm.get('target', '-'),
                                "Advanced": bm.get('advanced', '-'),
                                "Description": bm.get('description', '-')
                            })
                            
                    if benchmark_data:
                        st.dataframe(pd.DataFrame(benchmark_data), use_container_width=True)
                    else:
                        st.info(f"No benchmark data available for {category} in this age group")