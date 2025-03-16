import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from datetime import datetime
import time
import plotly.graph_objects as go
from PIL import Image
import io
import base64

class VideoAnalysis:
    def __init__(self):
        # Define analysis types
        self.analysis_types = {
            'skating': {
                'name': 'Skating Technique',
                'description': 'Analyze skating stride, edge work, and overall technique',
                'metrics': ['stride_efficiency', 'edge_control', 'balance', 'power'],
                'applicable_positions': ['Forward', 'Defense', 'Goalie']
            },
            'shooting': {
                'name': 'Shooting Technique',
                'description': 'Analyze shooting mechanics, release, and follow-through',
                'metrics': ['weight_transfer', 'release_speed', 'accuracy', 'follow_through'],
                'applicable_positions': ['Forward', 'Defense']
            },
            'passing': {
                'name': 'Passing Technique',
                'description': 'Analyze passing mechanics, accuracy, and vision',
                'metrics': ['technique', 'accuracy', 'vision', 'timing'],
                'applicable_positions': ['Forward', 'Defense']
            },
            'goalie_positioning': {
                'name': 'Goalie Positioning',
                'description': 'Analyze goaltender positioning, angles, and movements',
                'metrics': ['angle_control', 'depth', 'post_integration', 'movement_efficiency'],
                'applicable_positions': ['Goalie']
            },
            'stickhandling': {
                'name': 'Stickhandling',
                'description': 'Analyze puck control, hand positioning, and stickhandling technique',
                'metrics': ['hand_position', 'head_position', 'control', 'creativity'],
                'applicable_positions': ['Forward', 'Defense']
            },
            'defensive_play': {
                'name': 'Defensive Play',
                'description': 'Analyze defensive positioning, stick placement, and gap control',
                'metrics': ['gap_control', 'stick_position', 'body_positioning', 'awareness'],
                'applicable_positions': ['Defense']
            }
        }
        
        # Define feedback templates for analyses
        self.feedback_templates = {
            'skating': {
                'stride_efficiency': {
                    'good': "Good stride efficiency with proper extension. Continue focusing on full extension and recovery.",
                    'needs_work': "Work on stride extension and full leg push. Practice one-leg skating drills to improve power."
                },
                'edge_control': {
                    'good': "Strong edge control, particularly on tight turns. Continue working on edge transitions.",
                    'needs_work': "Edge work needs improvement. Practice inside/outside edge drills and c-cuts."
                },
                'balance': {
                    'good': "Excellent balance throughout skating stride. Maintain core engagement during turns.",
                    'needs_work': "Balance issues evident during transitions. Incorporate single-leg stability exercises."
                },
                'power': {
                    'good': "Good power generation in stride. Continue building leg strength for even more explosiveness.",
                    'needs_work': "Limited power in skating stride. Focus on leg strength and proper weight transfer."
                }
            },
            'shooting': {
                'weight_transfer': {
                    'good': "Excellent weight transfer from back to front foot. Continue to emphasize this timing.",
                    'needs_work': "Improve weight transfer from back to front foot. Practice stationary shooting focusing on weight shift."
                },
                'release_speed': {
                    'good': "Quick release with good hand positioning. Work on maintaining this speed from different positions.",
                    'needs_work': "Shot release is too telegraphed. Practice quick hands and minimize preparatory motion."
                },
                'accuracy': {
                    'good': "Good shot accuracy with consistent target hitting. Continue practicing varied shooting angles.",
                    'needs_work': "Shooting accuracy needs improvement. Set up targets and focus on consistent placement."
                },
                'follow_through': {
                    'good': "Strong follow-through directing the puck. Maintain this technique for consistent results.",
                    'needs_work': "Limited follow-through affecting shot power. Practice extending through the shot."
                }
            },
            'goalie_positioning': {
                'angle_control': {
                    'good': "Excellent angle control with good awareness of shot position. Continue developing consistency.",
                    'needs_work': "Work on maintaining proper angles. Practice with visual markers to improve positioning."
                },
                'depth': {
                    'good': "Good depth management based on shooter position. Continue adjusting based on threat level.",
                    'needs_work': "Playing too deep in the crease. Work on challenging shooters appropriately based on situation."
                },
                'post_integration': {
                    'good': "Strong post integration technique. Continue refining transitions between post and active position.",
                    'needs_work': "Post integration needs improvement. Practice reverse-VH technique and transitions."
                },
                'movement_efficiency': {
                    'good': "Efficient movement patterns with minimal unnecessary motion. Continue developing this efficiency.",
                    'needs_work': "Movement contains excess motion. Focus on economy of movement and proper push technique."
                }
            }
        }
    
    def get_analysis_types_for_position(self, position):
        """Get applicable analysis types for a specific position"""
        applicable = {}
        for analysis_id, details in self.analysis_types.items():
            if position in details['applicable_positions']:
                applicable[analysis_id] = details
        return applicable
    
    def generate_feedback(self, analysis_type, metrics):
        """Generate feedback based on analysis type and metrics"""
        feedback = []
        
        if analysis_type in self.feedback_templates:
            templates = self.feedback_templates[analysis_type]
            
            for metric, score in metrics.items():
                if metric in templates:
                    if score >= 3.5:
                        feedback.append(f"**{metric.replace('_', ' ').title()}**: {templates[metric]['good']}")
                    else:
                        feedback.append(f"**{metric.replace('_', ' ').title()}**: {templates[metric]['needs_work']}")
                else:
                    # Generic feedback if no template exists
                    if score >= 3.5:
                        feedback.append(f"**{metric.replace('_', ' ').title()}**: Good performance, continue refining technique.")
                    else:
                        feedback.append(f"**{metric.replace('_', ' ').title()}**: Needs improvement. Focus on proper technique.")
        
        return feedback
    
    def perform_mock_analysis(self, video_file, analysis_type):
        """
        Perform a mock analysis on a video file
        In a real implementation, this would use computer vision to analyze technique
        """
        # Get the metrics for this analysis type
        metrics = self.analysis_types.get(analysis_type, {}).get('metrics', [])
        
        # Simulated analysis - would be replaced with actual CV analysis
        analysis_results = {}
        
        # Generate somewhat realistic random scores for demo
        np.random.seed(int(time.time()))
        for metric in metrics:
            # Generate a score between 2.0 and 4.5 to simulate realistic ratings
            score = round(np.random.uniform(2.0, 4.5), 1)
            analysis_results[metric] = score
            
        # Simulate processing time
        time.sleep(1)
        
        return analysis_results
    
    def get_improvement_drills(self, analysis_type, metrics):
        """Get recommended drills based on analysis results"""
        drills = []
        
        # Skating drills
        skating_drills = {
            'stride_efficiency': {
                'name': 'One-Leg Skating Drill',
                'description': 'Practice skating using one leg at a time to improve stride power and extension. Focus on full extension and recovery.'
            },
            'edge_control': {
                'name': 'Figure 8 Edge Work',
                'description': 'Skate in figure 8 patterns focusing on inside and outside edges, maintaining proper body position and control.'
            },
            'balance': {
                'name': 'Single Leg Balance Drill',
                'description': 'Practice balancing on one leg while moving, gradually increasing difficulty with small obstacles or changes in direction.'
            },
            'power': {
                'name': 'Explosive Starts',
                'description': 'From standstill, practice explosive first 3-5 strides focusing on power and acceleration.'
            }
        }
        
        # Shooting drills
        shooting_drills = {
            'weight_transfer': {
                'name': 'Stationary Weight Transfer',
                'description': 'Practice proper weight transfer from back to front foot during shooting without moving. Focus on timing and balance.'
            },
            'release_speed': {
                'name': 'Quick Release Drill',
                'description': 'Receive pass and immediately shoot without stickhandling, focusing on minimizing time between reception and release.'
            },
            'accuracy': {
                'name': 'Target Practice',
                'description': 'Set up targets in the net and practice hitting specific locations, gradually increasing distance and angle difficulty.'
            },
            'follow_through': {
                'name': 'Follow-Through Focus',
                'description': 'Practice shooting with exaggerated follow-through, focusing on pointing at target and finishing with stick blade direction.'
            }
        }
        
        # Goalie drills
        goalie_drills = {
            'angle_control': {
                'name': 'Angle Alignment Drill',
                'description': 'Set up markers at top of crease and practice moving between them while maintaining proper angle to the puck.'
            },
            'depth': {
                'name': 'Depth Management Drill',
                'description': 'Practice adjusting depth based on puck position - challenging shooters from slot, deeper on wide angles.'
            },
            'post_integration': {
                'name': 'Post Seal Technique',
                'description': 'Practice reverse-VH and traditional VH techniques for sealing posts in different situations.'
            },
            'movement_efficiency': {
                'name': 'Shuffle-T-Push Combo Drill',
                'description': 'Practice combinations of lateral movements, focusing on minimal excess movement and proper technique.'
            }
        }
        
        # Select appropriate drills based on analysis type and metrics
        drill_library = {
            'skating': skating_drills,
            'shooting': shooting_drills,
            'goalie_positioning': goalie_drills
        }
        
        # If we have drills for this analysis type
        if analysis_type in drill_library:
            available_drills = drill_library[analysis_type]
            
            # Recommend drills for metrics with lowest scores
            sorted_metrics = sorted(metrics.items(), key=lambda x: x[1])
            
            # Recommend up to 3 drills for lowest scoring metrics
            for metric, score in sorted_metrics:
                if score < 3.5 and metric in available_drills:
                    drills.append(available_drills[metric])
                
                if len(drills) >= 3:
                    break
        
        return drills

