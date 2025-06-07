# mood_visualizations.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
from database import SupabaseClient
import json
import re


def extract_mood_from_entry(entry):
    """Extract mood from diary entry with multiple fallback methods"""
    # Method 1: Direct mood field
    if 'mood' in entry and entry['mood']:
        mood = str(entry['mood']).lower().strip()
        if mood and mood != 'none':
            return mood
    
    # Method 2: Check if mood is in emotions field
    if 'emotions' in entry and entry['emotions']:
        emotions = str(entry['emotions']).lower().strip()
        if emotions and emotions != 'none':
            return emotions
    
    # Method 3: Extract from entry text using common mood keywords
    text_fields = ['entry', 'content', 'text', 'description']
    for field in text_fields:
        if field in entry and entry[field]:
            text = str(entry[field]).lower()
            
            # Define mood keywords with priority (more specific first)
            mood_patterns = {
                'excited': r'\b(excited|thrilled|ecstatic|elated)\b',
                'happy': r'\b(happy|joyful|cheerful|delighted|glad)\b',
                'grateful': r'\b(grateful|thankful|blessed|appreciative)\b',
                'content': r'\b(content|satisfied|peaceful|serene)\b',
                'calm': r'\b(calm|relaxed|tranquil|composed)\b',
                'anxious': r'\b(anxious|nervous|worried|concerned|uneasy)\b',
                'stressed': r'\b(stressed|overwhelmed|pressured|tense)\b',
                'sad': r'\b(sad|down|depressed|gloomy|melancholy)\b',
                'angry': r'\b(angry|mad|furious|irritated|annoyed)\b',
                'frustrated': r'\b(frustrated|annoyed|irritated|fed up)\b',
                'tired': r'\b(tired|exhausted|weary|drained|fatigue)\b',
                'confused': r'\b(confused|uncertain|puzzled|lost)\b',
                'lonely': r'\b(lonely|isolated|alone|disconnected)\b',
                'disappointed': r'\b(disappointed|let down|discouraged)\b'
            }
            
            # Search for mood patterns
            for mood, pattern in mood_patterns.items():
                if re.search(pattern, text):
                    return mood
    
    # Method 4: Default mood based on overall sentiment
    return 'neutral'


