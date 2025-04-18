import os
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st
from prompts import (
    SYSTEM_PROMPT, PM_GUIDED_GENERATION_TEMPLATE, GP_GUIDED_GENERATION_TEMPLATE,
    PM_DIRECT_MODE_TEMPLATE, GP_DIRECT_MODE_TEMPLATE
)

# Load environment variables
load_dotenv()

# Configure Gemini API
def setup_openai():
    """
    Setup the Gemini API with the API key from environment variables
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("Gemini API key not found. Please check your .env file.")
        st.stop()
    
    genai.configure(api_key=api_key)


def get_openai_response(prompt, system_prompt=SYSTEM_PROMPT, chat_history=None):
    """
    Get a response from the Gemini model
    
    Args:
        prompt (str): The prompt to send to the model
        system_prompt (str): The system prompt to use
        chat_history (list, optional): Chat history for contextual responses
    
    Returns:
        str: The model's response
    """
    try:
        # Create the generation config with safety settings
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Format the prompt with system prompt and chat history
        if chat_history:
            # Format the chat history as part of the prompt
            conversation_context = ""
            for msg in chat_history:
                role = "المستخدم" if msg["role"] == "user" else "المساعد"
                content = msg["content"]
                conversation_context += f"{role}: {content}\n\n"
            
            # Combine everything into a single prompt
            full_prompt = f"{system_prompt}\n\n--- سجل المحادثة السابق ---\n\n{conversation_context}--- السؤال الحالي ---\n\nالمستخدم: {prompt}\n\nالمساعد:"
        else:
            # If no history, just use the system prompt and current query
            full_prompt = f"{system_prompt}\n\nالمستخدم: {prompt}\n\nالمساعد:"
        
        # Generate the response with the full context
        response = model.generate_content(full_prompt)
        return response.text
    
    except Exception as e:
        st.error(f"Error getting response from Gemini: {str(e)}")
        return "عذراً، حدث خطأ في الاتصال بنموذج الذكاء الاصطناعي. يرجى المحاولة مرة أخرى."


        # Add the current user message
        messages.append({"role": "user", "content": prompt})
        
        # Call the OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4-turbo",  # Use appropriate model
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=0.95,
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        st.error(f"Error getting response from OpenAI: {str(e)}")
        return "عذراً، حدث خطأ في الاتصال بنموذج الذكاء الاصطناعي. يرجى المحاولة مرة أخرى."


def process_guided_questionnaire(responses, project_type="pm"):
    """
    Process the responses from the guided questionnaire and generate advice or project ideas
    
    Args:
        responses (dict): The user's responses to the questionnaire
        project_type (str): The type of project ("pm" for project management, "gp" for graduation project)
        
    Returns:
        str: Generated advice or project ideas
    """
    if project_type == "pm":
        # Format template for project management advice
        prompt = PM_GUIDED_GENERATION_TEMPLATE.format(
            general_advice="نصائح عامة مخصصة بناءً على إجابات المستخدم",
            suggested_tools="أدوات مقترحة بناءً على احتياجات المشروع",
            best_practices="أفضل الممارسات في إدارة المشاريع البرمجية",
            actionable_steps="خطوات عملية يمكن تطبيقها فوراً",
            additional_resources="موارد إضافية للمساعدة في إدارة المشروع"
        )
        
    else:  # Graduation projects
        # Format template for graduation project ideas
        prompt = GP_GUIDED_GENERATION_TEMPLATE.format(
            project_ideas="أفكار مشاريع مخصصة بناءً على مجال الدراسة والاهتمامات",
            suggested_technologies="تقنيات مقترحة لتنفيذ المشاريع",
            starting_steps="خطوات عملية لبدء تنفيذ المشروع",
            challenges_and_solutions="تحديات محتملة وحلولها",
            learning_resources="موارد تعليمية للمساعدة في تنفيذ المشروع"
        )
    
    # Add the user's responses to help the model generate personalized advice
    prompt += "\n\nإجابات المستخدم:\n"
    for key, value in responses.items():
        prompt += f"- {key}: {value}\n"
    
    return get_openai_response(prompt)


def process_direct_question(question, chat_history=None, project_type="pm"):
    """
    Process a direct question from the user
    
    Args:
        question (str): The user's question
        chat_history (list, optional): Chat history for contextual responses
        project_type (str): The type of project ("pm" for project management, "gp" for graduation project)
        
    Returns:
        str: The model's response
    """
    # If there's chat history, use it directly with the raw question
    if chat_history:
        return get_openai_response(question, chat_history=chat_history)
    
    # Otherwise, use the appropriate template
    if project_type == "pm":
        # Determine topic from question for project management
        prompt = PM_DIRECT_MODE_TEMPLATE.format(
            topic="الموضوع المطلوب",
            response="سيتم توليد إجابة مفصلة هنا"
        )
    else:
        # Determine topic from question for graduation projects
        prompt = GP_DIRECT_MODE_TEMPLATE.format(
            topic="الموضوع المطلوب",
            response="سيتم توليد أفكار وإرشادات هنا"
        )
    
    # Add user question for context
    prompt += f"\n\nسؤال المستخدم: {question}"
    
    return get_openai_response(prompt) 