def display_video_upload_form(position):
    """Display the video upload form based on player position"""
    st.subheader("Upload Video for Analysis")
    
    # Initialize analysis system
    analyzer = VideoAnalysis()
    
    # Get applicable analysis types
    analysis_options = analyzer.get_analysis_types_for_position(position)
    
    if not analysis_options:
        st.warning(f"No analysis types available for position: {position}")
        return
    
    # Create selection for analysis type
    analysis_type = st.selectbox(
        "Select Analysis Type",
        options=list(analysis_options.keys()),
        format_func=lambda x: analysis_options[x]['name']
    )
    
    # Display description of selected analysis
    if analysis_type in analysis_options:
        st.info(analysis_options[analysis_type]['description'])
    
    # File uploader for video
    uploaded_file = st.file_uploader(
        "Upload Video (MP4, MOV, or MKV)",
        type=['mp4', 'mov', 'mkv']
    )
    
    # Form for additional information
    with st.form("video_analysis_form"):
        video_date = st.date_input("Date of Video", value=datetime.now())
        situation = st.selectbox(
            "Game Situation",
            options=["Practice", "Game", "Training Session", "Tryout", "Other"]
        )
        notes = st.text_area(
            "Additional Notes",
            placeholder="Provide any additional context or specific aspects you'd like analyzed..."
        )
        
        analyze_button = st.form_submit_button("Analyze Video")
        
        if analyze_button and uploaded_file is not None:
            # Show loading state during "analysis"
            with st.spinner("Analyzing video... This may take a minute..."):
                # In a real implementation, we would process the video here
                # For demo purposes, we'll simulate the analysis
                
                # Save the uploaded file temporarily
                video_bytes = uploaded_file.read()
                
                # Perform mock analysis
                analysis_results = analyzer.perform_mock_analysis(video_bytes, analysis_type)
                
                # Store analysis results in session state for display
                st.session_state.analysis_results = {
                    'file_name': uploaded_file.name,
                    'analysis_type': analysis_type,
                    'analysis_name': analysis_options[analysis_type]['name'],
                    'date': video_date,
                    'situation': situation,
                    'notes': notes,
                    'metrics': analysis_results
                }
                
                # Success indicator
                st.success("Analysis complete! See results below.")
                
                # Rerun to display results
                st.rerun()

