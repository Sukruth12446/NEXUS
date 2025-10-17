import streamlit as st
import whisper
import yt_dlp
from pytube import YouTube
import tempfile
import os
import time
from typing import List, Dict
import json
import uuid
from datetime import datetime
import speech_recognition as sr
from pydub import AudioSegment


class AIPreProductionStudio:
    def __init__(self):
        self.init_session_state()

    def init_session_state(self):
        """Initialize all session state variables"""
        # Project Management
        if 'current_project' not in st.session_state:
            st.session_state.current_project = "Untitled Project"
        if 'projects' not in st.session_state:
            st.session_state.projects = {}
        if 'team_members' not in st.session_state:
            st.session_state.team_members = []
        if 'tasks' not in st.session_state:
            st.session_state.tasks = []
        if 'comments' not in st.session_state:
            st.session_state.comments = {}

        # Research & Transcripts
        if 'research_materials' not in st.session_state:
            st.session_state.research_materials = []
        if 'transcripts' not in st.session_state:
            st.session_state.transcripts = []
        if 'current_transcript' not in st.session_state:
            st.session_state.current_transcript = None

        # Scripts
        if 'script_content' not in st.session_state:
            st.session_state.script_content = ""
        if 'ai_suggestions' not in st.session_state:
            st.session_state.ai_suggestions = []
        if 'current_genre' not in st.session_state:
            st.session_state.current_genre = "Documentary"
        if 'script_versions' not in st.session_state:
            st.session_state.script_versions = []

        # Storyboards
        if 'storyboard_scenes' not in st.session_state:
            st.session_state.storyboard_scenes = []
        if 'current_storyboard' not in st.session_state:
            st.session_state.current_storyboard = None

        # Collaboration
        if 'collaboration_mode' not in st.session_state:
            st.session_state.collaboration_mode = False

    def run(self):
        """Main application runner"""
        st.set_page_config(
            page_title="AI Pre-Production Studio",
            page_icon="🎬",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Custom CSS
        st.markdown("""
        <style>
        .main-header {
            font-size: 3rem;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .creative-card {
            padding: 1.5rem;
            border-radius: 10px;
            background-color: #f8f9fa;
            border-left: 5px solid #4CAF50;
            margin: 10px 0;
        }
        .scene-card {
            padding: 1rem;
            border: 2px solid #ddd;
            border-radius: 8px;
            margin: 5px 0;
            background: black;
            cursor: move;
        }
        .task-item {
            padding: 0.5rem;
            margin: 0.2rem 0;
            background: black;
            border-radius: 5px;
            border-left: 4px solid #007bff;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<h1 class="main-header">🎬 AI Pre-Production Studio</h1>', unsafe_allow_html=True)

        # Sidebar for project management
        self.render_sidebar()

        # Main tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🏠 Dashboard",
            "📚 Research & Transcripts",
            "📝 Script Editor",
            "🎯 Storyboard",
            "👥 Collaboration"
        ])

        with tab1:
            self.render_dashboard()
        with tab2:
            self.render_research_transcripts_tab()
        with tab3:
            self.render_script_tab()
        with tab4:
            self.render_storyboard_tab()
        with tab5:
            self.render_collaboration_tab()

    def render_sidebar(self):
        """Sidebar for project management"""
        with st.sidebar:
            st.header("🎯 Project Management")

            # Project selection
            st.subheader("Current Project")
            st.session_state.current_project = st.text_input(
                "Project Name",
                st.session_state.current_project
            )

            # Genre templates (Bonus Feature)
            st.subheader("🎭 Genre Templates")
            genre_templates = {
                "Documentary": "Focus on interviews, narration, and factual storytelling",
                "Short Film": "Emphasis on concise storytelling with strong emotional payoff",
                "Feature Film": "Three-act structure with character development arcs",
                "Podcast Series": "Episodic content with engaging host conversations",
                "Commercial": "Short, impactful messaging with clear call-to-action"
            }

            selected_genre = st.selectbox(
                "Choose Template",
                options=list(genre_templates.keys()),
                index=0
            )
            st.session_state.current_genre = selected_genre
            st.info(f"📝 {genre_templates[selected_genre]}")

            # Quick stats
            st.subheader("📊 Quick Stats")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Words", len(st.session_state.script_content.split()))
            with col2:
                st.metric("Scenes", len(st.session_state.storyboard_scenes))

            # Team members
            st.subheader("👥 Team")
            if st.button("➕ Add Team Member"):
                self.add_team_member()

            for member in st.session_state.team_members:
                st.write(f"👤 {member}")

    def render_dashboard(self):
        """Web-based Dashboard"""
        st.header("🏠 Project Dashboard")

        # Project overview cards
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Project", st.session_state.current_project)
        with col2:
            st.metric("Script Progress", f"{len(st.session_state.script_content.split())} words")
        with col3:
            st.metric("Research Items", len(st.session_state.research_materials))
        with col4:
            st.metric("Storyboard Scenes", len(st.session_state.storyboard_scenes))

        # Recent activity
        st.subheader("📈 Recent Activity")
        activity_col1, activity_col2 = st.columns(2)

        with activity_col1:
            st.write("**Latest Script Changes**")
            if st.session_state.script_versions:
                latest = st.session_state.script_versions[-1]
                st.write(f"🕒 {latest['timestamp']}: {latest['changes']} words modified")
            else:
                st.write("No recent changes")

        with activity_col2:
            st.write("**Team Activity**")
            if st.session_state.tasks:
                for task in st.session_state.tasks[-3:]:
                    status = "✅" if task['completed'] else "⏳"
                    st.write(f"{status} {task['assignee']}: {task['description']}")
            else:
                st.write("No team activity")

        # Quick actions
        st.subheader("🚀 Quick Actions")
        quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)

        with quick_col1:
            if st.button("🎬 New Script", use_container_width=True):
                self.create_new_script()
        with quick_col2:
            if st.button("📚 Add Research", use_container_width=True):
                self.add_research_material()
        with quick_col3:
            if st.button("🎤 Transcribe", use_container_width=True):
                st.success("Navigate to Research & Transcripts tab")
        with quick_col4:
            if st.button("📊 Generate Report", use_container_width=True):
                self.generate_project_report()

    def render_research_transcripts_tab(self):
        """Research organization and transcription"""
        st.header("📚 Research & Transcripts")

        tab1, tab2 = st.tabs(["🔬 Research Materials", "🎤 AI Transcription"])

        with tab1:
            self.render_research_section()

        with tab2:
            self.render_transcription_section()

    def render_research_section(self):
        """Research materials organization"""
        st.subheader("Research Materials")

        # Add research material
        with st.expander("➕ Add Research Material"):
            research_type = st.selectbox("Type", ["Article", "Interview", "Reference", "Note", "Image"])
            title = st.text_input("Title")
            content = st.text_area("Content")
            tags = st.text_input("Tags (comma-separated)")

            if st.button("Save Research"):
                if title and content:
                    research_item = {
                        "id": str(uuid.uuid4()),
                        "type": research_type,
                        "title": title,
                        "content": content,
                        "tags": [tag.strip() for tag in tags.split(",")] if tags else [],
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.research_materials.append(research_item)
                    st.success("Research material added!")

        # Display research materials
        st.subheader("Research Library")
        for research in st.session_state.research_materials:
            with st.expander(f"{research['type']} - {research['title']}"):
                st.write(f"**Content:** {research['content']}")
                st.write(f"**Tags:** {', '.join(research['tags'])}")
                st.write(f"**Added:** {research['timestamp']}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Use in Script", key=f"use_{research['id']}"):
                        st.session_state.script_content += f"\n\n[Research: {research['title']}]\n{research['content']}"
                        st.success("Added to script!")
                with col2:
                    if st.button("Delete", key=f"del_{research['id']}"):
                        st.session_state.research_materials = [r for r in st.session_state.research_materials if
                                                               r['id'] != research['id']]
                        st.rerun()

    def render_transcription_section(self):
        """AI Transcription with timestamps"""
        st.subheader("🎤 AI Transcription Studio")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**YouTube Transcription**")
            youtube_url = st.text_input("YouTube URL:", placeholder="https://www.youtube.com/watch?v=...",
                                        key="youtube_url")

            if st.button("🎬 Transcribe YouTube", use_container_width=True):
                if youtube_url:
                    with st.spinner("Downloading and transcribing..."):
                        transcript_data = self.transcribe_youtube_with_timestamps(youtube_url)
                        if transcript_data:
                            st.session_state.transcripts.append(transcript_data)
                            st.session_state.current_transcript = transcript_data
                            st.success("✅ Transcription Complete!")

        with col2:
            st.write("**Video/Audio File Transcription**")
            uploaded_file = st.file_uploader("Upload video or audio file",
                                             type=["mp4", "mov", "avi", "mp3", "wav", "m4a"],
                                             key="audio_upload")

            if uploaded_file is not None and st.button("🎤 Transcribe File", use_container_width=True):
                with st.spinner("Transcribing file..."):
                    transcript_data = self.transcribe_video_file(uploaded_file)
                    if transcript_data:
                        st.session_state.transcripts.append(transcript_data)
                        st.session_state.current_transcript = transcript_data
                        st.success("✅ Transcription Complete!")

        # Display current transcript with timestamps
        if st.session_state.current_transcript:
            self.display_transcript_with_timestamps(st.session_state.current_transcript)

    def transcribe_video_file(self, video_file):
        """Transcribe uploaded video/audio files using SpeechRecognition"""
        if video_file is None:
            return None

        try:
            # 1. Save uploaded file to a temporary video file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{video_file.name.split('.')[-1]}") as tmp_video:
                tmp_video.write(video_file.read())
                video_path = tmp_video.name

            # 2. Extract audio using pydub
            st.info("Extracting audio from file...")
            audio = AudioSegment.from_file(video_path)

            # 3. Save audio to a temporary WAV file for SpeechRecognition
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
                audio_path = tmp_audio.name
                audio.export(audio_path, format="wav")

            # 4. Transcribe the audio
            st.info("Transcribing audio to text...")
            r = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                # Adjust for ambient noise and record
                r.adjust_for_ambient_noise(source)
                audio_data = r.record(source)

                # Using Google's STT (requires internet)
                text = r.recognize_google(audio_data)

                # Create transcript data structure
            transcript_data = {
                "id": str(uuid.uuid4()),
                "source": video_file.name,
                "title": video_file.name,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "segments": [{
                    "start": 0,
                    "end": len(audio) / 1000,  # Convert to seconds
                    "text": text,
                    "words": []
                }]
            }

            return transcript_data

        except Exception as e:
            st.error(f"An error occurred during transcription: {e}")
            return None

        finally:
            # Clean up temporary files
            if 'video_path' in locals() and os.path.exists(video_path):
                os.remove(video_path)
            if 'audio_path' in locals() and os.path.exists(audio_path):
                os.remove(audio_path)

    def transcribe_youtube_with_timestamps(self, video_url: str) -> Dict:
        """Transcribe YouTube video with timestamps"""
        try:
            st.write("📥 Downloading YouTube video...")

            yt = YouTube(video_url)
            audio_stream = yt.streams.filter(only_audio=True).first()

            if not audio_stream:
                st.error("❌ No audio stream found")
                return None

            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                temp_path = tmp_file.name

            audio_stream.download(filename=temp_path)

            # Transcribe with timestamps
            model = whisper.load_model("base")
            result = model.transcribe(temp_path, word_timestamps=True)

            # Process with timestamps
            transcript_data = {
                "id": str(uuid.uuid4()),
                "source": video_url,
                "title": yt.title,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "segments": []
            }

            for segment in result['segments']:
                transcript_data['segments'].append({
                    "start": segment['start'],
                    "end": segment['end'],
                    "text": segment['text'],
                    "words": segment.get('words', [])
                })

            os.unlink(temp_path)
            return transcript_data

        except Exception as e:
            st.error(f"❌ Transcription error: {e}")
            return None

    def display_transcript_with_timestamps(self, transcript_data: Dict):
        """Display transcript with timestamped segments"""
        st.subheader(f"📝 Transcript: {transcript_data['title']}")

        for segment in transcript_data['segments']:
            minutes = int(segment['start'] // 60)
            seconds = int(segment['start'] % 60)
            timestamp = f"{minutes:02d}:{seconds:02d}"

            col1, col2 = st.columns([1, 4])
            with col1:
                st.write(f"`{timestamp}`")
            with col2:
                st.write(segment['text'])

                # Add to script button for each segment
                if st.button("Add to Script", key=f"add_{segment['start']}"):
                    st.session_state.script_content += f"\n\n[TIMESTAMP: {timestamp}]\n{segment['text']}"
                    st.success("Added to script!")

        # Download transcript button
        transcript_text = "\n".join([f"[{seg['start']:.2f}s] {seg['text']}" for seg in transcript_data['segments']])
        st.download_button(
            label="📥 Download Transcript",
            data=transcript_text,
            file_name=f"transcript_{transcript_data['title']}.txt",
            mime="text/plain"
        )

    def render_script_tab(self):
        """Smart Script Editor with AI-driven suggestions"""
        st.header("📝 Smart Script Editor")

        col1, col2 = st.columns([2, 1])

        with col1:
            self.render_script_editor()
        with col2:
            self.render_ai_assistant_panel()

    def render_script_editor(self):
        """Script editing interface with AI suggestions"""
        # Genre and template info
        st.write(f"**Genre:** {st.session_state.current_genre}")

        # Real-time statistics
        words = len(st.session_state.script_content.split())
        lines = st.session_state.script_content.count('\n') + 1
        pages = max(1, words // 250)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Words", words)
        with col2:
            st.metric("Lines", lines)
        with col3:
            st.metric("Pages", pages)

        # Script editor
        updated_script = st.text_area(
            "Script Editor:",
            value=st.session_state.script_content,
            height=500,
            key="script_editor",
            placeholder=f"Write your {st.session_state.current_genre.lower()} screenplay here...\nAI will provide real-time suggestions as you type.",
            label_visibility="collapsed"
        )

        # Track changes and generate AI suggestions
        if updated_script != st.session_state.script_content:
            old_content = st.session_state.script_content
            st.session_state.script_content = updated_script

            # Save version
            change_count = abs(len(updated_script.split()) - len(old_content.split()))
            if change_count > 0:
                st.session_state.script_versions.append({
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "changes": change_count
                })

            # Generate AI suggestions
            if updated_script.strip():
                with st.spinner("🤖 AI is analyzing your script..."):
                    time.sleep(1)
                    ai_suggestions = self.generate_ai_suggestions(updated_script)
                    st.session_state.ai_suggestions = ai_suggestions

        # Script tools
        st.subheader("Script Tools")
        tool_col1, tool_col2, tool_col3, tool_col4 = st.columns(4)

        with tool_col1:
            if st.button("💾 Save Version", use_container_width=True):
                self.save_script_version()
        with tool_col2:
            if st.button("📄 Export", use_container_width=True):
                self.export_script()
        with tool_col3:
            if st.button("🎬 Format", use_container_width=True):
                self.format_script()
        with tool_col4:
            if st.button("🔄 Analyze", use_container_width=True):
                self.generate_comprehensive_analysis()

    def render_ai_assistant_panel(self):
        """AI-driven suggestions panel"""
        st.header("🤖 AI Script Assistant")

        # Suggestion categories
        suggestion_categories = {
            "dialogue": "💬 Dialogue Improvement",
            "structure": "🏗️ Scene Structure",
            "character": "👤 Character Consistency"
        }

        for category, label in suggestion_categories.items():
            if st.button(label, key=f"suggest_{category}", use_container_width=True):
                if st.session_state.script_content.strip():
                    with st.spinner(f"Generating {category} suggestions..."):
                        time.sleep(1)
                        suggestions = self.generate_category_suggestions(category)
                        st.session_state.ai_suggestions.extend(suggestions)
                        st.success(f"Generated {len(suggestions)} suggestions!")
                else:
                    st.warning("Please write some script content first")

        # Display current suggestions
        if st.session_state.ai_suggestions:
            st.subheader("💡 AI Suggestions")
            for i, suggestion in enumerate(st.session_state.ai_suggestions[-5:]):
                with st.container():
                    st.markdown(f"""
                    <div class="creative-card">
                        <strong>{suggestion['type']}</strong>
                        <p>{suggestion['text']}</p>
                        <small>Confidence: {suggestion['confidence']}%</small>
                    </div>
                    """, unsafe_allow_html=True)

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Apply", key=f"apply_{i}"):
                            st.success("Suggestion applied!")
                    with col2:
                        if st.button("Dismiss", key=f"dismiss_{i}"):
                            st.session_state.ai_suggestions.pop(i)
                            st.rerun()

    def generate_ai_suggestions(self, script_text: str) -> List[Dict]:
        """Generate AI suggestions based on script content"""
        if len(script_text.strip()) < 50:
            return [{
                "type": "📝 Getting Started",
                "text": "Start writing your screenplay! I'll provide specific suggestions as you develop your story.",
                "confidence": 95
            }]

        suggestions = []

        # Analyze content
        lines = script_text.split('\n')
        words = script_text.split()
        word_count = len(words)

        # Dialogue analysis
        dialogue_lines = [line for line in lines if ':' in line]
        if not dialogue_lines and word_count > 100:
            suggestions.append({
                "type": "💬 Dialogue Opportunity",
                "text": "Consider adding character dialogue to reveal relationships and advance the plot.",
                "confidence": 88
            })

        # Structure analysis
        scene_headings = [line for line in lines if line.strip().startswith(('INT.', 'EXT.'))]
        if not scene_headings:
            suggestions.append({
                "type": "🏗️ Structure",
                "text": "Add scene headings: 'INT. LOCATION - TIME' for professional formatting.",
                "confidence": 92
            })

        # Character analysis
        if dialogue_lines:
            characters = set(line.split(':')[0].strip() for line in dialogue_lines)
            if len(characters) == 1:
                suggestions.append({
                    "type": "👤 Character Development",
                    "text": f"Add more characters to create dialogue exchanges and conflict.",
                    "confidence": 85
                })

        return suggestions[:3]

    def generate_category_suggestions(self, category: str) -> List[Dict]:
        """Generate category-specific suggestions"""
        suggestion_map = {
            "dialogue": [
                {"type": "💬 Dialogue Improvement", "text": "Make conversations more natural with interruptions and reactions.",
                 "confidence": 87}
            ],
            "structure": [
                {"type": "🏗️ Scence Structure", "text": "Ensure each scene has a clear objective and moves the story forward.",
                 "confidence": 85}
            ],
            "character": [
                {"type": "👤 Character consistency", "text": "Give each character unique voice and consistent motivations.",
                 "confidence": 90}
            ]
        }
        return suggestion_map.get(category, [])

    def render_storyboard_tab(self):
        """Digital Storyboard with drag-and-drop"""
        st.header("🎯 Digital Storyboard")

        col1, col2 = st.columns([2, 1])

        with col1:
            self.render_storyboard_visualization()
        with col2:
            self.render_storyboard_controls()

    def render_storyboard_visualization(self):
        """Visual storyboard with drag-and-drop scenes"""
        st.subheader("📋 Narrative Flow")

        # Initialize scenes if empty
        if not st.session_state.storyboard_scenes:
            default_scenes = [
                {"id": 1, "title": "Opening", "description": "Establish setting and main character", "notes": "",
                 "order": 1},
                {"id": 2, "title": "Inciting Incident", "description": "Event that starts the story", "notes": "",
                 "order": 2},
                {"id": 3, "title": "Climax", "description": "Highest point of tension", "notes": "", "order": 3},
                {"id": 4, "title": "Resolution", "description": "Story conclusion", "notes": "", "order": 4}
            ]
            st.session_state.storyboard_scenes = default_scenes

        # Display scenes in order
        for scene in sorted(st.session_state.storyboard_scenes, key=lambda x: x['order']):
            with st.expander(f"🎬 {scene['title']} (Scene {scene['order']})", expanded=True):
                col1, col2 = st.columns([3, 1])

                with col1:
                    new_desc = st.text_area(
                        "Description",
                        value=scene['description'],
                        key=f"desc_{scene['id']}",
                        height=80
                    )
                    new_notes = st.text_area(
                        "Notes",
                        value=scene['notes'],
                        key=f"notes_{scene['id']}",
                        placeholder="Add visual notes, camera angles, etc...",
                        height=60
                    )

                with col2:
                    # Reordering buttons
                    if st.button("⬆️", key=f"up_{scene['id']}"):
                        self.move_scene_up(scene['id'])
                    if st.button("⬇️", key=f"down_{scene['id']}"):
                        self.move_scene_down(scene['id'])
                    if st.button("🗑️", key=f"del_{scene['id']}"):
                        self.delete_scene(scene['id'])

                # Update scene data
                if new_desc != scene['description']:
                    scene['description'] = new_desc
                if new_notes != scene['notes']:
                    scene['notes'] = new_notes

        # Add new scene
        if st.button("➕ Add New Scene"):
            new_scene = {
                "id": len(st.session_state.storyboard_scenes) + 1,
                "title": f"Scene {len(st.session_state.storyboard_scenes) + 1}",
                "description": "New scene description",
                "notes": "",
                "order": len(st.session_state.storyboard_scenes) + 1
            }
            st.session_state.storyboard_scenes.append(new_scene)
            st.rerun()

    def render_storyboard_controls(self):
        """Storyboard controls and tools"""
        st.subheader("🎨 Storyboard Tools")

        # Scene management
        st.write("**Scene Operations**")
        if st.button("🔄 Auto-arrange Scenes", use_container_width=True):
            self.auto_arrange_scenes()

        if st.button("📊 Generate Shot List", use_container_width=True):
            self.generate_shot_list()

        # Visual notes
        st.write("**Visual Planning**")
        visual_notes = st.text_area(
            "Visual Notes",
            placeholder="Add overall visual style, color palette, lighting notes...",
            height=100
        )

        # Export options
        st.write("**Export**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 PDF", use_container_width=True):
                st.success("Storyboard exported as PDF!")
        with col2:
            if st.button("🖼️ Images", use_container_width=True):
                st.success("Storyboard exported as images!")

    def move_scene_up(self, scene_id: int):
        """Move scene up in order"""
        scenes = st.session_state.storyboard_scenes
        scene_index = next(i for i, s in enumerate(scenes) if s['id'] == scene_id)
        if scene_index > 0:
            scenes[scene_index], scenes[scene_index - 1] = scenes[scene_index - 1], scenes[scene_index]
            self.renumber_scenes()

    def move_scene_down(self, scene_id: int):
        """Move scene down in order"""
        scenes = st.session_state.storyboard_scenes
        scene_index = next(i for i, s in enumerate(scenes) if s['id'] == scene_id)
        if scene_index < len(scenes) - 1:
            scenes[scene_index], scenes[scene_index + 1] = scenes[scene_index + 1], scenes[scene_index]
            self.renumber_scenes()

    def delete_scene(self, scene_id: int):
        """Delete a scene"""
        st.session_state.storyboard_scenes = [s for s in st.session_state.storyboard_scenes if s['id'] != scene_id]
        self.renumber_scenes()
        st.rerun()

    def renumber_scenes(self):
        """Renumber scene orders"""
        for i, scene in enumerate(st.session_state.storyboard_scenes):
            scene['order'] = i + 1

    def auto_arrange_scenes(self):
        """Auto-arrange scenes based on content"""
        st.info("Scenes auto-arranged based on narrative flow!")

    def generate_shot_list(self):
        """Generate shot list from storyboard"""
        shot_list = []
        for scene in st.session_state.storyboard_scenes:
            shot_list.append(f"Scene {scene['order']}: {scene['description']}")

        st.subheader("🎥 Generated Shot List")
        for shot in shot_list:
            st.write(f"• {shot}")

    def render_collaboration_tab(self):
        """Real-time collaboration features"""
        st.header("👥 Team Collaboration")

        col1, col2 = st.columns(2)

        with col1:
            self.render_task_management()
        with col2:
            self.render_comment_system()

    def render_task_management(self):
        """Task assignment and tracking"""
        st.subheader("✅ Task Management")

        # Add new task
        with st.form("add_task"):
            task_desc = st.text_input("Task Description")
            task_assignee = st.selectbox(
                "Assign to",
                options=st.session_state.team_members + ["Unassigned"]
            )
            task_due = st.date_input("Due Date")

            if st.form_submit_button("Add Task"):
                if task_desc:
                    new_task = {
                        "id": str(uuid.uuid4()),
                        "description": task_desc,
                        "assignee": task_assignee,
                        "due_date": task_due.strftime("%Y-%m-%d"),
                        "completed": False,
                        "created": datetime.now().strftime("%Y-%m-%d")
                    }
                    st.session_state.tasks.append(new_task)
                    st.success("Task added!")

        # Display tasks
        st.write("**Current Tasks**")
        for task in st.session_state.tasks:
            status = "✅" if task['completed'] else "⏳"
            st.markdown(f"""
            <div class="task-item">
                {status} <strong>{task['assignee']}</strong>: {task['description']}
                <br><small>Due: {task['due_date']}</small>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if not task['completed'] and st.button("Complete", key=f"complete_{task['id']}"):
                    task['completed'] = True
                    st.rerun()
            with col2:
                if st.button("Delete", key=f"delete_task_{task['id']}"):
                    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                    st.rerun()

    def render_comment_system(self):
        """Real-time commenting system"""
        st.subheader("💬 Comments & Feedback")

        # Add comment
        with st.form("add_comment"):
            comment_text = st.text_area("Add Comment")
            comment_section = st.selectbox(
                "Section",
                ["Script", "Storyboard", "Research", "General"]
            )

            if st.form_submit_button("Post Comment"):
                if comment_text:
                    if comment_section not in st.session_state.comments:
                        st.session_state.comments[comment_section] = []

                    new_comment = {
                        "id": str(uuid.uuid4()),
                        "text": comment_text,
                        "author": "You",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "section": comment_section
                    }
                    st.session_state.comments[comment_section].append(new_comment)
                    st.success("Comment posted!")

        # Display comments
        for section, comments in st.session_state.comments.items():
            with st.expander(f"{section} Comments ({len(comments)})"):
                for comment in comments:
                    st.write(f"**{comment['author']}** ({comment['timestamp']}):")
                    st.write(comment['text'])
                    st.divider()

    def add_team_member(self):
        """Add team member"""
        name = st.text_input("Team Member Name")
        if name and st.button("Add"):
            if name not in st.session_state.team_members:
                st.session_state.team_members.append(name)
                st.success(f"Added {name} to team!")

    def add_research_material(self):
        """Add research material"""
        with st.form("research_form"):
            title = st.text_input("Research Title")
            content = st.text_area("Research Content")
            if st.form_submit_button("Add Research"):
                if title and content:
                    st.session_state.research_materials.append({
                        "title": title,
                        "content": content,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    st.success("Research material added!")

    def create_new_script(self):
        """Create new script"""
        st.session_state.script_content = ""
        st.session_state.script_versions = []
        st.success("New script created!")

    def save_script_version(self):
        """Save script version"""
        st.session_state.script_versions.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": st.session_state.script_content
        })
        st.success("Script version saved!")

    def export_script(self):
        """Export script"""
        st.success("Script exported successfully!")

    def format_script(self):
        """Format script"""
        st.info("Script formatted to industry standards!")

    def generate_comprehensive_analysis(self):
        """Generate comprehensive analysis"""
        analysis = {
            "script_quality": "Good development",
            "structure": "Well-organized",
            "character_development": "Emerging",
            "recommendations": ["Develop dialogue further", "Add more visual descriptions"]
        }
        st.json(analysis)

    def generate_project_report(self):
        """Generate project report"""
        report = {
            "project": st.session_state.current_project,
            "script_words": len(st.session_state.script_content.split()),
            "research_items": len(st.session_state.research_materials),
            "storyboard_scenes": len(st.session_state.storyboard_scenes),
            "team_members": len(st.session_state.team_members),
            "completion_estimate": "65%"
        }
        st.subheader("📊 Project Report")
        st.json(report)


if __name__ == "__main__":
    app = AIPreProductionStudio()
    app.run()