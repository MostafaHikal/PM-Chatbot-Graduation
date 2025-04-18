import streamlit as st
from utils import setup_openai, process_guided_questionnaire, process_direct_question
from prompts import (
    WELCOME_MESSAGE, PM_GUIDED_QUESTIONS, GP_GUIDED_QUESTIONS,
    PROJECT_MANAGEMENT_ASPECTS, GRADUATION_PROJECT_CATEGORIES
)

# Page configuration
st.set_page_config(
    page_title="مساعد المشاريع الذكي",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply right-to-left alignment for Arabic text
st.markdown(
    """
    <style>
    body {
        direction: rtl;
        text-align: right;
    }
    .element-container, .stTextInput, .stButton, .stSelectbox, .stRadio {
        direction: rtl;
        text-align: right;
    }
    .stMarkdown {
        direction: rtl;
        text-align: right;
    }
    button {
        direction: rtl;
        text-align: right;
    }
    .css-1cpxqw2 {
        direction: rtl;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize API
setup_openai()

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_mode" not in st.session_state:
    st.session_state.chat_mode = None

if "project_type" not in st.session_state:
    st.session_state.project_type = None

if "questionnaire_step" not in st.session_state:
    st.session_state.questionnaire_step = 0

if "questionnaire_responses" not in st.session_state:
    st.session_state.questionnaire_responses = {}

if "welcome_shown" not in st.session_state:
    st.session_state.welcome_shown = False


def display_welcome():
    """Display welcome message and mode selection"""
    st.markdown("<h1 style='text-align: center;'>مساعد المشاريع الذكي</h1>", unsafe_allow_html=True)
    
    # Display welcome message
    st.markdown(f"<div style='direction: rtl; text-align: right;'>{WELCOME_MESSAGE}</div>", unsafe_allow_html=True)
    
    # Mode selection
    st.markdown("<h3>اختر طريقة التفاعل:</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("الاستبيان الموجه", use_container_width=True):
            st.session_state.chat_mode = "guided"
            st.session_state.questionnaire_step = 0
            st.session_state.questionnaire_responses = {}
            st.rerun()
    
    with col2:
        if st.button("الطريقة المباشرة", use_container_width=True):
            st.session_state.chat_mode = "direct"
            welcome_msg = "مرحباً بك في نمط الطريقة المباشرة. يمكنك الآن طرح سؤالك مباشرة حول إدارة المشاريع البرمجية أو مشاريع التخرج، وسأقوم بمساعدتك."
            st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
            st.rerun()


def run_guided_questionnaire():
    """Run the guided questionnaire mode"""
    # Determine context based on previous answers
    if not st.session_state.project_type and st.session_state.questionnaire_step == 0:
        # First question determines project type
        st.markdown("<h2 style='text-align: center;'>الاستبيان الموجه</h2>", unsafe_allow_html=True)
        st.markdown("<h3 style='direction: rtl; text-align: right;'>ما هو مجال اهتمامك؟</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("إدارة المشاريع البرمجية", use_container_width=True):
                st.session_state.project_type = "pm"
                st.session_state.questionnaire_step = 1
                st.rerun()
        with col2:
            if st.button("مشاريع التخرج", use_container_width=True):
                st.session_state.project_type = "gp"
                st.session_state.questionnaire_step = 1
                st.rerun()
        return
    
    # Get appropriate questions based on project type
    project_type = st.session_state.project_type
    questions = PM_GUIDED_QUESTIONS if project_type == "pm" else GP_GUIDED_QUESTIONS
    
    title = "الاستبيان الموجه"
    st.markdown(f"<h2 style='text-align: center;'>{title}</h2>", unsafe_allow_html=True)
    
    # List of questions in order
    questions_order = list(questions.keys())
    
    # Display progress bar
    progress = (st.session_state.questionnaire_step - 1) / len(questions_order)
    st.progress(progress)
    
    # Display current question (subtract 1 because step 0 was used for project type selection)
    current_step = st.session_state.questionnaire_step - 1
    if current_step < len(questions_order):
        current_field = questions_order[current_step]
        current_question = questions[current_field]
        
        st.markdown(f"<h3 style='direction: rtl; text-align: right;'>{current_question}</h3>", unsafe_allow_html=True)
        
        # Project management specific handlers
        if project_type == "pm":
            # Special case for experience (radio)
            if current_field == "experience":
                experience = st.radio("", ["مبتدئ", "متوسط", "متقدم"], index=1, key="experience_radio")
                if st.button("التالي", key="next_experience"):
                    st.session_state.questionnaire_responses[current_field] = experience
                    st.session_state.questionnaire_step += 1
                    st.rerun()
                
            # Special case for project_type (dropdown)
            elif current_field == "project_type":
                project_type_options = ["تطوير برمجيات", "تطوير تطبيقات موبايل", "تطوير مواقع", "تطوير واجهات مستخدم", 
                                      "تطوير واجهات برمجة التطبيقات", "تطوير قواعد بيانات", "تطوير ذكاء اصطناعي", 
                                      "تطوير أمن معلومات", "تطوير ألعاب", "تطوير أنظمة مدمجة", "تطوير خدمات سحابية", 
                                      "تطوير DevOps", "تطوير Blockchain", "تطوير IoT", "تطوير AR/VR", "أخرى"]
                project_type_val = st.selectbox("", project_type_options, index=0, key="project_type_select")
                if st.button("التالي", key="next_project_type"):
                    st.session_state.questionnaire_responses[current_field] = project_type_val
                    st.session_state.questionnaire_step += 1
                    st.rerun()
                    
            # Special case for team size (number input)
            elif current_field == "team_size":
                team_size = st.number_input("", min_value=1, max_value=100, value=5, step=1, key="team_size_input")
                if st.button("التالي", key="next_team_size"):
                    st.session_state.questionnaire_responses[current_field] = str(team_size)
                    st.session_state.questionnaire_step += 1
                    st.rerun()
                    
            # Special case for project_phase (radio)
            elif current_field == "project_phase":
                project_phase = st.radio("", ["التخطيط", "التطوير", "الاختبار", "النشر", "الصيانة", "التقييم", "الإغلاق"], index=0, key="project_phase_radio")
                if st.button("التالي", key="next_project_phase"):
                    st.session_state.questionnaire_responses[current_field] = project_phase
                    st.session_state.questionnaire_step += 1
                    st.rerun()
                    
            # Special case for methodology (dropdown)
            elif current_field == "methodology":
                methodology = st.selectbox("", ["أجايل", "ووترفول", "هجين", "Scrum", "Kanban", "Lean", "DevOps", "Six Sigma", "Prince2", "PMP", "ITIL", "COBIT", "أخرى"], index=0, key="methodology_select")
                if st.button("التالي", key="next_methodology"):
                    st.session_state.questionnaire_responses[current_field] = methodology
                    st.session_state.questionnaire_step += 1
                    st.rerun()
                    
            # For other fields (text input)
            else:
                user_input = st.text_area("", key=f"input_{current_field}", height=100)
                if st.button("التالي", key=f"next_{current_field}"):
                    st.session_state.questionnaire_responses[current_field] = user_input
                    st.session_state.questionnaire_step += 1
                    st.rerun()
                    
        # Graduation project specific handlers
        else:
            # Special case for field_of_study (dropdown)
            if current_field == "field_of_study":
                fields = ["علوم الحاسوب", "هندسة البرمجيات", "هندسة الحاسوب", "نظم المعلومات", 
                        "تكنولوجيا المعلومات", "الذكاء الاصطناعي", "علم البيانات", "أمن المعلومات",
                        "الشبكات", "هندسة كهربائية", "هندسة الاتصالات", "هندسة إلكترونية", "أخرى"]
                field = st.selectbox("", fields, index=0, key="field_study_select")
                if st.button("التالي", key="next_field"):
                    st.session_state.questionnaire_responses[current_field] = field
                    st.session_state.questionnaire_step += 1
                    st.rerun()
                    
            # Special case for team_size (number input)
            elif current_field == "team_size":
                team_size = st.number_input("", min_value=1, max_value=10, value=3, step=1, key="gp_team_size_input")
                if st.button("التالي", key="next_team_size"):
                    st.session_state.questionnaire_responses[current_field] = str(team_size)
                    st.session_state.questionnaire_step += 1
                    st.rerun()
                    
            # Special case for duration (radio)
            elif current_field == "duration":
                duration = st.radio("", ["فصل دراسي واحد", "فصلين دراسيين", "سنة كاملة"], index=1, key="duration_radio")
                if st.button("التالي", key="next_duration"):
                    st.session_state.questionnaire_responses[current_field] = duration
                    st.session_state.questionnaire_step += 1
                    st.rerun()
                    
            # Special case for preferences (radio)
            elif current_field == "preferences":
                preference = st.radio("", ["مشروع عملي", "مشروع بحثي", "مزيج من الاثنين"], index=0, key="preferences_radio")
                if st.button("التالي", key="next_preferences"):
                    st.session_state.questionnaire_responses[current_field] = preference
                    st.session_state.questionnaire_step += 1
                    st.rerun()
                    
            # For other fields (text input)
            else:
                user_input = st.text_area("", key=f"input_{current_field}", height=100)
                if st.button("التالي", key=f"next_{current_field}"):
                    st.session_state.questionnaire_responses[current_field] = user_input
                    st.session_state.questionnaire_step += 1
                    st.rerun()
        
        # Add back button if not on the first question
        if st.session_state.questionnaire_step > 1:
            if st.button("السابق", key="back_button"):
                st.session_state.questionnaire_step -= 1
                st.rerun()
    
    # When all questions have been answered
    else:
        # Display summary of responses
        st.markdown("<h3>ملخص إجاباتك:</h3>", unsafe_allow_html=True)
        
        questions_dict = PM_GUIDED_QUESTIONS if st.session_state.project_type == "pm" else GP_GUIDED_QUESTIONS
        for field in st.session_state.questionnaire_responses:
            st.markdown(f"<p><strong>{questions_dict.get(field, field)}</strong> {st.session_state.questionnaire_responses.get(field, '')}</p>", unsafe_allow_html=True)
        
        # Generate advice button
        button_text = "توليد النصائح والإرشادات" 
        if st.button(button_text, key="generate_advice"):
            with st.spinner("جاري التوليد..."):
                response = process_guided_questionnaire(
                    st.session_state.questionnaire_responses, 
                    project_type=st.session_state.project_type
                )
                
                # Save to chat history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response
                })
                
                # Switch to direct mode after generating advice
                st.session_state.chat_mode = "direct"
                st.rerun()
        
        # Start over button
        if st.button("بدء الاستبيان من جديد", key="restart"):
            st.session_state.questionnaire_step = 0
            st.session_state.questionnaire_responses = {}
            st.session_state.project_type = None
            st.rerun()


def run_direct_mode():
    """Run the direct question mode"""
    st.markdown(f"<h2 style='text-align: center;'>مساعد المشاريع الذكي</h2>", unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # User input
    user_input = st.chat_input("اكتب سؤالك هنا...")
    
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("جاري التفكير..."):
                # Format chat history for API
                chat_history = []
                if len(st.session_state.messages) > 1:
                    for msg in st.session_state.messages[:-1]:  # Exclude current user message
                        if msg["role"] == "user":
                            chat_history.append({"role": "user", "content": msg["content"]})
                        else:
                            chat_history.append({"role": "assistant", "content": msg["content"]})
                
                # Determine project type based on question content if not set already
                if not st.session_state.project_type:
                    # Simple keyword detection
                    pm_keywords = ["إدارة المشروع", "مدير المشروع", "الجدول الزمني", "المخاطر", "الميزانية", "فريق العمل", "أصحاب المصلحة"]
                    gp_keywords = ["مشروع التخرج", "مشاريع التخرج", "أفكار", "فكرة مشروع", "تخرجي", "دراستي"]
                    
                    pm_count = sum(1 for kw in pm_keywords if kw in user_input)
                    gp_count = sum(1 for kw in gp_keywords if kw in user_input)
                    
                    # Set project type based on keyword count, defaulting to both if unclear
                    project_type = "pm" if pm_count > gp_count else "gp" if gp_count > pm_count else "pm"  # Default to PM if equal
                else:
                    project_type = st.session_state.project_type
                
                response = process_direct_question(
                    user_input, 
                    chat_history=chat_history if chat_history else None, 
                    project_type=project_type
                )
                st.markdown(response)
                
                # Add assistant message to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})


def display_sidebar():
    """Display sidebar with mode switching options"""
    with st.sidebar:
        st.markdown("<h2 style='text-align: center;'>الإعدادات</h2>", unsafe_allow_html=True)
        
        # Project area selection
        st.markdown("### تغيير مجال المساعدة")
        
        if st.button("إدارة المشاريع البرمجية", key="switch_to_pm", use_container_width=True):
            st.session_state.project_type = "pm"
            if st.session_state.chat_mode == "guided":
                st.session_state.questionnaire_step = 1  # Skip the initial project selection
                st.session_state.questionnaire_responses = {}
            st.rerun()
            
        if st.button("مشاريع التخرج", key="switch_to_gp", use_container_width=True):
            st.session_state.project_type = "gp"
            if st.session_state.chat_mode == "guided":
                st.session_state.questionnaire_step = 1  # Skip the initial project selection
                st.session_state.questionnaire_responses = {}
            st.rerun()
        
        # Mode switching
        st.markdown("### تغيير طريقة التفاعل")
        
        if st.button("الاستبيان الموجه", key="switch_to_guided", use_container_width=True):
            st.session_state.chat_mode = "guided"
            # Only reset questionnaire if no project type selected
            if st.session_state.project_type:
                st.session_state.questionnaire_step = 1
            else:
                st.session_state.questionnaire_step = 0
            st.session_state.questionnaire_responses = {}
            st.rerun()
            
        if st.button("الطريقة المباشرة", key="switch_to_direct", use_container_width=True):
            st.session_state.chat_mode = "direct"
            if not st.session_state.messages:
                welcome_msg = "مرحباً بك في نمط الطريقة المباشرة. يمكنك الآن طرح سؤالك مباشرة حول إدارة المشاريع البرمجية أو مشاريع التخرج، وسأقوم بمساعدتك."
                st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
            st.rerun()
            
        # Clear chat button
        st.markdown("### إعادة تعيين المحادثة")
        if st.button("مسح المحادثة", key="clear_chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.questionnaire_responses = {}
            st.session_state.questionnaire_step = 0
            st.session_state.welcome_shown = False
            st.session_state.chat_mode = None
            st.session_state.project_type = None
            st.rerun()
            
        # Topics based on current context
        st.markdown("---")
        
        # Combine topics from both areas for sidebar navigation
        st.markdown("### موضوعات شائعة")
        
        # Mix of PM and GP topics
        combined_topics = []
        for i in range(min(5, len(PROJECT_MANAGEMENT_ASPECTS))):
            combined_topics.append(("pm", PROJECT_MANAGEMENT_ASPECTS[i]))
        
        for i in range(min(5, len(GRADUATION_PROJECT_CATEGORIES))):
            combined_topics.append(("gp", GRADUATION_PROJECT_CATEGORIES[i]))
            
        # Display mixed topics
        for topic_type, topic in combined_topics:
            if st.button(topic, key=f"topic_{topic}", use_container_width=True):
                st.session_state.chat_mode = "direct"
                if topic_type == "pm":
                    query = f"أخبرني المزيد عن {topic}"
                else:
                    query = f"اقترح علي أفكار لمشاريع تخرج في مجال {topic}"
                
                st.session_state.project_type = topic_type
                st.session_state.messages.append({"role": "user", "content": query})
                st.rerun()
        
        # About section
        st.markdown("---")
        st.markdown("### حول التطبيق")
        st.markdown("""
        <div style='direction: rtl; text-align: right;'>
        هذا التطبيق مخصص لمساعدة المستخدمين في مجال المشاريع البرمجية ومشاريع التخرج.
        
        يعتمد على نموذج Google Gemini للذكاء الاصطناعي.
        </div>
        """, unsafe_allow_html=True)


# Main app flow
def main():
    # Always display sidebar
    display_sidebar()
    
    # Display appropriate interface based on chat mode
    if st.session_state.chat_mode is None:
        display_welcome()
        st.session_state.welcome_shown = True
    elif st.session_state.chat_mode == "guided":
        run_guided_questionnaire()
    elif st.session_state.chat_mode == "direct":
        run_direct_mode()


if __name__ == "__main__":
    main() 