def display_video_analysis_results():
    """Display the results of a video analysis"""
    if 'analysis_results' not in st.session_state:
        return
    
    results = st.session_state.analysis_results
    
    st.subheader("Video Analysis Results")
    st.write(f"**Video:** {results['file_name']}")
    st.write(f"**Analysis Type:** {results['analysis_name']}")
    st.write(f"**Date:** {results['date']}")
    st.write(f"**Situation:** {results['situation']}")
    
    if results['notes']:
        st.write("**Notes:**")
        st.info(results['notes'])
    
    # Initialize analyzer for feedback generation
    analyzer = VideoAnalysis()
    
    # Display metrics from analysis
    st.subheader("Technique Breakdown")
    
    # Create columns for metrics
    cols = st.columns(len(results['metrics']))
    
    for i, (metric, score) in enumerate(results['metrics'].items()):
        metric_name = metric.replace('_', ' ').title()
        
        with cols[i]:
            # Create gauge chart for score visualization
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': metric_name},
                gauge = {
                    'axis': {'range': [0, 5]},
                    'bar': {'color': "red" if score < 2.5 else "yellow" if score < 3.5 else "green"},
                    'steps': [
                        {'range': [0, 2.5], 'color': "lightgray"},
                        {'range': [2.5, 3.5], 'color': "lightyellow"},
                        {'range': [3.5, 5], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 2},
                        'thickness': 0.75,
                        'value': 3.5
                    }
                }
            ))
            
            fig.update_layout(height=200)
            st.plotly_chart(fig, use_container_width=True)
    
    # Generate feedback based on metrics
    feedback = analyzer.generate_feedback(results['analysis_type'], results['metrics'])
    
    st.subheader("Analysis Feedback")
    
    for item in feedback:
        st.write(item)
    
    # Show frame analysis with annotations (mock)
    st.subheader("Visual Analysis")
    
    # Simulated framegrab with annotations
    # In a real implementation, this would be actual frames from the video with annotations
    # Create a simulated annotated image
    if results['analysis_type'] == 'skating':
        # Use skating image
        st.image(
            "https://images.unsplash.com/photo-1562797807-aa9baed9a414",
            caption="Frame Analysis: Skating Technique",
            use_column_width=True
        )
        st.markdown("""
        **Frame Analysis:**
        - Yellow Line: Current stride path
        - Green Area: Optimal foot placement
        - Red Indicator: Area for improved knee bend
        """)
    elif results['analysis_type'] == 'shooting':
        # Use shooting image
        st.image(
            "https://images.unsplash.com/photo-1580668095823-ac452f5db744",
            caption="Frame Analysis: Shooting Technique",
            use_column_width=True
        )
        st.markdown("""
        **Frame Analysis:**
        - Blue Line: Stick flex path
        - Green Line: Weight transfer direction
        - Red Circle: Hand positioning for improved leverage
        """)
    elif results['analysis_type'] == 'goalie_positioning':
        # Use goalie image
        st.image(
            "https://images.unsplash.com/photo-1515703407324-5f753afd8be8",
            caption="Frame Analysis: Goalie Positioning",
            use_column_width=True
        )
        st.markdown("""
        **Frame Analysis:**
        - Red Lines: Angle coverage visualization
        - Blue Area: Optimal positioning zone
        - Yellow Indicators: Suggested stance adjustments
        """)
    else:
        # Generic hockey image
        st.image(
            "https://images.unsplash.com/photo-1564807387624-c6efad530083",
            caption="Frame Analysis",
            use_column_width=True
        )
    
    # Recommended drills based on analysis
    st.subheader("Recommended Improvement Drills")
    
    recommended_drills = analyzer.get_improvement_drills(
        results['analysis_type'],
        results['metrics']
    )
    
    if recommended_drills:
        for i, drill in enumerate(recommended_drills):
            with st.expander(f"Drill {i+1}: {drill['name']}", expanded=i==0):
                st.write(drill['description'])
    else:
        st.info("No specific drills to recommend based on this analysis.")
    
    # Option to save the analysis (mock functionality)
    if st.button("Save Analysis to Player Profile"):
        st.success("Analysis saved to player profile!")
        # In a real implementation, this would save to the database
        
    # Option to clear results
    if st.button("Clear Results and Upload New Video"):
        # Clear analysis results
        if 'analysis_results' in st.session_state:
            del st.session_state.analysis_results
        st.rerun()