def parse_datetime_flexible(date_string):
    """Parse datetime with multiple format support"""
    if not date_string:
        return None
        
    # Remove timezone info and clean the string
    date_string = str(date_string).strip()
    
    # Remove common timezone indicators
    date_string = re.sub(r'[+-]\d{2}:?\d{2}$', '', date_string)
    date_string = re.sub(r'Z$', '', date_string)
    
    # Try different datetime formats
    formats = [
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%d/%m/%Y %H:%M:%S',
        '%d/%m/%Y',
        '%m/%d/%Y %H:%M:%S',
        '%m/%d/%Y',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%d-%m-%Y %H:%M:%S',
        '%d-%m-%Y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    # If all formats fail, try to extract just the date part
    try:
        date_part = date_string.split('T')[0] if 'T' in date_string else date_string.split(' ')[0]
        return datetime.strptime(date_part, '%Y-%m-%d')
    except:
        return None


def prepare_mood_data(diary_entries):
    """Convert diary entries to DataFrame for visualization with robust parsing"""
    if not diary_entries:
        return None
    
    # Initialize lists for DataFrame
    dates = []
    moods = []
    timestamps = []
    
    # Enhanced mood values with more granular scoring
    mood_values = {
        # Very positive (5)
        "excited": 5, "thrilled": 5, "ecstatic": 5, "elated": 5, "joyful": 5, "euphoric": 5,
        
        # Positive (4)
        "happy": 4, "cheerful": 4, "delighted": 4, "glad": 4, "content": 4, 
        "grateful": 4, "thankful": 4, "blessed": 4, "peaceful": 4, "proud": 4,
        
        # Neutral/Calm (3)
        "calm": 3, "neutral": 3, "relaxed": 3, "tranquil": 3, "composed": 3, 
        "reflective": 3, "thoughtful": 3, "okay": 3, "fine": 3,
        
        # Slightly negative (2)
        "confused": 2, "uncertain": 2, "worried": 2, "concerned": 2, "uneasy": 2,
        "tired": 2, "weary": 2, "drained": 2, "restless": 2, "bored": 2,
        
        # Negative (1)
        "anxious": 1, "stressed": 1, "overwhelmed": 1, "sad": 1, "down": 1,
        "angry": 1, "frustrated": 1, "annoyed": 1, "lonely": 1, "isolated": 1,
        "disappointed": 1, "discouraged": 1, "depressed": 1, "furious": 1
    }
    
    # Process each entry
    for entry in diary_entries:
        try:
            # Extract timestamp
            timestamp_fields = ['created_at', 'timestamp', 'date', 'created']
            timestamp_str = None
            
            for field in timestamp_fields:
                if field in entry and entry[field]:
                    timestamp_str = entry[field]
                    break
            
            if not timestamp_str:
                continue
            
            # Parse the timestamp
            parsed_datetime = parse_datetime_flexible(timestamp_str)
            if not parsed_datetime:
                continue
            
            # Extract mood
            mood = extract_mood_from_entry(entry)
            if not mood:
                mood = 'neutral'
            
            # Add to lists
            dates.append(parsed_datetime.date())
            timestamps.append(parsed_datetime)
            moods.append(mood)
            
        except Exception:
            continue
    
    if not timestamps:
        return None
    
    # Create DataFrame
    df = pd.DataFrame({
        'date': dates,
        'timestamp': timestamps,
        'mood': moods,
        'mood_value': [mood_values.get(m.lower(), 3) for m in moods]
    })
    
    # Sort by timestamp
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    return df


def create_mood_timeline(diary_entries):
    """Create a timeline visualization of mood entries"""
    df = prepare_mood_data(diary_entries)
    if df is None or df.empty:
        st.info("📊 Not enough data to generate mood timeline. Keep logging your moods!")
        return
    
    # Create mood color mapping
    mood_colors = {
        1: "#DC3545",  # Red - Negative
        2: "#FD7E14",  # Orange - Slightly negative
        3: "#FFC107",  # Yellow - Neutral
        4: "#28A745",  # Green - Positive
        5: "#20C997"   # Teal - Very positive
    }
    
    # Create the main line chart
    fig = go.Figure()
    
    # Add line
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['mood_value'],
        mode='lines+markers',
        name='Mood Trend',
        line=dict(color='#6C757D', width=2),
        marker=dict(
            size=10,
            color=[mood_colors.get(val, "#FFC107") for val in df['mood_value']],
            line=dict(width=2, color='white')
        ),
        text=[f"Mood: {mood}<br>Date: {ts.strftime('%Y-%m-%d %H:%M')}" 
              for mood, ts in zip(df['mood'], df['timestamp'])],
        hovertemplate='%{text}<extra></extra>'
    ))
    
    # Customize layout
    fig.update_layout(
        title="Your Mood Journey Over Time",
        xaxis_title="Date",
        yaxis_title="Mood Level",
        hovermode="closest",
        height=450,
        yaxis=dict(
            tickvals=[1, 2, 3, 4, 5],
            ticktext=["😢 Negative", "😕 Low", "😐 Neutral", "😊 Good", "😄 Great"],
            range=[0.5, 5.5],
            gridcolor='rgba(128,128,128,0.2)'
        ),
        xaxis=dict(gridcolor='rgba(128,128,128,0.2)'),
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show recent trend
    if len(df) >= 2:
        recent_trend = "improving" if df.iloc[-1]['mood_value'] > df.iloc[-2]['mood_value'] else \
                     "declining" if df.iloc[-1]['mood_value'] < df.iloc[-2]['mood_value'] else "stable"
        
        trend_emoji = {"improving": "📈", "declining": "📉", "stable": "➡️"}
        st.info(f"Recent trend: {trend_emoji[recent_trend]} {recent_trend.title()}")


def create_mood_distribution(diary_entries):
    """Create a donut chart showing distribution of moods"""
    df = prepare_mood_data(diary_entries)
    if df is None or df.empty:
        st.info("📊 Not enough data to generate mood distribution.")
        return
    
    # Group moods by sentiment level
    mood_groups = {
        "Very Positive 😄": df[df['mood_value'] == 5],
        "Positive 😊": df[df['mood_value'] == 4],
        "Neutral 😐": df[df['mood_value'] == 3],
        "Low 😕": df[df['mood_value'] == 2],
        "Negative 😢": df[df['mood_value'] == 1]
    }
    
    # Create counts and colors
    labels = []
    values = []
    colors = []
    
    color_map = {
        "Very Positive 😄": "#20C997",
        "Positive 😊": "#28A745",
        "Neutral 😐": "#FFC107",
        "Low 😕": "#FD7E14",
        "Negative 😢": "#DC3545"
    }
    
    for group_name, group_df in mood_groups.items():
        count = len(group_df)
        if count > 0:
            labels.append(group_name)
            values.append(count)
            colors.append(color_map[group_name])
    
    if not values:
        st.info("No mood data available for distribution chart.")
        return
    
    # Create donut chart
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors,
        textinfo='label+percent',
        textposition='outside'
    )])
    
    fig.update_layout(
        title="Distribution of Your Moods",
        height=400,
        showlegend=True,
        legend=dict(orientation="v", x=1.05, y=0.5)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_weekly_mood_chart(diary_entries):
    """Create a heatmap of moods by day of week and time of day"""
    df = prepare_mood_data(diary_entries)
    if df is None or df.empty:
        st.info("📊 Not enough data to generate weekly mood patterns.")
        return
    
    # Add day of week and hour columns
    df['day_of_week'] = df['timestamp'].dt.day_name()
    df['hour'] = df['timestamp'].dt.hour
    
    # Create time buckets
    def get_time_bucket(hour):
        if 5 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 17:
            return 'Afternoon'
        elif 17 <= hour < 21:
            return 'Evening'
        else:
            return 'Night'
    
    df['time_bucket'] = df['hour'].apply(get_time_bucket)
    
    # Order days and times
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    time_order = ['Morning', 'Afternoon', 'Evening', 'Night']
    
    # Calculate average mood by day and time bucket
    if len(df) > 0:
        avg_mood = df.groupby(['day_of_week', 'time_bucket'])['mood_value'].mean().reset_index()
        
        # Create pivot table
        pivot_df = avg_mood.pivot(index='day_of_week', columns='time_bucket', values='mood_value')
        
        # Reorder and fill missing values
        pivot_df = pivot_df.reindex(days_order).reindex(columns=time_order)
        
        # Create heatmap
        fig = px.imshow(
            pivot_df,
            labels=dict(x="Time of Day", y="Day of Week", color="Mood Score"),
            color_continuous_scale="RdYlGn",
            aspect="auto",
            zmin=1, zmax=5
        )
        
        fig.update_layout(
            title="When Are You Happiest?",
            height=350
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data for weekly patterns analysis.")


def get_recent_mood_trend(diary_entries, days=7):
    """Calculate the mood trend over the specified days"""
    df = prepare_mood_data(diary_entries)
    if df is None or df.empty:
        return "neutral", "steady"
    
    # Filter for recent entries
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_df = df[df['timestamp'] >= cutoff_date]
    
    if recent_df.empty:
        return "neutral", "steady"
    
    # Calculate average mood
    avg_mood = recent_df['mood_value'].mean()
    
    # Determine dominant mood category
    if avg_mood >= 4.5:
        dominant_mood = "very positive"
    elif avg_mood >= 3.5:
        dominant_mood = "positive"
    elif avg_mood >= 2.5:
        dominant_mood = "neutral"
    elif avg_mood >= 1.5:
        dominant_mood = "negative"
    else:
        dominant_mood = "very negative"
    
    # Calculate trend
    if len(recent_df) >= 3:
        recent_df = recent_df.sort_values('timestamp')
        first_half_avg = recent_df.iloc[:len(recent_df)//2]['mood_value'].mean()
        second_half_avg = recent_df.iloc[len(recent_df)//2:]['mood_value'].mean()
        
        if second_half_avg > first_half_avg + 0.3:
            trend = "improving"
        elif second_half_avg < first_half_avg - 0.3:
            trend = "declining"
        else:
            trend = "steady"
    else:
        trend = "steady"
    
    return dominant_mood, trend


def create_dashboard_mood_summary(user_id):
    """Create a summary of mood data for the dashboard"""
    try:
        db = SupabaseClient()
        diary_entries = db.get_emotional_diary_history(user_id)
        
        if not diary_entries:
            st.warning("🔄 No mood data available yet. Start using the Emotional Diary to track your moods!")
            return
        
        dominant_mood, trend = get_recent_mood_trend(diary_entries)
        
        # Display current mood trend
        st.subheader("Your Recent Mood Status")
        
        # Mood indicators
        mood_data = {
            "very positive": {"emoji": "😄", "color": "#20C997", "desc": "Excellent"},
            "positive": {"emoji": "😊", "color": "#28A745", "desc": "Good"},
            "neutral": {"emoji": "😐", "color": "#FFC107", "desc": "Okay"},
            "negative": {"emoji": "😕", "color": "#FD7E14", "desc": "Low"},
            "very negative": {"emoji": "😢", "color": "#DC3545", "desc": "Struggling"}
        }
        
        trend_data = {
            "improving": {"emoji": "📈", "desc": "Getting Better"},
            "steady": {"emoji": "➡️", "desc": "Stable"},
            "declining": {"emoji": "📉", "desc": "Needs Attention"}
        }
        
        # Get mood info
        mood_info = mood_data.get(dominant_mood, mood_data["neutral"])
        trend_info = trend_data.get(trend, trend_data["steady"])
        
        # Display mood summary
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown(
                f"<div style='text-align: center; font-size: 3rem;'>{mood_info['emoji']}</div>",
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(f"**Overall Mood:** {mood_info['desc']}")
            st.markdown(f"**Trend:** {trend_info['desc']} {trend_info['emoji']}")
            
            # Count recent entries
            recent_count = len([e for e in diary_entries 
                              if (datetime.now() - parse_datetime_flexible(e.get('created_at', ''))).days <= 7
                              if parse_datetime_flexible(e.get('created_at', ''))])
            st.markdown(f"**Recent entries:** {recent_count} this week")
        
        # Mini mood chart
        df = prepare_mood_data(diary_entries)
        if df is not None and len(df) > 1:
            recent_df = df.tail(10)  # Last 10 entries
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=recent_df['timestamp'],
                y=recent_df['mood_value'],
                mode='lines+markers',
                line=dict(color=mood_info['color'], width=2),
                marker=dict(size=6, color=mood_info['color']),
                showlegend=False
            ))
            
            fig.update_layout(
                height=150,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=False, showticklabels=False, range=[0.5, 5.5]),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error loading mood summary: {str(e)}")


def display_mood_visualizations(user_id):
    """Display all mood visualizations as a single comprehensive page"""
    try:
        db = SupabaseClient()
        diary_entries = db.get_emotional_diary_history(user_id)
        
        if not diary_entries:
            st.title("🎨 Your Mood Analytics")
            st.warning("📝 No mood data available yet. Start logging your emotions to see beautiful visualizations!")
            st.info("💡 Tip: Use words like 'happy', 'sad', 'anxious', 'excited' in your diary entries, or fill out the mood field directly.")
            return

        st.title("🎨 Your Mood Analytics")
        st.markdown("*Discover patterns in your emotional journey*")
        
        # Key insights at the top
        df = prepare_mood_data(diary_entries)
        if df is not None and not df.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_mood = df['mood_value'].mean()
                st.metric("Average Mood", f"{avg_mood:.1f}/5")
            
            with col2:
                most_common_mood = df['mood'].mode().iloc[0] if not df['mood'].mode().empty else "neutral"
                st.metric("Most Common", most_common_mood.title())
            
            with col3:
                st.metric("Total Entries", len(df))
            
            with col4:
                recent_count = len(df[df['timestamp'] >= datetime.now() - timedelta(days=7)])
                st.metric("This Week", recent_count)
        
        st.markdown("---")
        
        # Main visualizations
        st.subheader("📈 Mood Timeline")
        create_mood_timeline(diary_entries)
        
        # Two column layout for distribution and patterns
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Mood Distribution")
            create_mood_distribution(diary_entries)
        
        with col2:
            st.subheader("📅 Weekly Patterns")
            create_weekly_mood_chart(diary_entries)
        
        # Insights section
        st.markdown("---")
        st.subheader("💡 Personal Insights")
        
        if df is not None and not df.empty:
            # Generate insights
            insights = []
            
            avg_mood = df['mood_value'].mean()
            if avg_mood >= 4:
                insights.append("🌟 Great job maintaining positive mental health! Keep up the good work.")
            elif avg_mood >= 3:
                insights.append("😊 You're doing well overall. Consider what activities make you happiest.")
            else:
                insights.append("🤗 Remember that it's okay to have ups and downs. Consider talking to someone you trust.")
            
            # Find best day of week
            if 'day_of_week' in df.columns:
                best_day = df.groupby('day_of_week')['mood_value'].mean().idxmax()
                insights.append(f"📅 Your happiest day tends to be {best_day}.")
            
            # Recent trend analysis
            if len(df) >= 5:
                recent_avg = df.tail(5)['mood_value'].mean()
                older_avg = df.head(5)['mood_value'].mean() if len(df) >= 10 else df.iloc[0]['mood_value']
                
                if recent_avg > older_avg + 0.5:
                    insights.append("📈 Your mood has been improving recently - that's wonderful!")
                elif recent_avg < older_avg - 0.5:
                    insights.append("📉 Your mood has been lower recently. Consider self-care activities.")
            
            # Display insights
            for insight in insights:
                st.info(insight)
        
    except Exception as e:
        st.error(f"Error displaying mood visualizations: {str(e)}")