def display_analysis_history():
    """Display a history of previously analyzed videos (mock)"""
    st.subheader("Previous Analyses")
    
    # In a real implementation, this would load from the database
    # For demo purposes, show mock data
    mock_history = [
        {
            'date': '2025-02-15',
            'type': 'Skating Technique',
            'situation': 'Practice',
            'avg_score': 3.8
        },
        {
            'date': '2025-01-20',
            'type': 'Shooting Technique',
            'situation': 'Game',
            'avg_score': 3.2
        },
        {
            'date': '2024-12-05',
            'type': 'Skating Technique',
            'situation': 'Practice',
            'avg_score': 3.5
        }
    ]
    
    # Display history table
    if mock_history:
        history_df = pd.DataFrame(mock_history)
        st.dataframe(history_df, use_container_width=True)
        
        # Create a trend chart
        if len(mock_history) > 1:
            # For demo, create a progress chart
            fig = px.line(
                history_df,
                x='date',
                y='avg_score',
                color='type',
                title="Analysis Scores Over Time",
                markers=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No previous analyses found.")

def display_video_analysis_interface(player_id, player_data):
    """Main interface for video analysis feature"""
    st.title("Video Analysis")
    st.write("Upload videos of your hockey skills for AI-assisted analysis and feedback")
    
    position = player_data.get('position', 'Forward')
    
    # Create tabs for different functions
    tabs = st.tabs(["Upload & Analyze", "Analysis Results", "Analysis History"])
    
    with tabs[0]:
        display_video_upload_form(position)
        
    with tabs[1]:
        display_video_analysis_results()
        
    with tabs[2]:
        display_analysis_history()